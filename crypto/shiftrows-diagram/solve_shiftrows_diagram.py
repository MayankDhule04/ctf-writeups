#!/usr/bin/env python3
"""
Try all Caesar shifts and print ALL results
Maybe we'll spot something readable
"""

cipher = "TYWCDOY7GFRMHYDILOSBOXO2KPGYWMGSFYPKVASGHRNILBAPVIVAVHYFNLAFFTPODRNKZYZASB7YWCDOYBYXHTHZMVYTLBRNFIWNPODRNKZYRDSGIGSGHLSBCVHLVFAFF7LPOCSBAP7BNENVYQEUHY"

print("[*] ALL CAESAR SHIFTS")
print("="*70)

for shift in range(26):
    decoded = ''
    for char in cipher:
        if char.isalpha():
            decoded += chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
        else:
            decoded += char
    
    print(f"\nShift {shift:2d}: {decoded}")

print("\n" + "="*70)
