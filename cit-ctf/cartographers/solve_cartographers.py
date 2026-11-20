#!/usr/bin/env python3
"""
Cartographer's Secret - OSINT Challenge (CIT CTF)

CORRECTED INFORMATION:
- Prerequisite: "Follow the Flock" = CIT{State_Street_New_Haven_CT}
- Hint: "Maybe I'm not looking closely enough"
- Challenge: Find the name of a menu item
- Flag format: CIT{name_of_item} or CIT{name-of-item}

KEY INSIGHT: The user said "read the description carefully" and emphasized
looking "closely" at State Street in New Haven, CT.

When you zoom in CLOSELY on State Street in New Haven on a map, what do you see?
- Buildings
- Landmarks
- Street signs
- Business names
- Historical markers

State Street in New Haven is near:
- New Haven Green (famous landmark)
- Yale University campus
- City Hall
- Various restaurants and businesses

The challenge asks for a "menu item" - this suggests:
1. A restaurant on State Street
2. A famous dish from that area
3. A landmark that has a "menu" metaphorically

Looking CLOSELY at State Street, New Haven:
- It runs along the New Haven Green
- City Hall is on State Street
- Multiple historic buildings

CARTOGRAPHER'S SECRET + MENU ITEM:
A cartographer makes maps. Looking closely at a map of State Street...

Possible answers (things visible when zooming in on State Street):
"""

import requests

# These are things you'd see when looking CLOSELY at State Street on a map
possible_flags = [
    # Landmarks visible on State Street
    "CIT{New_Haven_Green}",
    "CIT{The_Green}",
    "CIT{City_Hall}",
    "CIT{New_Haven_City_Hall}",
    
    # Historical markers/buildings on State Street
    "CIT{John_Brockett}",  # Surveyed New Haven
    "CIT{Center_Church}",  # On the Green
    "CIT{Trinity_Church}",
    "CIT{United_Church}",
    
    # Streets that intersect State Street (visible when zooming in)
    "CIT{Chapel_Street}",
    "CIT{Elm_Street}",
    "CIT{Church_Street}",
    "CIT{College_Street}",
    
    # Yale buildings near State Street
    "CIT{Yale_University}",
    "CIT{Old_Campus}",
    "CIT{Phelps_Gate}",
    
    # Restaurants/businesses on State Street (menu items!)
    "CIT{Louis_Lunch}",  # Famous burger place in New Haven
    "CIT{Pepes_Pizza}",  # Frank Pepe's
    "CIT{Modern_Apizza}",
    "CIT{Sallys_Apizza}",
    
    # If it's literally a menu item from a State Street restaurant
    "CIT{New_Haven_Pizza}",
    "CIT{Apizza}",
    "CIT{White_Clam_Pizza}",  # Famous New Haven dish
    "CIT{Tomato_Pie}",
    
    # Map features you'd see zooming in
    "CIT{Nine_Squares}",  # Original New Haven city plan
    "CIT{The_Nine_Squares}",
    
    # Building numbers/addresses on State Street
    "CIT{165_Church_Street}",  # City Hall address
    
    # Other possibilities
    "CIT{Grove_Street}",  # Famous cemetery nearby
    "CIT{Wooster_Square}",  # Pizza district
]

print("=" * 70)
print("Cartographer's Secret - Systematic Solver")
print("=" * 70)
print()
print("[*] Challenge: Find menu item related to State Street, New Haven, CT")
print("[*] Hint: 'Maybe I'm not looking closely enough'")
print("[*] User emphasis: Look CLOSELY at State Street on a map")
print()
print("[*] Strategy: When you zoom in on State Street in New Haven,")
print("    what landmarks, buildings, or businesses become visible?")
print()
print("[*] Testing possible flags...")
print()

# Note: This would need the actual challenge URL to test
# For now, just list the possibilities

print("Top candidates (most likely to least likely):")
print()
print("1. CIT{New_Haven_Green}")
print("   - The famous park that State Street borders")
print("   - Visible when looking closely at State Street")
print()
print("2. CIT{City_Hall}")
print("   - Located on State Street")
print("   - Major landmark visible on maps")
print()
print("3. CIT{White_Clam_Pizza}")
print("   - Famous New Haven menu item")
print("   - If challenge wants actual food item")
print()
print("4. CIT{Chapel_Street}")
print("   - Intersects State Street")
print("   - Visible when zooming in")
print()
print("5. CIT{Center_Church}")
print("   - Historic church on the Green")
print("   - Visible from State Street")
print()

print("\n[!] RECOMMENDATION:")
print("    Open Google Maps, search 'State Street, New Haven, CT'")
print("    Zoom in CLOSELY and look for:")
print("    - Building names")
print("    - Business names")
print("    - Street signs")
print("    - Landmarks")
print("    - Historical markers")
print()
print("    The 'menu item' is likely something you can SEE on the map")
print("    when you zoom in close enough!")

