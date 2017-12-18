import os, re, time, pickle, shutil
from dateutil.relativedelta import relativedelta

import lfNcUtil


class lfCalendar:
  def __init__(self, calendarStart):
    self.calendarStart = calendarStart
    self.timeStep = relativedelta(days=1)
    self.units = 'days since ' + self.calendarStart.strftime('%Y-%m-%d %H:%M:%S')
    self.calendar = 'gregorian'


class lisfloodRunManager:


  def __init__(self, initDir, runningDir, tmpOutDir, outDir, calendarStart, 
      calendarEnd, lisfloodcmd,
      sttsColdFileTmpl='', sttsWarmFileTmpl='',
      dtRestart=relativedelta(years=1), dtReWarmUp=relativedelta(months=1)):
    self.initDir = initDir
    self.tmpOutDir = tmpOutDir
    self.runningDir = runningDir
    self.outDir = outDir
    self.calendar = lfCalendar(calendarStart)
    self.calendarEnd = calendarEnd
    self.lisfloodcmd = lisfloodcmd
    moddir = os.path.dirname(os.path.absdir(__file__))
    defaultSettingsColdFile = os.path.join(moddir, sttsColdFileTmpl)
    defaultSettingsWarmFile = os.path.join(moddir, sttsWarmFileTmpl)
    self.sttsColdFileTmpl = sttsColdFileTmpl if sttsColdFileTmpl != '' else defaultSettingsColdFile
    self.sttsWarmFileTmpl = settingsWarmFile if settingsWarmFile != '' else defaultSettingsWarmFile
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


  def _saveNextStartRunDate(self):
    if os.path.isfile(self.currentRunStartDate):
      shutil.copyfile(self.currentRunStartDate, self.currentRunStartDateFile_prior)
    pickle.dump(open(elf.currentRunStartDate, 'w'), self.currentRunStartDate)


  def _raiseException(self, msg):
    raise Exception('Error running restart ' + self.currentRunStartDate.strftime('%Y%m%d%H') + ': ' + msg)


  def isColdStart(self):
    return self.getStartDate() == self.calendar.calendarStart


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
    @STEP_START@
    @STEP_END@
    @STEP_INIT@
    @PATH_INIT@
    @PATH_OUT@
    """
    tmpl = self.getSettingsTemplate()
    
    initDir = self.initDir
    outDir = self.tmpOutDir
    clndr = self.calendar
    calendarStartStr = clndr.calendarStart.strftime('%m/%d/%Y')
    startDate = self.currentRunStartDate - self.dtReWarmUp if not self.isColdStart() else clndr.calendarStart
    endDate = self.currentRunStartDate + self.dtRestart - self.calendar.timeStep
    
    stepInit = netCDF4.date2num(startDate, clndr.units, clndr.calendar)
    stepStart = stepInit + 1
    stepEnd = netCDF4.date2num(endDate, clndr.units, clndr.calendar) + 1

    tmplFile = self.getSettingsTemplate()
    with open(tmplFile) as fl:
      tmplcntnt = ''.join(fl.readlines())
      fl.close()
    cntnt = tmplcntnt.replace('@CALENDAR_START@', calendarStartStr)
    cntnt = cntnt.replace('@STEP_START@', str(stepStart))
    cntnt = cntnt.replace('@STEP_END@', str(stepEnd))
    cntnt = cntnt.replace('@STEP_INIT@', str(stepInit))
    cntnt = cntnt.replace('@PATH_INIT@', initDir)
    cntnt = cntnt.replace('@PATH_OUT', outDir)
    
    runningDir = self.runningDir
    if not os.path.isfile(runningDir):
      os.makedirs(runningDir)
    # adding a random tag on the name of the settings file, to have a unique name for a unique run
    settingsFile = os.path.join(runningDir, 'settings_' + str(random.randrange(1000000)).zfill(6) + '.xml')
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
        shutil.rmtree(os.path.join(self.initDir, '.nc'))
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
        lfNcUtil.lfNcSliceTime(flpath, initfl, initDate, initDate)
      print('      ... init extraction complete')


  def storeOutput(self):
    """
    After each run, takes the output from tmpOutDir,
    cuts away the first part of simulation (given by dtReWarmUp), and
    store them to outDir with a name that includes the years.
    """
    print('   storing output to ' + self.outDir)
    currentRunDateStr = self.currentRunStartDate.strftime('%Y%m%d%H')
    fls = [f for f in os.listdir(self.tmpOutDir) if re.match('(.*)\.nc', f)
    for f in fls:
      fpth = os.path.join(self.tmpOutDir, f)
      ofl = re.sub('\.nc', '_' + currentRunStartDate + '.nc', f)
      oflpth = os.path.join(self.outDir, ofl)
      print('      elaborating file ' + f)
      print('        writing ' + fpth)
      print('        to      ' + oflpth)
      lfNcUtil.lfNcSliceTime(fpth, oflpth, self.currentRunStartDate, None)
    print('      output successfully stored')
      

  def executeNextRun(self):
    print('  elaborating ' + str(self.currentRunStartDate))
    self.extractInitConditions()
    settingsFile = self.compileTemplate()
    logfile = os.path.join(self.runningDir, 'run_' + self.currentRunStartDate.strftime('%Y%m%d%H') + '.log')
    lfcmd = '{lfcmd} {sttsfl} > {log} 2>&1'.format(lfcmd=self.lisfloodcmd, sttsfl=settingsFile, log=logfile)
    starttime = time.time()
    out = os.system(lfcmd)
    if out != 0:
      self._raiseException('Lisflood exited with non-zero status. Some error happened. Stopping')
    endtime = time.time()
    self.storeOutput()
    print('  done with ' + str(self.currentRunStartDate) + ', elapsed time = ' str(int(round(endtime - starttime))) + ' s')
    self.currentRunStartDate += self.dtRestart
    self._saveNextStartRunDate()
    return self.getStartDate() <= self.calendarEnd


  def iterateRun(self):
    while True:
      if not executeNextRun():
        return
  
    
    


