#!/usr/bin/python3
"""Experimental PAM session placement. Account boundary precedes user execution."""
import json,os,pathlib,pwd,re,subprocess,sys,time
def main():
 if os.environ.get('PAM_TYPE')!='open_session':return
 if os.geteuid()!=0:raise RuntimeError('Privileged session helper required')
 user=os.environ.get('PAM_USER','')
 if not re.fullmatch(r'[a-z_][a-z0-9_-]{0,31}',user):raise RuntimeError('Invalid PAM user')
 account=pwd.getpwnam(user)
 if account.pw_uid<1000 or not (pathlib.Path('/var/webuzo/users')/user).is_dir():return
 uid=account.pw_uid;parent=os.getppid();target='/golden.slice/golden-'+str(uid)+'.slice'
 current=pathlib.Path('/proc',str(parent),'cgroup').read_text().strip()
 if current=='0::'+target or current.startswith('0::'+target+'/'):return
 if not pathlib.Path('/var/lib/golden-shield/installed.json').is_file():raise RuntimeError('Golden Shield is not installed')
 subprocess.run(['/usr/bin/python3','/usr/local/sbin/golden-shield.py','prepare-account',str(uid)],capture_output=True,check=True,timeout=20)
 root=pathlib.Path('/sys/fs/cgroup'+target)
 for name in ['cpu.max','memory.max','pids.max']:
  if (root/name).read_text().strip().startswith('max'):raise RuntimeError('Unbounded account '+name)
 if (root/'memory.swap.max').read_text().strip()!='0':raise RuntimeError('Account swap must be zero')
 unit='webuzo-session-u'+str(uid)+'-p'+str(parent)+'-'+str(time.time_ns())+'.scope'
 args=['/usr/bin/busctl','call','org.freedesktop.systemd1','/org/freedesktop/systemd1','org.freedesktop.systemd1.Manager','StartTransientUnit','ssa(sv)a(sa(sv))',unit,'fail','3','Slice','s','golden-'+str(uid)+'.slice','PIDs','au','1',str(parent),'MemorySwapMax','t','0','0']
 r=subprocess.run(args,capture_output=True,text=True,timeout=20)
 if r.returncode:raise RuntimeError('Scope creation failed: '+r.stderr[-300:])
 for _ in range(100):
  cg=pathlib.Path('/proc',str(parent),'cgroup').read_text().strip()
  if cg.startswith('0::'+target+'/'):
   return
  time.sleep(.02)
 raise RuntimeError('Parent process did not enter its account boundary')
if __name__=='__main__':
 try:main()
 except Exception as e:
  print('Webuzo session resource guard: '+str(e),file=sys.stderr)
  sys.exit(1)
