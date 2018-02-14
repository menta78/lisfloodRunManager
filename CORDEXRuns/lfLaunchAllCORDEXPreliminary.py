import lfLaunchAllCORDEX
from dateutil.relativedelta import relativedelta

if __name__ == '__main__':
  scenarios = ['historical']
  outDir = '/eos/jeodpp/data/projects/CRITECH/ADAPTATION/ClimateRuns/LisfloodEuroCordex_preliminary'
  runDirRoot = '/eos/jeodpp/data/projects/CRITECH/ADAPTATION/lisflood/run_preliminary'
  preliminaryRun = True
  lfLaunchAllCORDEX.launchAll(scenarios=scenarios, outDir=outDir, runDirRoot=runDirRoot, preliminaryRun=preliminaryRun)

