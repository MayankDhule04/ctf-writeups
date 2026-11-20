#!/usr/bin/env python3
"""
OSINT Challenge - Pizza Police
Find the street in New Haven, CT with police and pizza
"""

print("="*70)
print("OSINT - PIZZA POLICE CHALLENGE")
print("="*70)

print("\n[Analysis]")
print("  Clue 1: 'seagulls' with 'sirens blaring' = POLICE CARS")
print("  Clue 2: 'smell like pizza' = Near pizza restaurants")
print("  Clue 3: 'being watched' = Police station/heavy presence")
print("  Hint: Connecticut city known for pizza = NEW HAVEN, CT")

print("\n[New Haven Pizza Context]")
print("  New Haven is famous for 'apizza' (New Haven-style pizza)")
print("  Famous pizza places:")
print("    - Frank Pepe Pizzeria Napoletana (Wooster Street)")
print("    - Sally's Apizza (Wooster Street)")
print("    - Modern Apizza (State Street)")
print("    - BAR (Crown Street)")

print("\n[Key Streets in New Haven with Pizza]")
print("  1. Wooster Street - Historic pizza district")
print("  2. State Street - Modern Apizza location")
print("  3. Crown Street - BAR location")

print("\n[Police Stations in New Haven]")
print("  - New Haven Police Department HQ: 1 Union Avenue")
print("  - District stations throughout city")

print("\n[Most Likely Answer]")
print("  Wooster Street is the most famous pizza street in New Haven")
print("  It's in the Wooster Square neighborhood")
print("  Known for Frank Pepe's and Sally's Apizza")
print("  Heavy foot traffic and police presence due to popularity")

print("\n[Flag Format: CIT{Street_Name_City_Name_State}]")
print("  Example: CIT{Main_Street_Los_Angeles_CA}")

print("\n[Possible Flags]")
flags = [
    "CIT{Wooster_Street_New_Haven_CT}",
    "CIT{State_Street_New_Haven_CT}",
    "CIT{Crown_Street_New_Haven_CT}",
    "CIT{Union_Avenue_New_Haven_CT}",
]

for flag in flags:
    print(f"  {flag}")

print("\n[Most Likely]")
print("  FLAG: CIT{Wooster_Street_New_Haven_CT}")
print("  Reason: Most famous pizza street in New Haven")

print("\n" + "="*70)
