import sys
sys.path.append('../')
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta


import lisfloodRunManager as lfrm


def launchTestRun():
  runningDir = '/ADAPTATION/mentalo/lisfloodRun/testEuropeRestartECMWFAutomatic/run/'
  runRootDir = "/ADAPTATION/mentalo/lisfloodRun/testEuropeRestartECMWFAutomatic"
  initDir = os.path.join(runRootDir, 'init')
  tmpOutDir = os.path.join(runRootDir, "tmpout")
  outDir = os.path.join(runRootDir, "out")
  rootConfDir = "/ADAPTATION/mentalo/lisfloodRun/LisfloodEurope"
  waterUseDir = "/ADAPTATION/mentalo/lisfloodRun/waterdemandEurope/static/hist"
  meteoDir = "/ADAPTATION/mentalo/lisfloodRun/meteoEurope/CNRM-CERFACS-CNRM-CM5/historical"
  calendarStart = datetime(1981, 1, 1)
  calendarEnd = datetime(1982, 1, 1)
  dtRestart = relativedelta(months = 1)
  dtReWarmUp = relativedelta(days = 3)
  py = '/ADAPTATION/usr/anaconda2/bin/python'
  lisfloodpy = '/ADAPTATION/mentalo/src/git/lisflood-ecmwf/Lisflood/lisf1.py'
  lisfloodcmd = '{python} {lisflood}'.format(python=py, lisflood=lisfloodpy)
 
  lfManager = lfrm.lisfloodRunManager( initDir, runningDir, tmpOutDir, outDir,
                      meteoDir, rootConfDir, waterUseDir,
                      calendarStart, calendarEnd, lisfloodcmd,
                      dtRestart=dtRestart, dtReWarmUp=dtReWarmUp )
  import pdb; pdb.set_trace()
  lfManager.iterateRun()


if __name__ == '__main__':
  launchTestRun()
  



