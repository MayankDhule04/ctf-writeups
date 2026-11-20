# Stolen Schematics - Current Status & Action Plan

## 🚨 CRITICAL DISCOVERY

**THE ORIGINAL APPROACH IS WRONG!**

- `/etc/flag.txt` **DOES NOT EXIST** in the running container
- sync-loop.sh **DOES NOT PROCESS** our config files
- Writing to `/opt/mc/config/sync-request.conf` produces **NO RESPONSE**
- But **2 teams have solved this** - so solution exists!

## 🎯 New Hypothesis: "Stolen Schematics" = Steal the Source

**Challenge**: The challenge name is the hint - we need to STEAL the SCHEMATICS (source code)  
**Target**: Flag might be EMBEDDED in the Docker registry layers themselves  
**Instance**: `ssh player@instance.ctf.tdho.st -p <PORT>` (password: `reyalp`)  
**Last Known Port**: 32902 (likely expired - get new one from CTF platform)

### ✅ What We Know

1. **Docker Registry is Accessible**
   - Internal registry at `172.27.0.1:5000`
   - Repository: `images/stolen-schematics-watcher`
   - Contains multiple tags: v1, latest, team131-fix
   - Extracted watcher.sh code from old layers

2. **What DOESN'T Work**
   - `/etc/flag.txt` does NOT exist in container
   - sync-loop.sh does NOT process config files we write
   - No watcher responses to any config format
   - File timestamps never change - watcher isn't active

3. **Key Clue: 2 Teams Solved It**
   - Solution exists but we haven't found it
   - Challenge name: "STOLEN Schematics" suggests STEALING something
   - Not USING the schematics to exploit - STEALING them

### 💡 New Theory: Flag in Registry

The flag might be:
1. **Embedded in a Docker layer** as a file or environment variable
2. **Hidden in build-time secrets** that weren't cleaned up
3. **In a different image version** we haven't checked
4. **In registry metadata** (image labels, annotations)

## 🔍 CRITICAL FINDING

**The Docker registry tags we were looking for DON'T EXIST!**
- v1: HTTP 404
- latest: HTTP 404  
- team131-fix: HTTP 404

This means either:
1. We have the wrong repository name
2. We have the wrong registry URL
3. The registry approach is a red herring
4. The tags changed/were removed

## 🚀 Next Steps (REVISED - in order of priority)

## 🚀 Next Steps (REVISED - in order of priority)

### PRIORITY 1: Discover What's Actually in the Registry

```bash
# Copy-paste from STOLEN_DISCOVER_REGISTRY.txt
curl -s http://172.27.0.1:5000/v2/_catalog
curl -s http://172.27.0.1:5000/v2/images/stolen-schematics-watcher/tags/list
```

### PRIORITY 2: Complete System Reconnaissance

Since our assumptions were wrong, we need fresh reconnaissance:

```bash
# Copy-paste from STOLEN_COMPLETE_RECON.txt
# This will systematically check EVERYTHING
```

### PRIORITY 3: Try All Alternative Approaches

```bash
# Copy-paste from STOLEN_ALTERNATIVE_APPROACHES.txt
# Includes: symlinks, race conditions, proc filesystem, etc.
```

### PRIORITY 4: Focus on "2 Teams Solved It"

Since 2 teams solved it, the solution is likely:
1. **Simple but non-obvious** - something we overlooked
2. **Related to the challenge name** - "STOLEN Schematics" = stealing source code
3. **Time-sensitive** - race condition or timing-based
4. **Different location** - flag isn't where we think

### PRIORITY 5: Ask for Hints

If all reconnaissance fails, consider:
- Check CTF Discord/forums for hints from other players
- Ask organizers if the challenge is working correctly
- See if there's a write-up from the 2 teams who solved it

## 📋 Quick Action Commands

**If you're in SSH right now, run these:**

```bash
# 1. Quick flag search
find / -type f -readable 2>/dev/null | xargs grep -l "TDHT{" 2>/dev/null | head -20

# 2. Check environment
env | grep -i flag
cat /proc/16/environ 2>/dev/null | tr '\0' '\n' | grep -i flag

# 3. Discover registry
curl -s http://172.27.0.1:5000/v2/_catalog

# 4. Check alternative flag locations
cat /flag.txt 2>/dev/null
cat /flag 2>/dev/null
cat ~/flag.txt 2>/dev/null
cat /opt/flag.txt 2>/dev/null
cat /var/flag.txt 2>/dev/null
```

## 🎯 Most Likely Solutions (Based on 2 Teams Solving)

1. **Flag is in plain sight** - in a readable file we haven't checked
2. **Flag is in environment** - $FLAG variable or similar
3. **Registry is accessible differently** - different URL/repo name
4. **Timing-based exploit** - watcher DOES work but needs specific timing
5. **Process memory** - flag is in sync-loop.sh process memory
