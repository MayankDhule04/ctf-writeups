#!/usr/bin/env python3
"""
CIT Challenge Solver
New Haven University CTF Event

Challenge 1: SHA1 hash - 33746b3052f748a9d41f030d2be4f196d02453cb
Challenge 2: Brainfuck code
"""

import hashlib

print("=" * 70)
print("CIT CHALLENGE SOLVER")
print("=" * 70)

# Challenge 1: SHA1 Hash
sha1_hash = "33746b3052f748a9d41f030d2be4f196d02453cb"
print(f"\n🔍 Challenge 1: SHA1 Hash")
print(f"   Hash: {sha1_hash}")
print(f"   Trying common strings...")

# Try common CTF strings
common_strings = [
    "flag", "password", "admin", "root", "secret", "key",
    "cit", "CIT", "newhaven", "university", "ctf", "CTF",
    "challenge", "solve", "answer", "solution"
]

for s in common_strings:
    if hashlib.sha1(s.encode()).hexdigest() == sha1_hash:
        print(f"   ✅ FOUND: '{s}'")
        break
else:
    print(f"   Trying with CIT{{}} format...")
    for s in common_strings:
        test = f"CIT{{{s}}}"
        if hashlib.sha1(test.encode()).hexdigest() == sha1_hash:
            print(f"   ✅ FOUND: '{test}'")
            break

# Challenge 2: Brainfuck Code
brainfuck_code = "++++++++++[>+>+++>+++++++>++++++++++<<<<-]>>>---.++++++.+++++++++++.>+++++++++++++++++++++++.<+++.+++++++++++++++++.<++++++++++++++++++++++++++++++++++.>>-------.<---------.++++++++++.+++++.---------------.>.<+++++++++.<-------------.>---------.>+++.<<---.>>-----.------.<+++++.-----.>---.<<------------.>.>+++++++++++.<+++++++++.<+++++++++++++.>>-.<---------.>-------.<<+++++++++++++++.>>++.-------.++++++++++++++.<<.>++++++++.<-------------.>>++++++++."

print(f"\n🧠 Challenge 2: Brainfuck Code")
print(f"   Code length: {len(brainfuck_code)} characters")
print(f"   Executing brainfuck...")

# Brainfuck interpreter
def execute_brainfuck(code):
    tape = [0] * 30000
    pointer = 0
    code_pointer = 0
    output = []
    
    bracket_map = {}
    bracket_stack = []
    for i, c in enumerate(code):
        if c == '[':
            bracket_stack.append(i)
        elif c == ']':
            start = bracket_stack.pop()
            bracket_map[start] = i
            bracket_map[i] = start
    
    while code_pointer < len(code):
        cmd = code[code_pointer]
        
        if cmd == '>':
            pointer += 1
        elif cmd == '<':
            pointer -= 1
        elif cmd == '+':
            tape[pointer] = (tape[pointer] + 1) % 256
        elif cmd == '-':
            tape[pointer] = (tape[pointer] - 1) % 256
        elif cmd == '.':
            output.append(chr(tape[pointer]))
        elif cmd == ',':
            tape[pointer] = ord(input()[0])
        elif cmd == '[':
            if tape[pointer] == 0:
                code_pointer = bracket_map[code_pointer]
        elif cmd == ']':
            if tape[pointer] != 0:
                code_pointer = bracket_map[code_pointer]
        
        code_pointer += 1
    
    return ''.join(output)

result = execute_brainfuck(brainfuck_code)
print(f"   Output: {result}")

# Check if it's the flag
if result.startswith("CIT{") and result.endswith("}"):
    print(f"   ✅ FLAG FOUND: {result}")
else:
    print(f"   Wrapping in CIT{{}}: CIT{{{result}}}")

print(f"\n" + "=" * 70)
print(f"SOLUTIONS:")
print(f"=" * 70)
print(f"\n🏁 Brainfuck Output: {result}")
if result.startswith("CIT{"):
    print(f"🏁 Final Flag: {result}")
else:
    print(f"🏁 Possible Flag: CIT{{{result}}}")
