"""Regression: native reload preserves routing and gracefully reloads PHP masters."""
import ast,contextlib,pathlib,types,unittest,re

class NativeReloadTests(unittest.TestCase):
 def setUp(self):
  self.calls=[];self.reconciles=[];self.signals=[];self.active={'wpiso-manager-php84.service','wpiso-fpm-php84-alice.service','wpiso-health-php84.service'};self.signal_failure=False
  tree=ast.parse((pathlib.Path(__file__).parent/'core/webuzo-isolation.py').read_text(encoding='utf-8'))
  self.ns={'sys':types.SimpleNamespace(exit=lambda c:None),'is_managed':lambda v:True,'assert_launcher':lambda v:None,'reconcile':lambda v,restart:self.reconciles.append((v,restart))or 2,'execute':self.execute,'manifest':lambda v:{'pools':[{'user':'alice'},{'user':'idle'}]},'names':lambda v,u:('wpiso-fpm-'+v+'-'+u+'.service','proxy','socket'),'lock':lambda v:contextlib.nullcontext()}
  exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in['action','graceful_reload','heal_launcher']],type_ignores=[]),'shipping-runtime','exec'),self.ns)
 def execute(self,args,check=True,**kw):
  self.calls.append(args)
  if args[:2]==['systemctl','is-active']:return types.SimpleNamespace(returncode=0 if args[2]in self.active else 3,stdout='')
  if args[:2]==['systemctl','kill']:
   self.signals.append(args)
   return types.SimpleNamespace(returncode=1 if self.signal_failure else 0,stdout='')
  return types.SimpleNamespace(returncode=0,stdout='')
 def test_reload_never_forces_reconcile_restart(self):
  self.ns['action']('php84','reload');self.assertEqual(self.reconciles,[('php84',False)])
 def test_reload_signals_only_active_native_masters(self):
  self.ns['action']('php84','reload')
  self.assertEqual(self.signals,[['systemctl','kill','--kill-whom=main','--signal=USR2','wpiso-fpm-php84-alice.service'],['systemctl','kill','--kill-whom=main','--signal=USR2','wpiso-health-php84.service']])
  self.assertFalse(any(c[:2]in[['systemctl','stop'],['systemctl','restart']]for c in self.calls))
 def test_explicit_restart_retains_restart_semantics(self):
  self.ns['action']('php84','restart');self.assertEqual(self.reconciles,[('php84',True)]);self.assertEqual(self.signals,[])
 def test_start_does_not_restart_healthy_pools(self):
  self.ns['action']('php84','start');self.assertEqual(self.reconciles,[('php84',False)]);self.assertEqual(self.signals,[])
 def test_reload_starts_an_inactive_coordinator(self):
  self.active.remove('wpiso-manager-php84.service');self.ns['action']('php84','reload');self.assertEqual(self.reconciles,[]);self.assertIn(['systemctl','start','wpiso-manager-php84.service'],self.calls)
 def test_failed_reload_signal_is_not_reported_as_success(self):
  self.signal_failure=True
  with self.assertRaises(RuntimeError):self.ns['action']('php84','reload')
 def test_inactive_pools_are_not_started_just_to_reload(self):
  self.active={'wpiso-manager-php84.service'};self.ns['action']('php84','reload');self.assertEqual(self.signals,[])
 def test_validation_failure_sends_no_signal(self):
  def invalid(*args):raise ValueError('invalid native configuration')
  self.ns['reconcile']=invalid
  with self.assertRaises(ValueError):self.ns['action']('php84','reload')
  self.assertEqual(self.signals,[])
 def test_launcher_drift_auto_repairs_during_action(self):
  heals=[]
  self.ns['heal_launcher']=lambda v:heals.append(v)
  def faulty_assert(v):
   if not heals: raise RuntimeError('drift')
  self.ns['assert_launcher']=faulty_assert
  self.ns['action']('php84','start')
  self.assertEqual(heals,['php84'])

