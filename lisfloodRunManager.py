import os, re, time, pickle, shutil, random
from dateutil.relativedelta import relativedelta
import netCDF4

import lfNcUtil


class lfCalendar:
  def __init__(self, calendarStart):
    self.calendarStart = calendarStart
    self.timeStep = relativedelta(days=1)
    self.units = 'days since ' + self.calendarStart.strftime('%Y-%m-%d %H:%M:%S')
    self.calendar = 'proleptic_gregorian'


class lisfloodRunManager:


  def __init__(self, initDir, runningDir, tmpOutDir, outDir, 
      meteoDir, rootConfDir, waterUseDir,
      calendarStart, calendarEnd, lisfloodcmd,
      sttsColdFileTmpl='', sttsWarmFileTmpl='',
      dtRestart=relativedelta(years=1), dtReWarmUp=relativedelta(months=1)):
    self.initDir = initDir
    self.meteoDir = meteoDir
    self.tmpOutDir = tmpOutDir
    self.runningDir = runningDir
    self.rootConfDir = rootConfDir
    self.waterUseDir = waterUseDir
    self.outDir = outDir
    self.calendar = lfCalendar(calendarStart)
    self.calendarEnd = calendarEnd
    self.lisfloodcmd = lisfloodcmd
    moddir = os.path.dirname(os.path.abspath(__file__))
    defaultSttsColdFileTmpl = os.path.join(moddir, 'template/settingsEurope_cold.xml')
    defaultSttsWarmFileTmpl = os.path.join(moddir, 'template/settingsEurope.xml')
    self.sttsColdFileTmpl = sttsColdFileTmpl if sttsColdFileTmpl != '' else defaultSttsColdFileTmpl
    self.sttsWarmFileTmpl = sttsWarmFileTmpl if sttsWarmFileTmpl != '' else defaultSttsWarmFileTmpl
    self.dtRestart = dtRestart
    self.dtReWarmUp = dtReWarmUp
    self.currentRunStartDateFile = os.path.join(runningDir, 'nextRunStart.pkl')
    self.currentRunStartDateFile_prior = os.path.join(runningDir, 'nextRunStart_prior.pkl')
    if os.path.isfile(self.currentRunStartDateFile):
      try:
        self.currentRunStartDate = pickle.load(open(self.currentRunStartDateFile))
      except:
        self.currentRunStartDate = pickle.load(open(self.currentRunStartDateFile_prior))
    else:
      self.currentRunStartDate = self.calendar.calendarStart
    self._printState()


  def _printState(self):
    print('lisfloodRunManager, setup:')
    attrs = dir(self)
    for att in attrs:
      if att[0] != '_':
        vv = getattr(self, att)
        if not callable(vv):
          print('  ' + att + ' = '+ str(vv))


  def _saveNextStartRunDate(self):
    if os.path.isfile(self.currentRunStartDateFile):
      shutil.copyfile(self.currentRunStartDateFile, self.currentRunStartDateFile_prior)
    pickle.dump(self.currentRunStartDate, open(self.currentRunStartDateFile, 'w'))


  def _raiseException(self, msg):
    raise Exception('Error running restart ' + self.currentRunStartDate.strftime('%Y%m%d%H') + ': ' + msg)


  def isColdStart(self):
    return self.currentRunStartDate == self.calendar.calendarStart


  def getSettingsTemplate(self):
    if self.isColdStart():
      return self.sttsColdFileTmpl
    else:
      return self.sttsWarmFileTmpl


  def compileTemplate(self):
    """
    compileTemplate: create workable settings.xml for lisflood.
    Markups handled in this function:
    @CALENDAR_START@
    @CALENDAR_CONVENTION@
    @STEP_START@
    @STEP_END@
    @STEP_INIT@
    @PATH_INIT@
    @PATH_OUT@
    @PATH_CONF_ROOT@
    """
    initDir = self.initDir
    outDir = self.tmpOutDir
    rootConfDir = self.rootConfDir
    waterUseDir = self.waterUseDir
    meteoDir = self.meteoDir
    clndr = self.calendar
    calendarStartStr = clndr.calendarStart.strftime('%m/%d/%Y')
    calendar = clndr.calendar
    startDate = self.currentRunStartDate - self.dtReWarmUp if not self.isColdStart() else clndr.calendarStart
    endDate = self.currentRunStartDate + self.dtRestart - self.calendar.timeStep
    
    stepInit = int(netCDF4.date2num(startDate, clndr.units, clndr.calendar))
    stepStart = stepInit + 1
    stepEnd = int(netCDF4.date2num(endDate, clndr.units, clndr.calendar) + 1)

    tmplFile = self.getSettingsTemplate()
    with open(tmplFile) as fl:
      tmplcntnt = ''.join(fl.readlines())
      fl.close()
    cntnt = tmplcntnt.replace('@CALENDAR_START@', calendarStartStr)
    cntnt = cntnt.replace('@CALENDAR_CONVENTION@', calendar)
    cntnt = cntnt.replace('@STEP_START@', str(stepStart))
    cntnt = cntnt.replace('@STEP_END@', str(stepEnd))
    cntnt = cntnt.replace('@STEP_INIT@', str(stepInit))
    cntnt = cntnt.replace('@PATH_INIT@', initDir)
    cntnt = cntnt.replace('@PATH_OUT@', outDir)
    cntnt = cntnt.replace('@PATH_CONF_ROOT@', rootConfDir)
    cntnt = cntnt.replace('@PATH_WATER_USE@', waterUseDir)
    cntnt = cntnt.replace('@PATH_METEO@', meteoDir)
    
    runningDir = self.runningDir
    if not os.path.isdir(runningDir):
      os.makedirs(runningDir)
    # adding a random tag on the name of the settings file, to have a unique name for a unique run
    settingsFile = os.path.join(runningDir, 'settings_'\
      + self.currentRunStartDate.strftime('%Y%m%d%H') + '_'\
      + str(random.randrange(1000000)).zfill(6) + '.xml')
    with open(settingsFile, 'w') as fl:
      fl.write(cntnt)
      fl.close()
    return settingsFile


  def extractInitConditions(self):
    print('    init extraction start:')
    if self.isColdStart():
      print('      this is the cold start. Skipping')
      return
    else:
      print('      removing previously generated init files')

      initDate = self.currentRunStartDate - self.dtReWarmUp - self.calendar.timeStep
      print('      init datetime: ' + str(initDate))
      try:
        shutil.rmtree(os.path.join(self.initDir, '*.nc'))
      except:
        pass
      priorRunStartDate = self.currentRunStartDate - self.dtRestart
      priorRunStartPattern = '(.*)_' + priorRunStartDate.strftime('%Y%m%d%H') + '\.nc'
      fls = [f for f in os.listdir(self.outDir) if re.match(priorRunStartPattern, f)]
      if fls == []:
        self._raiseException('no init files found')
      for f in fls:
        print('        slicing file ' + f)
        flpath = os.path.join(self.outDir, f)
        ptrn = re.sub(priorRunStartPattern, '\\1', f)
        initfl = ptrn + '.nc'
        initflpath = os.path.join(self.initDir, initfl)
        print('          prev out file: ' + flpath)
        print('          generated init file: ' + initflpath)
        lfNcUtil.lfNcSliceTime(flpath, initflpath, initDate, initDate)
      print('      ... init extraction complete')


  def storeOutput(self):
    """
    After each run, takes the output from tmpOutDir,
    cuts away the first part of simulation (given by dtReWarmUp), and
    store them to outDir with a name that includes the years.
    """
    print('   storing output to ' + self.outDir)
    currentRunDateStr = self.currentRunStartDate.strftime('%Y%m%d%H')
    fls = [f for f in os.listdir(self.tmpOutDir) if re.match('(.*)\.nc', f)]
    for f in fls:
      fpth = os.path.join(self.tmpOutDir, f)
      ofl = re.sub('\.nc', '_' + currentRunDateStr + '.nc', f)
      oflpth = os.path.join(self.outDir, ofl)
      print('      elaborating file ' + f)
      print('        writing ' + fpth)
      print('        to      ' + oflpth)
      lfNcUtil.lfNcSliceTime(fpth, oflpth, self.currentRunStartDate, None)
      os.remove(fpth)
    print('      output successfully stored')
      

  def executeNextRun(self):
    print('  elaborating ' + str(self.currentRunStartDate))
    self.extractInitConditions()
    settingsFile = self.compileTemplate()
    logfile = os.path.join(self.runningDir, 'run_' + self.currentRunStartDate.strftime('%Y%m%d%H') + '.log')
    lfcmd = '{lfcmd} {sttsfl} > {log} 2>&1'.format(lfcmd=self.lisfloodcmd, sttsfl=settingsFile, log=logfile)
    starttime = time.time()
    print('    launching lisflood: using command:')
    print('      ' + lfcmd)
    out = os.system(lfcmd)
    if out != 0:
      self._raiseException('Lisflood exited with non-zero status. Some error happened. Stopping')
    self.storeOutput()
    endtime = time.time()
    print('  done with ' + str(self.currentRunStartDate) 
        + ', elapsed time = ' + str(int(round(endtime - starttime))) + ' s')
    self.currentRunStartDate += self.dtRestart
    self._saveNextStartRunDate()
    return self.currentRunStartDate <= self.calendarEnd


  def iterateRun(self):
    starttime = time.time()
    while True:
      if not self.executeNextRun():
        return
    endtime = time.time()
    print('All done. Elapsed time = ' + str(int(round(endtime - starttime))) + ' s')
  
    
    


