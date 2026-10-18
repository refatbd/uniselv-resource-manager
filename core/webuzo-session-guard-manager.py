#!/usr/bin/python3
"""Experimental AlmaLinux PAM boundary; protected backups and exact reset."""
import hashlib,json,os,pathlib,shutil,subprocess,sys,time
STATE=pathlib.Path('/var/lib/webuzo-session-guard')
TARGET=pathlib.Path('/usr/local/sbin/webuzo-session-guard.py')
REGISTRY=STATE/'files.json'
SERVICES=['cron','crond','sshd','su','su-l','sudo','sudo-i','runuser','runuser-l']
LINE='session required pam_exec.so quiet /usr/local/sbin/webuzo-session-guard.py'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def atomic(p,data,mode=0o600):
 if p.is_symlink():raise RuntimeError('Refusing symlink: '+str(p))
 t=p.with_name(p.name+'.session-guard-'+str(time.time_ns()))
 with open(t,'xb') as f:f.write(data)
 os.chmod(t,mode);os.replace(t,p)
def restore(rows):
 for name,row in rows.items():
  p=pathlib.Path(name)
  if p.is_symlink() or digest(p) not in [row['originalHash'],row['hash']]:raise RuntimeError('PAM file changed; review protected backup before reset: '+name)
 for name,row in rows.items():shutil.copy2(row['backup'],name)
def main():
 if os.geteuid()!=0:raise RuntimeError('Run with sudo')
 action=sys.argv[1] if len(sys.argv)>1 else 'check'
 if STATE.is_symlink():raise RuntimeError('Unsafe state directory')
 STATE.mkdir(mode=0o700,parents=True,exist_ok=True);STATE.chmod(0o700)
 if action=='install':
  if REGISTRY.exists():raise RuntimeError('Already installed: run check or uninstall first')
  if not pathlib.Path('/var/lib/golden-shield/installed.json').is_file():raise RuntimeError('Install and verify Golden Shield first')
  source=pathlib.Path(sys.argv[2]);data=source.read_bytes();compile(data,str(TARGET),'exec')
  helper_preexisting = TARGET.exists()
  if TARGET.is_symlink():raise RuntimeError('Unsafe helper symlink')
  if helper_preexisting and (TARGET.read_bytes()!=data or TARGET.stat().st_uid!=0 or TARGET.stat().st_mode&0o022):raise RuntimeError('Different or unsafe untracked helper; review before installing')
  atomic(STATE/'helper-ownership.json',json.dumps({'preexisting':helper_preexisting,'sha256':hashlib.sha256(data).hexdigest()}).encode())
  rows={}
  for service in SERVICES:
   p=pathlib.Path('/etc/pam.d')/service
   if not p.exists():continue
   if p.is_symlink():raise RuntimeError('Unsupported symlink PAM file: '+str(p))
   old=p.read_bytes()
   if b'webuzo-session-guard' in old:raise RuntimeError('Unexpected existing hook: '+str(p))
   new=old.rstrip()+b'\n# Webuzo account session boundary; root/non-hosting admins are exempt.\n'+LINE.encode()+b'\n'
   backup=STATE/service;shutil.copy2(p,backup)
   rows[str(p)]={'backup':str(backup),'originalHash':digest(p),'hash':hashlib.sha256(new).hexdigest(),'mode':p.stat().st_mode&0o777,'new':new.decode()}
  if not rows:raise RuntimeError('No supported PAM services found')
  atomic(REGISTRY,json.dumps(rows,indent=2).encode())
  try:
   atomic(TARGET,data,0o755)
   for name,row in rows.items():atomic(pathlib.Path(name),row['new'].encode(),row['mode'])
  except Exception:
   restore(rows);TARGET.unlink(missing_ok=True);REGISTRY.rename(STATE/('failed-install-'+str(time.time_ns())+'.json'));raise
  print('Installed. Keep an admin session open; verify native cron, SSH and CPU/RAM boundaries before relying on it.')
 elif action=='uninstall':
  rows=json.loads(REGISTRY.read_text());restore(rows)
  helper_meta=json.loads((STATE/'helper-ownership.json').read_text()) if (STATE/'helper-ownership.json').exists() else {'preexisting':False}
  if not helper_meta.get('preexisting'):TARGET.unlink(missing_ok=True)
  REGISTRY.rename(STATE/('uninstalled-files-'+str(time.time_ns())+'.json'))
  print('Exact original PAM files restored. Existing sessions finish normally.')
 elif action=='check':
  rows=json.loads(REGISTRY.read_text())
  for name,row in rows.items():
   if digest(pathlib.Path(name))!=row['hash']:raise RuntimeError('PAM configuration changed: '+name)
  if not TARGET.is_file() or TARGET.stat().st_uid!=0 or TARGET.stat().st_mode&0o022:raise RuntimeError('Unsafe or missing helper')
  if not pathlib.Path('/var/lib/golden-shield/installed.json').is_file():raise RuntimeError('Golden Shield dependency missing')
  print('PASS: '+str(len(rows))+' PAM hooks and root-owned helper; repeat actual session tests after maintenance.')
 else:raise RuntimeError('Use install SOURCE, check, or uninstall')
if __name__=='__main__':main()
