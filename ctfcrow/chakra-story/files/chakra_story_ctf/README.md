# The Keeper's Four Pages

For one hundred years, the mountain temple had a single keeper. On the night
the last keeper disappeared, four pages were found in the lantern room.

Each page contains part of a secret message hidden inside its story. Read the
pages in order, follow the small hint hidden in each one, decode the marked
inscription, and join the four pieces.

The flag format is:

```text
CHAKRA{...}
```

The three hiding methods are:

- **Base64** — the temple's "square script"
- **ROT13** — the alphabet turned thirteen steps
- **Morse code** — the language of dots and dashes

The joined result is not the final flag yet. Reverse the complete joined
string once. It will then be written in simple leetspeak:

```text
4 = A    0 = o    7 = T    3 = E    5 = S
```

Run the optional checker with:

```bash
python3 tools/verify.py 'YOUR_FLAG'
```

If you get stuck, use the progressive hints in `hints/optional_hints.txt`.

There is no network access or third-party dependency.