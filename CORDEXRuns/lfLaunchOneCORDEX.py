import pickle
import os, sys
from dateutil.relativedelta import relativedelta
libpath = os.path.join( os.path.dirname(os.path.abspath(__file__)), '../' )
print('adding path ' + libpath)
sys.path.append(libpath)
import lisfloodRunManager as lfrm



class _iniObj:
  pass


def doLaunch():
  iniFile = os.environ['LF_INIT_FILE']
  with open(iniFile) as ifl:
    ii = pickle.load(ifl)
  runDirMdl = ii.runDirMdl
  initDirMdl = ii.initDirMdl
  tmpOutDirMdl = ii.tmpOutDirMdl
  outDirMdl = ii.outDirMdl
  rootConfDirMdl = ii.rootConfDirMdl
  waterUse = ii.waterUse
  scen = ii.scen
  mdl = ii.mdl
  calendarDayStart = ii.calendarDayStart
  calendarDayEnd = ii.calendarDayEnd
  calendar = ii.calendar
  miscVars = ii.miscVars

  dtRestart = relativedelta(years = 1)
  dtReWarmUp = miscVars['dtReWarmUp']
  preliminaryRun = miscVars['preliminaryRun']
  py = '/eos/jeodpp/data/projects/CRITECH/miniconda3/envs/LISFLOOD/bin/python'
  lisfloodpy = '/eos/jeodpp/data/projects/CRITECH/ADAPTATION/src/git/lisflood/Lisflood/lisf1.py'
  lisfloodcmd = '{python} {lisflood}'.format(python=py, lisflood=lisfloodpy)

  wustr = 'waterUse' if waterUse else 'notWaterUse'
  modelTag = mdl + '_' + scen + '_' wustr
  lfManager = lfrm.lisfloodRunManager( initDirMdl, runDirMdl, tmpOutDirMdl, outDirMdl,
                      rootConfDirMdl, waterUse,
                      calendarDayStart, calendarDayEnd, calendar, lisfloodcmd, miscVars,
                      modelTag=modelTag,
                      dtRestart=dtRestart, dtReWarmUp=dtReWarmUp )
  if preliminaryRun:
    lfManager.setPreliminaryRun()
  print('starting the iterating run')
  lfManager.iterateRun()
  
  


if __name__ == '__main__':
  doLaunch()


