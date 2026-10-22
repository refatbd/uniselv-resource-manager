#!/usr/bin/python3
"""Read-only comparison with an explicit root-owned generator export.

Does not install settings or certify application capacity/lifecycle. Prints only
allowlisted configuration values; credentials and account names are not emitted.
"""
import json,pathlib,subprocess,re,hashlib,os,sys,time
P=pathlib.Path
def run(args):
 result=subprocess.run(args,text=True,capture_output=True,timeout=45)
 if result.returncode:raise RuntimeError('Configuration read/check failed: '+str(args[:2]))
 return result.stdout
def normalized(value):
 if value is None:return ''
 if isinstance(value,bool):return int(value)
 if isinstance(value,(int,float)):return value
 text=str(value).strip()
 if text.lower() in ['on','true']:return 1
 if text.lower() in ['off','false']:return 0
 if re.fullmatch(r'-?\d+(?:\.\d+)?',text):return float(text)
 return re.sub(r'\s+','',text)
def size(value):
 match=re.fullmatch(r'(\d+)\s*([KMGT]?)',str(value),re.I)
 return int(match[1])*{'':1,'K':1024,'M':1024**2,'G':1024**3,'T':1024**4}[match[2].upper()] if match else value
def audit(path):
 st=path.stat()
 if path.is_symlink() or st.st_uid!=0 or st.st_mode&0o022:raise RuntimeError('Profile must be a root-owned non-writable file')
 raw=path.read_bytes();doc=json.loads(raw);c=doc['configuration'];h=c['globalInputs']['hardware'];sections=c['sections'];rows=[]
 def compare(section,key,expected,actual,kind=None):
  a,b=(size(expected),size(actual)) if kind=='size' else (normalized(expected),normalized(actual))
  # PHP uses an empty string for disabled bools; numeric configuration zeros remain 0.
  if isinstance(expected,bool) and b=='':b=0
  rows.append({'section':section,'key':key,'expected':expected,'actual':actual,'match':a==b})
 ram=int(re.search(r'MemTotal:\s+(\d+)',P('/proc/meminfo').read_text())[1])//1024
 compare('hardware','cpu',h['cpu'],os.cpu_count());compare('hardware','measuredRamMiB',h['measuredRamMiB'],ram)
 versions=sorted(p.name for p in P('/usr/local/apps').glob('php*') if (p/'bin/php').is_file() and (p/'etc/php-fpm.conf').is_file())
 compare('hardware','phpVersions',sorted(h['phpVersions']),versions)
 native=json.loads(P('/var/webuzo/conf/php-fpm').read_text())
 for version,expected in sections['phpIni']['byVersion'].items():
  keys=list(expected);php='$out=[];$saved=[];$files=array_merge([php_ini_loaded_file()],array_filter(array_map("trim",explode(",",php_ini_scanned_files()))));foreach($files as $file){$values=parse_ini_file($file,false,INI_SCANNER_RAW);if(is_array($values)){$saved=array_merge($saved,$values);}}foreach('+json.dumps(keys)+' as $key){$out[$key]=in_array($key,["max_execution_time","max_input_time"])?($saved[$key]??null):get_cfg_var($key);}echo json_encode($out);'
  actual=json.loads(run(['/usr/local/apps/'+version+'/bin/php','-c','/usr/local/apps/'+version+'/etc/php.ini','-r',php]))
  for key,value in expected.items():compare('phpIni',version+':'+key,value,actual.get(key),'size' if key=='realpath_cache_size' else None)
  for key,value in sections['phpFpm']['settings'].items():
   field=key.replace('pm_','pm.',1) if key.startswith('pm_') else key
   compare('phpFpm',version+':'+key,value,native.get(version,{}).get(field))
  health=run(['systemctl','show','wpiso-health-'+version+'.service','-p','ExecStart','--value'])
  compare('health',version+':smallCacheAndStrings',True,'opcache.memory_consumption=16 -d opcache.interned_strings_buffer=4' in health)
  compare('services',version+':coordinator','active',run(['systemctl','is-active','wpiso-manager-'+version+'.service']).strip())
 for plan in sections['resourcePlans']['plans']:
  actual=json.loads((P('/var/webuzo/cgroups')/plan['plan'].lower()).read_text())
  for key,value in plan['apiParameters'].items():
   if key in actual:compare('resourcePlans',plan['plan']+':'+key,value,actual[key])
 for key,value in sections['isolation']['policy'].items():compare('isolation',key,value,json.loads(P('/etc/webuzo-isolation/policy.json').read_text()).get(key))
 mysql=sections['mysql']['settings'];names=[key.replace('-','_') for key in mysql]
 query='SHOW GLOBAL VARIABLES WHERE Variable_name IN ('+','.join("'"+name+"'" for name in names)+')'
 actual=dict(line.split('\t',1) for line in run(['mysql','--defaults-extra-file=/root/.my.cnf','-NBe',query]).splitlines() if '\t' in line)
 for key,value in mysql.items():
  key=key.replace('-','_');compare('mysql',key,value,actual.get(key),'size' if re.fullmatch(r'\d+[KMGT]',str(value)) else None)
 apache=P('/usr/local/apps/apache2/etc/conf.d/webuzo.conf').read_text()
 directives={'start':'StartServers','minSpare':'MinSpareServers','maxSpare':'MaxSpareServers','serverLimit':'ServerLimit','workers':'MaxRequestWorkers','requests':'MaxRequestsPerChild','connections':'MaxConnectionsPerChild','keepAlive':'KeepAlive','keepAliveTimeout':'KeepAliveTimeout','keepAliveMax':'MaxKeepAliveRequests','timeout':'Timeout','cipher':'SSLCipherSuite','protocols':'SSLProtocol','trace':'TraceEnable','signature':'ServerSignature','etag':'FileETag','logLevel':'LogLevel'}
 for key,directive in directives.items():
  values=re.findall(r'^\s*'+directive+r'\s+([^\r\n]+)',apache,re.M|re.I)
  if not values and directive=='MaxRequestsPerChild':values=re.findall(r'^\s*MaxConnectionsPerChild\s+([^\r\n]+)',apache,re.M|re.I)
  compare('apache',key,sections['apache']['settings'][key],values[-1] if values else None)
 modules=run(['/usr/local/apps/apache2/bin/httpd','-M'])
 compare('apache','prefork',True,'mpm_prefork_module' in modules);compare('apache','ruid2',True,'ruid2_module' in modules)
 run(['/usr/local/apps/apache2/bin/httpd','-t'])
 golden=json.loads(P('/etc/golden-shield/policy.json').read_text())
 for key in ['customerCpuPercent','hostingMemoryMaxMiB','headroomMiB']:compare('golden',key,sections['golden']['policy'][key],golden.get(key))
 group=P('/sys/fs/cgroup/golden.slice')
 quota,period=(group/'cpu.max').read_text().split();compare('kernel','aggregateCpuPercent',golden['customerCpuPercent'],int(quota)*100/int(period))
 compare('kernel','aggregateMemoryBytes',golden['hostingMemoryMaxMiB']*1048576,int((group/'memory.max').read_text()))
 compare('swap','hostSwapBytes',0,int(re.search(r'SwapTotal:\s+(\d+)',P('/proc/meminfo').read_text())[1])*1024)
 exceptions=[];ini_keys=set(sections['phpIni']['settings'])
 for file in P('/home').glob('*/public_html/.user.ini'):
  if file.is_symlink() or not file.is_file():continue
  for line in file.read_text(errors='replace').splitlines():
   match=re.match(r'^\s*([a-zA-Z_][\w.]*)\s*=',line)
   if match and match[1] in ini_keys:exceptions.append({'path':str(file),'key':match[1]})
 report={'schemaVersion':1,'at':int(time.time()),'profileSha256':hashlib.sha256(raw).hexdigest(),'scope':'Allowlisted saved/configured values, service state and kernel aggregate limits; HTTP and load evidence are separate. Root document .user.ini exceptions are listed; nested/application overrides require HTTP checks. Not a complete virtual-host parser or lifecycle certificate.','checks':len(rows),'mismatches':[row for row in rows if not row['match']],'inheritanceExceptions':exceptions,'rows':rows}
 return report
if __name__=='__main__':
 try:
  if os.geteuid()!=0:raise PermissionError('Root required')
  result=audit(P(sys.argv[1] if len(sys.argv)>1 else '/etc/webuzo-isolation/generator-profile.json'))
  print(json.dumps(result,indent=2));sys.exit(1 if result['mismatches'] else 0)
 except Exception as error:print(json.dumps({'error':str(error)}));sys.exit(2)
