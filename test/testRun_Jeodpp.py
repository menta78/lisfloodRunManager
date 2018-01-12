import os
import sys
libpath = os.path.join( os.path.dirname(os.path.abspath(__file__)), '../' )
sys.path.append(libpath)
from datetime import datetime
from dateutil.relativedelta import relativedelta


import lisfloodRunManager as lfrm


def launchTestRun():
  print('starting the test simulation')
  runningDir = '/eos/jeodpp/data/projects/CRITECH/ADAPTATION/lisflood/lisfloodRun/testEuropeRestartJRCAutomatic/run/'
  runRootDir = "/eos/jeodpp/data/projects/CRITECH/ADAPTATION/lisflood/lisfloodRun/testEuropeRestartJRCAutomatic"
  initDir = os.path.join(runRootDir, 'init')
  tmpOutDir = os.path.join(runRootDir, "tmpout")
  outDir = os.path.join(runRootDir, "out")
  rootConfDir = "/eos/jeodpp/data/projects/CRITECH/ADAPTATION/lisflood/lisfloodRun/LisfloodEurope"
  waterUseDir = "/eos/jeodpp/data/projects/CRITECH/ADAPTATION/lisflood/lisfloodRun/waterdemandEurope/static/hist"
  meteoDir = "/eos/jeodpp/data/projects/CRITECH/ADAPTATION/lisflood/input/LAEAETRS89_BIAS_CORDEX/IPSL-INERIS-WRF331F/historical"
  calendarStart = datetime(1981, 1, 1)
  calendarEnd = datetime(1982, 1, 1)
  dtRestart = relativedelta(months = 1)
  dtReWarmUp = relativedelta(days = 3)
  py = '/eos/jeodpp/data/projects/CRITECH/miniconda3/envs/LISFLOOD/bin/python'
  lisfloodpy = '/eos/jeodpp/data/projects/CRITECH/ADAPTATION/src/git/lisflood/Lisflood/lisf1.py'
  lisfloodcmd = '{python} {lisflood}'.format(python=py, lisflood=lisfloodpy)
 
  print('initializing the lisfloodRunManager')
  lfManager = lfrm.lisfloodRunManager( initDir, runningDir, tmpOutDir, outDir,
                      meteoDir, rootConfDir, waterUseDir,
                      calendarStart, calendarEnd, lisfloodcmd,
                      dtRestart=dtRestart, dtReWarmUp=dtReWarmUp )
  print('starting the iterating run')
  lfManager.iterateRun()


if __name__ == '__main__':
  launchTestRun()
  



