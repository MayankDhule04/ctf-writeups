<#
  ctfbox.ps1 — run a tool from the ctfbox image against the current folder.

  Examples (run from your ctf workspace root):
    .\docker\ctfbox.ps1 nmap -sV scanme.nmap.org
    .\docker\ctfbox.ps1 ffuf -u https://target/FUZZ -w /usr/share/wordlists/x.txt
    .\docker\ctfbox.ps1 steghide extract -sf case.jpg
    .\docker\ctfbox.ps1 stegseek case.jpg /work/rockyou.txt
    .\docker\ctfbox.ps1 r2 -AA ./binary
    .\docker\ctfbox.ps1 jadx -d out app.apk
    .\docker\ctfbox.ps1              # no args -> interactive shell

  The current directory is mounted read-write at /work inside the container.
#>
param([Parameter(ValueFromRemainingArguments = $true)] $Cmd)

$mount = "$($PWD.Path):/work"
if (-not $Cmd -or $Cmd.Count -eq 0) {
    docker run --rm -it -e TERM=xterm -v $mount -w /work ctfbox:latest /bin/bash
} else {
    docker run --rm -i -e TERM=xterm -v $mount -w /work ctfbox:latest @Cmd
}
