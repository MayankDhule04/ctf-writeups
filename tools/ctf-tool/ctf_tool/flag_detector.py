"""Flag detection engine — scans text/bytes for CTF flag patterns."""

import re
import json
import os
from typing import List, Dict, Optional

_DEFAULT_PATTERNS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "flag_formats.json")

_BUILTIN_PATTERNS = [
    {"name": "generic_braces",  "regex": r"[A-Za-z0-9_]{2,20}\{[^}]{3,80}\}", "priority": 1},
    {"name": "CHAKRA",          "regex": r"CHAKRA\{[^}]+\}",                   "priority": 2},
    {"name": "flag",            "regex": r"flag\{[^}]+\}",                     "priority": 2},
    {"name": "CTF",             "regex": r"CTF\{[^}]+\}",                      "priority": 2},
    {"name": "SpaceCTF",        "regex": r"SpaceCTF\{[^}]+\}",                 "priority": 2},
    {"name": "KAALRAJ",         "regex": r"KAALRAJ\{[^}]+\}",                  "priority": 2},
    {"name": "picoCTF",         "regex": r"picoCTF\{[^}]+\}",                  "priority": 2},
    {"name": "HTB",             "regex": r"HTB\{[^}]+\}",                      "priority": 2},
    {"name": "THM",             "regex": r"THM\{[^}]+\}",                      "priority": 2},
]


class FlagDetector:
    """Scan text or binary data for CTF flag patterns."""

    def __init__(self, patterns_file: Optional[str] = None, extra_regex: Optional[str] = None):
        """
        Args:
            patterns_file: Path to flag_formats.json (uses built-in if not found)
            extra_regex: Additional regex pattern to search for
        """
        self.patterns = list(_BUILTIN_PATTERNS)

        # Try loading from file
        pf = patterns_file or _DEFAULT_PATTERNS_FILE
        if pf and os.path.exists(pf):
            try:
                with open(pf, encoding="utf-8") as f:
                    data = json.load(f)
                self.patterns = data.get("patterns", self.patterns)
            except Exception:
                pass

        if extra_regex:
            self.patterns.insert(0, {"name": "custom", "regex": extra_regex, "priority": 0})

        # Compile regexes
        self._compiled = []
        for p in self.patterns:
            try:
                self._compiled.append((p["name"], re.compile(p["regex"]), p.get("priority", 5)))
            except re.error:
                pass

    def scan_text(self, text: str) -> List[Dict]:
        """Scan text for flag patterns.

        Returns:
            List of dicts: {name, value, start, end, priority}
        """
        found = []
        seen = set()
        for name, pattern, priority in self._compiled:
            for m in pattern.finditer(text):
                val = m.group(0)
                if val not in seen:
                    seen.add(val)
                    found.append({
                        "name":     name,
                        "value":    val,
                        "start":    m.start(),
                        "end":      m.end(),
                        "priority": priority,
                    })
        found.sort(key=lambda x: x["priority"])
        return found

    def scan_bytes(self, data: bytes) -> List[Dict]:
        """Scan binary data for flag patterns (decodes as UTF-8 with errors replaced)."""
        text = data.decode("utf-8", errors="replace")
        return self.scan_text(text)

    def is_flag(self, s: str) -> bool:
        """Return True if s matches any known flag pattern."""
        return bool(self.scan_text(s))

    def extract_all(self, text: str) -> List[str]:
        """Return unique flag strings found in text."""
        return list(dict.fromkeys(r["value"] for r in self.scan_text(text)))


# Module-level default detector
_detector = FlagDetector()


def scan_text(text: str, extra_regex: Optional[str] = None) -> List[Dict]:
    """Convenience: scan text with default detector."""
    d = FlagDetector(extra_regex=extra_regex) if extra_regex else _detector
    return d.scan_text(text)


def scan_file(path: str, extra_regex: Optional[str] = None) -> List[Dict]:
    """Read a file and scan for flags."""
    try:
        with open(path, "rb") as f:
            data = f.read()
        d = FlagDetector(extra_regex=extra_regex) if extra_regex else _detector
        return d.scan_bytes(data)
    except Exception as e:
        return [{"error": str(e)}]
