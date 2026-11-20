import re

raw = "THOSE WHO DO NOTFOLLOW THE PRINCIPLES OF VULCAN LOGIC WILL FAIL VTOSH KATUR NIRAK DO NOT PITYTHOSE WHO DO NOTFOLLOW LOGIC HELP THEM SEE REASON TURN THE VULCAN INTO ENGLISHAND WRAP IT WITHUNDERSCORES TOSEE REASON"

# Manually fix known glued-together boundaries based on obvious English dictionary words
fixes = [
    ("NOTFOLLOW", "NOT FOLLOW"),
    ("PITYTHOSE", "PITY THOSE"),
    ("ENGLISHAND", "ENGLISH AND"),
    ("WITHUNDERSCORES", "WITH UNDERSCORES"),
    ("TOSEE", "TO SEE"),
]
fixed = raw
for a, b in fixes:
    fixed = fixed.replace(a, b)

print(fixed)

def mk(s):
    s = re.sub(r"[^A-Za-z ]", '', s).strip()
    s = re.sub(r'\s+', '_', s).lower()
    return 'spooky{' + s + '}'

print()
print(mk(fixed))
