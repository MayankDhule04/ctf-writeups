"""Misc solvers — graph traversal, automata, Bacon cipher, OSINT, coordinates."""

import json
import re
from collections import defaultdict, deque
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from .flag_detector import FlagDetector
from .utils import extract_printable_strings

_detector = FlagDetector()

# ---------------------------------------------------------------------------
# Graph traversal
# ---------------------------------------------------------------------------

def graph_walk(graph_data: Dict, flag_regex: str = None,
               max_depth: int = 50) -> List[Dict]:
    """Walk all paths through a graph and look for flag patterns in edge labels.

    Args:
        graph_data: Dict with 'nodes' and 'edges' keys (or adjacency dict)
        flag_regex: Optional additional flag regex
        max_depth: Maximum path length to explore

    Returns:
        List of {path, label_string, flags}
    """
    detector = FlagDetector(extra_regex=flag_regex) if flag_regex else _detector
    results = []

    # Normalize graph
    adj: Dict[str, List[Tuple[str, str]]] = defaultdict(list)  # node -> [(target, label)]

    if "edges" in graph_data:
        for edge in graph_data["edges"]:
            src = str(edge.get("source", edge.get("from", edge.get("src", ""))))
            tgt = str(edge.get("target", edge.get("to", edge.get("dst", ""))))
            label = str(edge.get("label", edge.get("weight", "")))
            adj[src].append((tgt, label))
    elif isinstance(graph_data, dict):
        for src, targets in graph_data.items():
            if isinstance(targets, dict):
                for tgt, label in targets.items():
                    adj[str(src)].append((str(tgt), str(label)))
            elif isinstance(targets, list):
                for tgt in targets:
                    if isinstance(tgt, (list, tuple)) and len(tgt) == 2:
                        adj[str(src)].append((str(tgt[0]), str(tgt[1])))
                    else:
                        adj[str(src)].append((str(tgt), ""))

    # BFS all paths collecting labels
    nodes = set(adj.keys())
    for src in adj:
        for tgt, _ in adj[src]:
            nodes.add(tgt)

    for start in nodes:
        queue = deque([(start, [], [])])
        while queue:
            node, path, labels = queue.popleft()
            if len(path) > max_depth:
                continue
            path = path + [node]
            # Decode current label string
            label_str = "".join(labels)
            flags = detector.extract_all(label_str)
            if flags:
                results.append({"path": path, "label_string": label_str, "flags": flags})

            for tgt, label in adj.get(node, []):
                if tgt not in path:  # avoid cycles
                    queue.append((tgt, path, labels + [label]))

    return results


def graph_edge_labels_decode(graph_data: Dict,
                              decode_fn: Optional[Callable] = None) -> List[str]:
    """Collect all edge labels and try to decode them.

    Args:
        graph_data: Graph in standard format
        decode_fn: Optional function(label) -> str to apply to each label

    Returns:
        List of decoded strings
    """
    labels = []
    if "edges" in graph_data:
        for edge in graph_data["edges"]:
            label = str(edge.get("label", edge.get("weight", "")))
            if label:
                labels.append(label)

    if decode_fn:
        return [decode_fn(l) for l in labels]
    return labels


# ---------------------------------------------------------------------------
# Finite automaton
# ---------------------------------------------------------------------------

def automaton_simulate(states: List, transitions: Dict,
                        inputs: List[str], accepting: List) -> List[str]:
    """Simulate a finite automaton and find all accepting input strings.

    Args:
        states: List of state names
        transitions: Dict {state: {symbol: next_state}}
        inputs: List of input symbols to try
        accepting: List of accepting states

    Returns:
        List of input sequences that lead to accepting states
    """
    results = []
    start = states[0] if states else None
    if not start:
        return results

    def dfs(state, path, depth=0):
        if depth > 100:
            return
        if state in accepting:
            flag_candidate = "".join(path)
            if _detector.is_flag(flag_candidate) or len(path) > 3:
                results.append(flag_candidate)
        for symbol in inputs:
            next_state = transitions.get(state, {}).get(symbol)
            if next_state and next_state in states:
                dfs(next_state, path + [symbol], depth + 1)

    dfs(start, [])
    return results


# ---------------------------------------------------------------------------
# Classical ciphers — Bacon, binary, etc.
# ---------------------------------------------------------------------------

_BACON_STD = {
    "AAAAA": "A", "AAAAB": "B", "AAABA": "C", "AAABB": "D", "AABAA": "E",
    "AABAB": "F", "AABBA": "G", "AABBB": "H", "ABAAA": "I", "ABAAB": "J",
    "ABABA": "K", "ABABB": "L", "ABBAA": "M", "ABBAB": "N", "ABBBA": "O",
    "ABBBB": "P", "BAAAA": "Q", "BAAAB": "R", "BAABA": "S", "BAABB": "T",
    "BABAA": "U", "BABAB": "V", "BABBA": "W", "BABBB": "X", "BBAAA": "Y",
    "BBAAB": "Z",
}


def bacon_decode(text: str, a_char: str = "A", b_char: str = "B") -> str:
    """Decode Bacon cipher.

    Args:
        text: Ciphertext (can use any two distinct characters as A/B)
        a_char: Character to treat as 'A'
        b_char: Character to treat as 'B'

    Returns:
        Decoded plaintext
    """
    normalized = ""
    for c in text.upper():
        if c == a_char.upper():
            normalized += "A"
        elif c == b_char.upper():
            normalized += "B"
        elif c in ("A", "B"):
            normalized += c
        # skip other characters (spaces, etc.)

    result = []
    for i in range(0, len(normalized) - 4, 5):
        group = normalized[i:i + 5]
        result.append(_BACON_STD.get(group, "?"))
    return "".join(result)


