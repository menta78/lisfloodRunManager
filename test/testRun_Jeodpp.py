import os
import sys
libpath = os.path.join( os.path.dirname(os.path.abspath(__file__)), '../' )
print('adding path ' + libpath)
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
  waterUse = False
  calendarStart = datetime(1981, 1, 1)
  calendarEnd = datetime(1982, 1, 1)
  calendar = 'proleptic_gregorian'
  dtRestart = relativedelta(months = 1)
  dtReWarmUp = relativedelta(days = 3)
  py = '/eos/jeodpp/data/projects/CRITECH/miniconda3/envs/LISFLOOD/bin/python'
  lisfloodpy = '/eos/jeodpp/data/projects/CRITECH/ADAPTATION/src/git/lisflood/Lisflood/lisf1.py'
  lisfloodcmd = '{python} {lisflood}'.format(python=py, lisflood=lisfloodpy)

  landUseDir =  "/eos/jeodpp/data/projects/CRITECH/ADAPTATION/lisflood/lisfloodRun/LisfloodEurope/maps_netcdf/landuse/cordex/hist/landuse2010"
  waterUseDir = "/eos/jeodpp/data/projects/CRITECH/ADAPTATION/lisflood/lisfloodRun/waterdemandEurope/static/hist"
  miscVars = {
    'waterUseDir': waterUseDir,
    "meteoDir": "/eos/jeodpp/data/projects/CRITECH/ADAPTATION/lisflood/input/LAEAETRS89_BIAS_CORDEX/IPSL-INERIS-WRF331F/historical",
    "landUseDir": landUseDir,
    "directRunoffFractionMaps": os.path.join(landUseDir, 'fracsealed'),
    "forestFractionMaps": os.path.join(landUseDir, 'fracforest'),
    "waterFractionMaps": os.path.join(landUseDir, 'fracwater'),
    "otherFractionMaps": os.path.join(landUseDir, 'fracother'),
    "irrigationFractionMaps": os.path.join(landUseDir, 'fracirrigated'),
    "riceFractionMaps": os.path.join(landUseDir, 'fracrice'),
    "riceFractionMaps": os.path.join(landUseDir, 'fracrice'),
    "populationMaps": os.path.join(waterUseDir, 'pop'),
    "prefixWaterUseDomestic": 'dom',
    "prefixWaterUseLivestock": "liv",
    "prefixWaterUseEnergy": "ene",
    "prefixWaterUseIndustry": "ind"
  }
 
  print('initializing the lisfloodRunManager')
  lfManager = lfrm.lisfloodRunManager( initDir, runningDir, tmpOutDir, outDir,
                      rootConfDir, waterUse,
                      calendarStart, calendarEnd, calendar, lisfloodcmd, miscVars,
                      modelTag="IPSL-INERIS-WRF331F",
                      dtRestart=dtRestart, dtReWarmUp=dtReWarmUp )
  print('starting the iterating run')
  lfManager.iterateRun()


if __name__ == '__main__':
  launchTestRun()
  



