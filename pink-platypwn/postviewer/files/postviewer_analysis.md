# Postviewer5-FF Challenge Analysis

## Challenge Overview
- URL: https://wl3zck2n-postviewer5-ff.instancer.2025.ctfcompetition.com/
- Type: Web XSS/CSRF challenge
- Goal: Extract flag from admin bot's IndexedDB
- Note: "Should be easier than the other version" - suggests simplified exploit

## Architecture

### File Storage
- Files stored in IndexedDB with two object stores: `files` and `info`
- File ID generated from SHA-256 hash or filename (if alphanumeric and longer)
- Files have properties: `id`, `file`, `cached`, `isPublic`

### File Rendering
- Files rendered in sandboxed iframe via `safe-frame.js`
- Uses Google's `scf.usercontent.goog` domain for isolation
- Hash-based subdomain: `calculateHash(product, salt, origin)`
- Salt generation:
  - Cached files: `salt = encoder.encode(id).buffer`
  - Non-cached: `salt = encoder.encode(getRandom(5)).buffer`
- `getRandom(5)` uses `Math.random()` - **PREDICTABLE!**

### Bot Behavior (bot.js)
1. Flips Firefox content isolation flag (`fission.webContentIsolationStrategy`)
2. Navigates to challenge URL
3. Posts flag via `postMessage`:
   ```javascript
   window.postMessage({
     type: "share",
     file: new File([flag], "flag.txt", { type: "text/plain" }),
     cached: true,
     isPublic: false
   }, "*");
   ```
4. Waits 1 second
5. Opens attacker-provided URL
6. Stays open for 5 minutes

### postMessage Handler (index.ejs)
```javascript
window.addEventListener("message", async (e) => {
  if (e.data.type === "share") {
    const fileInfo = await db.addFile({
      id: await generateFileId(e.data.file),
      file: e.data.file,
      cached: e.data.cached ?? false,
      isPublic: e.data.isPublic ?? false,
    });
    await appendFileInfo(fileInfo);
  }
});
```

## Key Vulnerabilities

### 1. Math.random() Predictability
- Non-cached files use `getRandom(5)` which relies on `Math.random()`
- `mathRandomInvocations` array stores all random values
- **CRITICAL**: This array is accessible from same-origin contexts!

### 2. Cached File Salt Predictability
- Cached files use file ID as salt
- File ID is SHA-256 hash of file content OR filename
- Flag file ID is predictable: `SHA256("flag content").slice(0,50)` or "flag.txt"

### 3. Same-Origin Access
- Bot visits attacker URL AFTER adding flag to IndexedDB
- If attacker can get same-origin execution, can access IndexedDB directly
- IndexedDB is same-origin accessible

### 4. postMessage Wildcard
- `window.postMessage(..., "*")` accepts messages from any origin
- But handler doesn't validate `e.origin` - accepts all messages!

## Attack Vectors

### Vector 1: Direct IndexedDB Access (Most Likely)
If we can get JavaScript execution on the challenge origin:
1. Bot adds flag to IndexedDB
2. Bot navigates to our URL on same origin
3. Our script reads IndexedDB directly
4. Exfiltrate flag

**Requirements**: 
- Need same-origin execution
- Possible via open redirect, XSS, or path traversal

### Vector 2: Math.random() State Recovery
1. Predict Math.random() sequence
2. Calculate salt for non-cached files
3. Reconstruct iframe URL
4. Access rendered content

**Problem**: Flag is cached, so uses file ID as salt, not Math.random()

### Vector 3: Hash Collision / ID Prediction
1. Calculate expected file ID for flag.txt
2. Since cached=true, salt = encoder.encode(fileId)
3. Calculate iframe URL hash
4. Access the scf.usercontent.goog subdomain

**Problem**: Need to know flag content to calculate hash, or filename must be predictable

### Vector 4: postMessage Injection
1. Send malicious postMessage to add our own file
2. Trick bot into revealing flag through file interaction

**Problem**: Bot doesn't interact with files after adding flag

## Most Promising Approach

### Exploit Strategy: Same-Origin IndexedDB Access

The bot:
1. Adds flag to IndexedDB at challenge origin
2. Then navigates to attacker URL

If the attacker URL is on the SAME ORIGIN (challenge domain), we can:
- Access IndexedDB directly
- Read all files including the flag
- Exfiltrate to our server

**Key Question**: Can we host a page on the challenge origin?

Possibilities:
- Open redirect vulnerability
- Path traversal to serve attacker HTML
- XSS in any parameter
- JSONP or callback parameter

Let me check the Express routes more carefully...

### Checking app.js Routes:
- `GET /` - renders index.ejs
- `GET /bot` - renders bot.ejs  
- `POST /bot` - accepts URL and triggers bot visit
- No obvious open redirect or file serving

### Alternative: Cross-Origin Frame Access
If we can't get same-origin, we need to:
1. Open challenge URL in iframe from our domain
2. Use postMessage to communicate
3. Exploit the wildcard postMessage handler

But IndexedDB is same-origin only, so this won't work directly.

## Next Steps
1. Test the live site for open redirects or XSS
2. Check if any parameter reflects in response
3. Look for CORS misconfigurations
4. Test if we can inject HTML/JS through any input
5. Check for path traversal in static file serving
