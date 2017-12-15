"""
Markups handled in this script:
@CALENDAR_START@
@STEP_START@
@STEP_END@
@STEP_INIT@
@PATH_INIT@
@PATH_OUT@
"""
import os, re, time
from dateutil.relativedelta import relativedelta

class lisfloodRunManager:

  def __init__(self, initDir, tmpOutDir, outDir, calendarStart, 
      calendarEnd, lisfloodcmd,
      sttsColdFileTmpl='', sttsWarmFileTmpl='', 
      dtRestart=relativedelta(years=2), dtReWarmUp=relativedelta(months=3)):
    self.initDir = initDir
    self.tmpOutDir = tmpOutDir
    self.outDir = outDir
    self.calendarStart = calendarStart
    self.calendarEnd = calendarEnd
    self.lisfloodcmd = lisfloodcmd
    moddir = os.path.dirname(os.path.absdir(__file__))
    defaultSettingsColdFile = os.path.join(moddir, sttsColdFileTmpl)
    defaultSettingsWarmFile = os.path.join(moddir, sttsWarmFileTmpl)
    self.sttsColdFileTmpl = sttsColdFileTmpl if sttsColdFileTmpl != '' else defaultSettingsColdFile
    self.sttsWarmFileTmpl = settingsWarmFile if settingsWarmFile != '' else defaultSettingsWarmFile
    self.dtRestart = dtRestart
    self.dtReWarmUp = dtReWarmUp
    self.nextRunStart = self.getFirstStartDate()

  def getFirstStartDate(self):
    """
    Computes the first running date, for the first launch, or for the recovery of 
    crashed simulations. The date is estimated from calendarStart and from the content 
    of the directory outDir. If outDir is empty, then the first running date
    is equal to calendarStart. If in outDir there are saved results up to year y,
    the first running date is given by y-dtRestart-dtReWarmUp .
    The last saved data are reproduced, because there is the risk that the system crashed
    while saving the last results.
    """
    pass

  def getStartDate(self):
    """
    retruns the start date of the ith warm start
    """
    pass

  def isColdStart(self):
    return self.getStartDate() == self.calendarStart

  def getSettingsTemplate(self):
    if self.isColdStart():
      return self.sttsColdFileTmpl
    else:
      return self.sttsWarmFileTmpl

  def compileTemplate(self):
    tmpl = self.getSettingsTemplate()
    
    initDir = self.initDir
    outDir = self.tmpOutDir
    calendarStart = self.calendarStart
    startDate = ...
    stepEnd = ...
    stepInit = ...
    return settingsFile

  def extractInitConditions(self):
    if self.isColdStart():
      return
    else:
      pass

  def storeOutput(self):
    """
    After each run, takes the output from tmpOutDir,
    cuts away the first 3 months of simulation, and
    store them in outDir with a name that includes the years.
    """
    pass

  def executeNextRun(self):
    self.extractInitConditions()
    settingsFile = self.compileTemplate()
    lfcmd = '{lfcmd} {sttsfl}'.format(lfcmd=self.lisfloodcmd, sttsfl=settingsFile)
    starttime = time.time()
    out = os.system(lfcmd)
    if out != 0:
      something wrong
    endtime = time.time()
    print('elapsed time = ' str(int(round(endtime - starttime))) + ' s')
    self.storeOutput()
    return self.getStartDate() <= self.calendarEnd

  def iterateRun(self):
    while True:
      if not executeNextRun():
        return
  
    
    


