import re

# Verified word-by-word reconstruction (gap=14.6 -> new word, gap=3.0 -> same word)
lines = [
 "THOSE WHO DO NOT",
 "FOLLOW THE PRIN",
 "CIPLES OF VULCA",
 "N LOGIC WILL FAI",
 "L VTOSH KATUR NI",
 "RAK DO NOT PITY",
 "THOSE WHO DO NOT",
 "FOLLOW LOGIC HE",
 "LP THEM SEE REAS",
 "ON TURN THE VULC",
 "AN INTO ENGLISH",
 "AND WRAP IT WITH",
 "UNDERSCORES TO",
 "SEE REASON",
]
# Concatenate raw letters per line (strip spaces), then re-wrap using true word boundaries
raw = ''.join(l.replace(' ', '') for l in lines)
print("raw letters:", raw)

# True word boundaries come from gaps within each line; reconstruct full word list
words_per_line = [l.split(' ') for l in lines]
# merge: last word of a line continues into first word of next line (no space at line wrap)
all_words = []
carry = ''
for lw in words_per_line:
    lw = lw[:]
    lw[0] = carry + lw[0]
    carry = lw[-1]
    all_words.extend(lw[:-1])
all_words.append(carry)

sentence = ' '.join(all_words)
print()
print("Reconstructed:", sentence)

def mk(s):
    s = re.sub(r"[^A-Za-z ]", '', s).strip()
    s = re.sub(r'\s+', '_', s).lower()
    return 'spooky{' + s + '}'

print()
print(mk(sentence))
