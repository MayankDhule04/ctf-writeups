"""Journey final stage = Emojicode (healthy_food.journey).
Each char block: `N ➡ 🖍🆕 <var>` then `<var> ⬅❌ <fruit>` (XOR) per fruit, prints chr(<var>).
Flag = concat over blocks in order. Parse generically (var name differs each block)."""
import re

t = open('healthy_food.journey', encoding='utf-8').read().replace('\ufe0f', '').replace('\r', '')
ARROW, NEW, ASSIGN, X = '\u27a1', '\U0001f58d\U0001f195', '\u2b05', '\u274c'

consts = dict((m.group(2), int(m.group(1)))
              for m in re.finditer(r'(\d+)\s*' + ARROW + r'\s*([a-z]+)', t))
# remove any that are actually block vars (defined via 🖍🆕) -- base fruits only
block_def = re.compile(r'(\d+)\s*' + ARROW + r'\s*' + NEW + r'\s*([a-z]+)')
starts = [(m.start(), int(m.group(1)), m.group(2)) for m in block_def.finditer(t)]
print('fruit consts:', consts, '\nblocks:', len(starts))

flag = []
for i, (pos, n, var) in enumerate(starts):
    end = starts[i + 1][0] if i + 1 < len(starts) else len(t)
    seg = t[pos:end]
    val = n
    for fruit in re.findall(re.escape(var) + r'\s*' + ASSIGN + X + r'\s*([a-z]+)', seg):
        val ^= consts[fruit]
    flag.append(chr(val & 0xFF))

flag = ''.join(flag)
print('FLAG:', flag)
print('valid PINK{...}:', bool(re.fullmatch(r'PINK\{[^}]+\}', flag)))
open('journey_flag.txt', 'w').write(flag + '\n')
