import os, re, subprocess

def jobIsAlive(model, scenario, waterUseStr, logDir='/eos/jeodpp/htcondor/processing_logs/CRITECH'):
  logFlPattern = 'job_lisflood_{waterUseStr}_{scen}_{mdl}_([0-9]*)_(.*).log'.format(
                    waterUseStr=waterUseStr, scen=scenario, mdl=model)

  fls = [f for f in os.listdir(logDir) if re.match(logFlPattern, f)]
  fls.sort()
  for f in fls:
    rem = re.match(logFlPattern, f)
    jobId = rem.groups()[0]
    runstr = subprocess.check_output(['condor_q', jobId]).strip('\n \t\r').split('\n')[-1]
    if runstr[0] == '0':
      print('        Job ' + jobId + ' is dead.')
    else:
      print('        Job ' + jobId + ' is alive.')
      return True, jobId
  print('        This model is not running, yet or any more')
  return False, -1
      
  


