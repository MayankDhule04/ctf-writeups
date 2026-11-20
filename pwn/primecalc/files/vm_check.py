import paramiko
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.137.128', port=22, username='kali', password='Mayank_1601',
          look_for_keys=False, allow_agent=False, timeout=15)


def run(cmd):
    i, o, e = c.exec_command(cmd, timeout=120)
    return o.read().decode(errors='replace') + e.read().decode(errors='replace')


for label, cmd in [
    ('uname', 'uname -a'),
    ('docker', 'docker --version; docker info >/dev/null 2>&1 && echo ok || echo no-perm; groups'),
    ('net', 'curl -sS -o /dev/null -w "%{http_code}\\n" https://github.com'),
    ('disk', 'df -h / | tail -1'),
]:
    print(f'--- {label} ---')
    print(run(cmd))
c.close()