class ReloadControlTests(unittest.TestCase):
 def setUp(self):
  tree=ast.parse((pathlib.Path(__file__).parent/'core/webuzo-isolation.py').read_text(encoding='utf-8'));self.ns={'re':re}
  exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='reload_control_settings'],type_ignores=[]),'shipping-runtime','exec'),self.ns)
 def apply(self,text,timeout):return self.ns['reload_control_settings'](text,timeout)
 def test_native_ten_second_escalation_cannot_cut_a_valid_request(self):self.assertIn('process_control_timeout = 120s',self.apply('process_control_timeout = 10s\n',120))
 def test_missing_control_is_inserted_once(self):
  result=self.apply('emergency_restart_threshold = 10\n',90);self.assertEqual(result.count('process_control_timeout'),1);self.assertEqual(self.apply(result,90),result)
 def test_existing_longer_operator_value_is_preserved(self):self.assertEqual(self.apply('process_control_timeout = 5m\n',120),'process_control_timeout = 5m\n')
 def test_hardware_profile_request_timeout_remains_the_input(self):self.assertIn('process_control_timeout = 45s',self.apply('',45))
 def test_duplicate_controls_fail_closed(self):
  with self.assertRaises(ValueError):self.apply('process_control_timeout = 10s\nprocess_control_timeout = 2m\n',120)
 def test_malformed_control_fails_closed(self):
  with self.assertRaises(ValueError):self.apply('process_control_timeout = invalid\n',120)
 def test_unbounded_request_timeout_refused(self):
  with self.assertRaises(ValueError):self.apply('',0)

