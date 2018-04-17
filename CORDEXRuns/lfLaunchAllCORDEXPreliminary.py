import lfLaunchAllCORDEX
from dateutil.relativedelta import relativedelta

if __name__ == '__main__':
  scenarios = ['historical', 'rcp85', 'rcp45']
  outDir = '/eos/jeodpp/data/projects/CRITECH/ADAPTATION/lisflood/coldInit'
  runDirRoot = '/eos/jeodpp/data/projects/CRITECH/ADAPTATION/lisflood/run_preliminary'
  preliminaryRun = True
  import pdb; pdb.set_trace()
  lfLaunchAllCORDEX.launchAll(scenarios=scenarios, outDir=outDir, runDirRoot=runDirRoot, preliminaryRun=preliminaryRun)

