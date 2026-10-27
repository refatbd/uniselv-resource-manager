"""Regression: native reload preserves routing and gracefully reloads PHP masters."""
import ast,contextlib,pathlib,types,unittest,re

class NativeReloadTests(unittest.TestCase):
 def setUp(self):
  self.calls=[];self.reconciles=[];self.signals=[];self.active={'wpiso-manager-php84.service','wpiso-fpm-php84-alice.service','wpiso-health-php84.service'};self.signal_failure=False
  tree=ast.parse((pathlib.Path(__file__).parent/'core/webuzo-isolation.py').read_text(encoding='utf-8'))
  self.ns={'sys':types.SimpleNamespace(exit=lambda c:None),'is_managed':lambda v:True,'assert_launcher':lambda v:None,'reconcile':lambda v,restart:self.reconciles.append((v,restart))or 2,'execute':self.execute,'manifest':lambda v:{'pools':[{'user':'alice'},{'user':'idle'}]},'names':lambda v,u:('wpiso-fpm-'+v+'-'+u+'.service','proxy','socket'),'lock':lambda v:contextlib.nullcontext()}
  exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in['action','graceful_reload']],type_ignores=[]),'shipping-runtime','exec'),self.ns)
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
if __name__=='__main__':unittest.main()