class ScopeLeakAndUpgradeResilienceTests(unittest.TestCase):
 def test_transient_scopes_use_collect_mode_inactive_or_failed(self):
  iso_src=(pathlib.Path(__file__).parent/'core/webuzo-isolation.py').read_text(encoding='utf-8')
  ses_src=(pathlib.Path(__file__).parent/'core/webuzo-session-guard.py').read_text(encoding='utf-8')
  tree=ast.parse(iso_src)
  calls=[]
  ns={'pathlib':types.SimpleNamespace(Path=lambda p:types.SimpleNamespace(exists=lambda:True)),'account_slice':lambda uid:'golden-1001.slice','time':types.SimpleNamespace(time_ns=lambda:123),'execute':lambda args,check=True,**kw:calls.append(args)or types.SimpleNamespace(returncode=0,stdout='')}
  exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in['place_native_process','cleanup_failed_transient_scopes']],type_ignores=[]),'iso-scope','exec'),ns)
  ns['place_native_process'](1001,4242,pathlib.Path('/sys/fs/cgroup/golden.slice/golden-1001.slice'))
  self.assertEqual(len(calls),1)
  self.assertIn('CollectMode',calls[0])
  self.assertIn('inactive-or-failed',calls[0])
  self.assertEqual(calls[0][-1],'0')
  self.assertLess(calls[0].index('CollectMode'),len(calls[0])-1)
  idx=calls[0].index('fail')
  self.assertEqual(calls[0][idx+1],'4')
  self.assertIn("'CollectMode','s','inactive-or-failed','0'",ses_src)
  self.assertIn("'fail','4','Slice'",ses_src)

 def test_golden_shield_redis_conf_aclfile_reconcile_and_upgrade_healing(self):
  import hashlib,json,tempfile
  gs_path=pathlib.Path(__file__).parent/'core/golden-shield.py'
  tree=ast.parse(gs_path.read_text(encoding='utf-8'))
  with tempfile.TemporaryDirectory() as td:
   base=pathlib.Path(td);state=base/'state';units=base/'units';state.mkdir();units.mkdir()
   (state/'backups').mkdir();(base/'etc').mkdir()
   redis_conf=base/'redis.conf';apachectl=base/'apachectl'
   orig_conf='bind 127.0.0.1\nport 6379\n# BEGIN Webuzo Planner Shared Redis\nmaxmemory 128mb\nmaxmemory-policy allkeys-lru\nmaxclients 128\nprotected-mode yes\n# END Webuzo Planner Shared Redis\n'
   redis_conf.write_bytes((orig_conf+'aclfile /usr/local/apps/redis/users.acl\n').encode('utf-8'))
   orig_hash=hashlib.sha256(orig_conf.encode()).hexdigest()
   wrapper='#!/bin/sh\n# Golden Shield shared Apache launcher\n'
   apachectl.write_bytes(wrapper.encode('utf-8'))
   shared_files={
    str(redis_conf):{'backup':str(state/'backups/r'),'mode':0o644,'uid':0,'gid':0,'hash':orig_hash},
    str(apachectl):{'backup':str(state/'apachectl.original'),'mode':0o755,'uid':0,'gid':0,'hash':hashlib.sha256(wrapper.encode()).hexdigest()},
   }
   (state/'shared-files.json').write_bytes(json.dumps(shared_files).encode('utf-8'))
   (state/'installed.json').write_bytes(json.dumps({'version':2}).encode('utf-8'))
   (base/'etc/shared-redis-policy.json').write_bytes(json.dumps({'datasetMiB':128,'memoryMiB':512,'maxclients':128}).encode('utf-8'))
   cmds=[]
   ns={'re':re,'json':json,'hashlib':hashlib,'pathlib':pathlib,'shlex':__import__('shlex'),'time':__import__('time'),'os':__import__('os'),
       'fcntl':types.SimpleNamespace(flock=lambda *a:None,LOCK_EX=2),
       'BASE':base/'etc','STATE':state,'UNITS':units,'REDIS_CONFIG':redis_conf,'APACHE':apachectl,'INIT':base/'init_httpd',
       'command':lambda args,check=True:cmds.append(args)or types.SimpleNamespace(returncode=0,stdout='',stderr=''),
       'properties':lambda u,k:{'ActiveState':'inactive','ControlGroup':''}}
   fn_names=['files','atomic','managed','shared_redis_config','apache_launcher','reconcile_redis_conf_registry','heal_managed_upgrades']
   exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in fn_names],type_ignores=[]),'gs-resilience','exec'),ns)
   reconciled,unresolved=ns['reconcile_redis_conf_registry']()
   self.assertEqual((reconciled,unresolved),(1,0))
   updated=json.loads((state/'shared-files.json').read_text())
   self.assertEqual(updated[str(redis_conf)]['hash'],hashlib.sha256(redis_conf.read_bytes()).hexdigest())
   # Simulate Webuzo upgrading apachectl (native httpd -k wrapper) and overwriting redis.conf
   apachectl.write_bytes(b'#!/bin/sh\nARGV="$@"\nexec /usr/local/apps/apache2/bin/httpd -k $ARGV\n')
   redis_conf.write_bytes(b'bind 127.0.0.1\nport 6379\naclfile /usr/local/apps/redis/users.acl\n')
   healed=ns['heal_managed_upgrades']()
   self.assertTrue(healed['apachectl_repaired'])
   self.assertTrue(healed['redis_conf_repaired'])
   self.assertIn('# Golden Shield shared Apache launcher',apachectl.read_text())
   self.assertIn('# BEGIN Webuzo Planner Shared Redis',redis_conf.read_text())

 def test_root_and_plugin_mirrored_files_are_identical(self):
  root=pathlib.Path(__file__).parent
  pairs=[]
  for folder in('agent','core'):
   for p in sorted((root/folder).glob('*')):
    if p.is_file() and p.suffix in('.py','.php','.service','.html'):
     pairs.append((p,root/'plugin'/folder/p.name))
  pairs.append((root/'CHANGELOG.md',root/'plugin'/'CHANGELOG.md'))
  for src,dst in pairs:
   self.assertTrue(dst.exists(),msg=f'Missing plugin mirror: {dst}')
   self.assertEqual(src.read_bytes().replace(b'\r\n',b'\n'),dst.read_bytes().replace(b'\r\n',b'\n'),msg=f'Parity mismatch: {src.relative_to(root)} vs {dst.relative_to(root)}')
if __name__=='__main__':unittest.main()