def binary_to_text(binary: str, delimiter: str = " ") -> str:
    """Convert binary string to ASCII text.

    Args:
        binary: Binary string like '01001000 01100101'
        delimiter: Separator between bytes (space by default)

    Returns:
        Decoded ASCII string
    """
    if delimiter:
        groups = binary.strip().split(delimiter)
    else:
        groups = [binary[i:i + 8] for i in range(0, len(binary), 8)]

    result = []
    for g in groups:
        g = g.strip()
        if len(g) == 8 and all(c in "01" for c in g):
            result.append(chr(int(g, 2)))
    return "".join(result)


# ---------------------------------------------------------------------------
# Coordinate extraction
# ---------------------------------------------------------------------------

def extract_coordinates(text: str) -> List[Dict]:
    """Extract GPS, Minecraft-style, or grid coordinates from text.

    Returns list of {type, raw, parsed}
    """
    results = []

    # GPS decimal: 12.345, 67.890
    gps_dec = re.finditer(
        r"(-?\d{1,3}\.\d{4,})[,\s]+(-?\d{1,3}\.\d{4,})", text
    )
    for m in gps_dec:
        results.append({"type": "gps_decimal", "raw": m.group(0),
                         "parsed": {"lat": float(m.group(1)), "lon": float(m.group(2))}})

    # Minecraft/game coords: X=1234 Y=56 Z=789 or (1234, 56, 789)
    mc = re.finditer(r"[Xx][\s=:]*(-?\d+)[,\s]+[Yy][\s=:]*(-?\d+)[,\s]+[Zz][\s=:]*(-?\d+)", text)
    for m in mc:
        results.append({"type": "minecraft", "raw": m.group(0),
                         "parsed": {"x": int(m.group(1)), "y": int(m.group(2)), "z": int(m.group(3))}})

    # Tuples: (1234, -2040)
    tuples = re.finditer(r"\((-?\d+),\s*(-?\d+)\)", text)
    for m in tuples:
        results.append({"type": "2d_tuple", "raw": m.group(0),
                         "parsed": {"x": int(m.group(1)), "y": int(m.group(2))}})

    return results


# ---------------------------------------------------------------------------
# Flag assembly
# ---------------------------------------------------------------------------

def flag_from_parts(parts: List[str], separators: List[str] = None,
                    flag_regex: str = None) -> List[str]:
    """Try combining flag parts with different separators and orderings.

    Returns list of strings that look like flags.
    """
    from itertools import permutations
    detector = FlagDetector(extra_regex=flag_regex) if flag_regex else _detector
    if separators is None:
        separators = ["", "_", "-", " ", "."]

    candidates = []
    for perm in permutations(parts):
        for sep in separators:
            candidate = sep.join(perm)
            if detector.is_flag(candidate):
                candidates.append(candidate)
            # Try with CHAKRA{ } wrapper
            wrapped = f"CHAKRA{{{candidate}}}"
            if detector.is_flag(wrapped):
                candidates.append(wrapped)

    return list(dict.fromkeys(candidates))


# ---------------------------------------------------------------------------
# OSINT helpers
# ---------------------------------------------------------------------------

def osint_username_search(username: str, platforms: List[str] = None) -> Dict:
    """Check if a username exists on common platforms.

    Args:
        username: Username to search
        platforms: List of platform URLs (uses built-in list if None)

    Returns:
        Dict mapping platform -> {found, url, status}
    """
    try:
        import requests
    except ImportError:
        return {"error": "requests not installed"}

    if platforms is None:
        platforms = {
            "github":    f"https://github.com/{username}",
            "twitter":   f"https://twitter.com/{username}",
            "instagram": f"https://instagram.com/{username}",
            "reddit":    f"https://reddit.com/user/{username}",
            "pastebin":  f"https://pastebin.com/u/{username}",
        }
    else:
        platforms = {p: p.replace("{}", username) for p in platforms}

    results = {}
    for name, url in platforms.items():
        try:
            r = requests.get(url, timeout=8,
                             headers={"User-Agent": "Mozilla/5.0 ctf-tool"})
            results[name] = {
                "found":  r.status_code == 200,
                "url":    url,
                "status": r.status_code,
            }
        except Exception as e:
            results[name] = {"found": False, "url": url, "error": str(e)}

    return results


# ---------------------------------------------------------------------------
# Brainfuck interpreter
# ---------------------------------------------------------------------------

def brainfuck_run(code: str, input_data: str = "",
                  max_steps: int = 100000) -> str:
    """Execute Brainfuck code and return output."""
    tape = [0] * 30000
    ptr = 0
    code = [c for c in code if c in "+-<>.,[]"]
    ip = 0
    output = []
    inp = list(input_data)
    steps = 0

    # Build bracket map
    bracket_map = {}
    stack = []
    for i, c in enumerate(code):
        if c == "[":
            stack.append(i)
        elif c == "]":
            if stack:
                j = stack.pop()
                bracket_map[j] = i
                bracket_map[i] = j

    while ip < len(code) and steps < max_steps:
        cmd = code[ip]
        if cmd == ">":
            ptr = (ptr + 1) % 30000
        elif cmd == "<":
            ptr = (ptr - 1) % 30000
        elif cmd == "+":
            tape[ptr] = (tape[ptr] + 1) % 256
        elif cmd == "-":
            tape[ptr] = (tape[ptr] - 1) % 256
        elif cmd == ".":
            output.append(chr(tape[ptr]))
        elif cmd == ",":
            tape[ptr] = ord(inp.pop(0)) if inp else 0
        elif cmd == "[" and tape[ptr] == 0:
            ip = bracket_map.get(ip, ip)
        elif cmd == "]" and tape[ptr] != 0:
            ip = bracket_map.get(ip, ip)
        ip += 1
        steps += 1

    return "".join(output)
