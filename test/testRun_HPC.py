import os
import sys
libpath = os.path.join( os.path.dirname(os.path.abspath(__file__)), '../' )
sys.path.append(libpath)
from datetime import datetime
from dateutil.relativedelta import relativedelta


import lisfloodRunManager as lfrm


def launchTestRun():
  print('starting the test simulation')
  runningDir = '/ADAPTATION/mentalo/lisfloodRun/testEuropeRestartJRCAutomatic/run/'
  runRootDir = "/ADAPTATION/mentalo/lisfloodRun/testEuropeRestartJRCAutomatic"
  initDir = os.path.join(runRootDir, 'init')
  tmpOutDir = os.path.join(runRootDir, "tmpout")
  outDir = os.path.join(runRootDir, "out")
  rootConfDir = "/ADAPTATION/mentalo/lisfloodRun/LisfloodEurope"
  waterUseDir = "/ADAPTATION/mentalo/lisfloodRun/waterdemandEurope/static/hist"
  waterUse = True
  meteoDir = "/ADAPTATION/mentalo/lisfloodRun/meteoEurope/CNRM-CERFACS-CNRM-CM5/historical"
  calendarStart = datetime(1981, 1, 1)
  calendarEnd = datetime(1982, 1, 1)
  dtRestart = relativedelta(months = 1)
  dtReWarmUp = relativedelta(days = 3)
  py = '/ADAPTATION/usr/anaconda2/bin/python'
  lisfloodpy = '/ADAPTATION/mentalo/src/git/lisflood/Lisflood/lisf1.py'
  lisfloodcmd = '{python} {lisflood}'.format(python=py, lisflood=lisfloodpy)
 
  print('initializing the lisfloodRunManager')
  lfManager = lfrm.lisfloodRunManager( initDir, runningDir, tmpOutDir, outDir,
                      meteoDir, rootConfDir, waterUse, waterUseDir,
                      calendarStart, calendarEnd, lisfloodcmd,
                      dtRestart=dtRestart, dtReWarmUp=dtReWarmUp )
  print('starting the iterating run')
  lfManager.iterateRun()


if __name__ == '__main__':
  launchTestRun()
  



