# Stolen Schematics - Attack Plan

## Initial Recon Results ✅

Connected via SSH - Here's what we found:
- **Container ID:** `28700e11bb86`
- **OS:** Ubuntu 22.04.5 LTS
- **Minecraft Server:** Scripts in `/opt/mc/scripts/`
- **No docker socket** mounted
- **No docker command** available
- **No elevated capabilities**

## The Challenge Says:
> An older build of this server image was accidently left public on our ghcr.io registry, might be worth a look...

## Attack Strategy

### Step 1: Find the Public Docker Image

The challenge hints at **ghcr.io** (GitHub Container Registry). Common patterns:

```bash
# Try these image names:
ghcr.io/talldwarf/game-server
ghcr.io/talldwarf/minecraft-server
ghcr.io/talldwarf/stolen-schematics
ghcr.io/tdhost/game-server
ghcr.io/tallhost/minecraft
```

### Step 2: Pull and Inspect the Image

```bash
# Pull the image
docker pull ghcr.io/<org>/<image>:latest

# Inspect for secrets
docker history ghcr.io/<org>/<image> --no-trunc
docker inspect ghcr.io/<org>/<image>

# Run and explore
docker run -it ghcr.io/<org>/<image> /bin/bash

# Look for:
# - SSH keys
# - Passwords in environment variables
# - Configuration files
# - The malicious JAR file
# - Docker socket configurations
```

### Step 3: Look for Container Escape Vectors

Based on the recon, standard escapes won't work:
- ❌ No docker socket
- ❌ No docker command
- ❌ No elevated capabilities
- ❌ Not privileged

**Need to find:**
1. **Credentials** to access host or other containers
2. **Vulnerabilities** in the entrypoint scripts
3. **SSH keys** to pivot
4. **Exposed services** on the host

### Step 4: Examine the Scripts

From the processes we saw:
```bash
/entrypoint.sh
/opt/mc/scripts/sync-loop.sh
```

Reconnect and examine these:
```bash
ssh player@instance.ctf.tdho.st -p 32904
# Password: reyalp

cat /entrypoint.sh
cat /opt/mc/scripts/sync-loop.sh
ls -la /opt/mc/
find /opt -type f 2>/dev/null
```

### Step 5: Look for the Malicious JAR

```bash
find / -name '*.jar' -ls 2>/dev/null
find / -name '*malicious*' 2>/dev/null
find / -name '*backdoor*' 2>/dev/null
```

### Step 6: Check for SSH Keys or Credentials

```bash
find / -name 'id_rsa' -o -name 'id_ed25519' 2>/dev/null
find / -name 'authorized_keys' 2>/dev/null
find / -name '.ssh' -type d 2>/dev/null
grep -r "password" /opt/ 2>/dev/null
grep -r "ssh" /opt/ 2>/dev/null
```

### Step 7: Network Reconnaissance

```bash
ip addr
ip route
cat /etc/hosts
netstat -tulpn 2>/dev/null || ss -tulpn
```

Look for other containers or services on the network.

### Step 8: Check Environment Variables

```bash
env
cat /proc/1/environ | tr '\0' '\n'
```

## Most Likely Solution Paths

### Path A: Credentials in Public Image
1. Pull the public ghcr.io image
2. Find SSH keys or credentials
3. Use them to access host or another container
4. Get the flag

### Path B: Script Vulnerability
1. Find vulnerability in `/entrypoint.sh` or sync scripts
2. Exploit to escape or access another container
3. Get the flag

### Path C: Network Pivot
1. Scan the internal network
2. Find another game server container
3. Access it via found credentials
4. Get the flag

## Commands to Run Next

```bash
# Reconnect
ssh player@instance.ctf.tdho.st -p 32904
# Password: reyalp

# Full recon
cat /entrypoint.sh
cat /opt/mc/scripts/sync-loop.sh
ls -laR /opt/ | head -100
env
find / -name '*.jar' 2>/dev/null
find / -type f -name 'id_*' 2>/dev/null
cat ~/.bash_history
```

## Docker Image Investigation Commands

```powershell
# On your local machine, try to find and pull the image
docker search ghcr.io/talldwarf
docker pull ghcr.io/talldwarf/game-server:latest

# Inspect it
docker history --no-trunc ghcr.io/talldwarf/game-server:latest
docker run -it ghcr.io/talldwarf/game-server:latest /bin/bash

# Inside the image:
find / -name '*.key' -o -name 'id_rsa' -o -name '*.pem'
cat /entrypoint.sh
env
ls -la /opt/mc/
```

## Next Steps

1. **Reconnect to SSH** and examine scripts
2. **Try to find the public Docker image** on ghcr.io
3. **Look for credentials** in the image
4. **Network scan** for other containers
5. **Examine the malicious JAR file** if found

The key is likely in the **public Docker image** as the challenge strongly hints at it!
