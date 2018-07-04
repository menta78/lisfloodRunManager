import os, re, glob

try:
  import numpy as np
except:
  print('numpy should be installed in python in order for this util to work')

try:
  import netCDF4
except:
  print('netCDF4 should be installed in python in order for this util to work')

from dateutil.relativedelta import relativedelta

projFlPattern='ww3\.(.*)_bulk6h\.nc'
histFlPattern='ww3\.([0-9]{6})\.nc'



class ncDataIterator:
  def __init__(self, ncDir, varName, flPattern, timeVarName='time', timeVarUnits='', outNcDir='', listFileMode='regexp'):
    self.ncDir = ncDir
    self.outNcDir = outNcDir if outNcDir != '' else ncDir
    self.varName = varName
    self.flPattern = flPattern
    self.timeVarName = timeVarName
    self.timeVarUnits = timeVarUnits
    self.outFilePrefix = ''
    self.verbose = True
    self.defaultMissingValue = 1E20
    self.listFileMode = listFileMode # can be regexp or wildcard


  def _print(self, lstr):
    if self.verbose:
      print(lstr)

  def _listFiles(self, ncDir, flPattern):
    if self.listFileMode == 'regexp':
      fls = [f for f in os.listdir(ncDir) if re.match(flPattern, f)]
    elif self.listFileMode == 'wildcard':
      cdir = os.getcwd()
      try:
        os.chdir(ncDir)
        fls = glob.glob(flPattern)
      finally:
        os.chdir(cdir)
    else:
      raise Exception('Supported listFileMode are regexp and wildcard')
    fls.sort()
    return fls


  def iterateByMonth(self):
    ncDir = self.ncDir
    outNcDir = self.outNcDir
    varName = self.varName
    flPattern = self.flPattern
    timeVarName = self.timeVarName
    timeVarUnits = self.timeVarUnits
    outFilePrefix = self.outFilePrefix

   #fls = [f for f in os.listdir(ncDir) if re.match(flPattern, f)]
   #fls.sort()
    fls = self._listFiles(ncDir, flPattern)
    yr, mnt = -1, -1
    nflname, nflpth = '', ''
    dtm, mtmIndxs = [], []
    flpth = ''

    def updateOutputFile():
      monthDtm = dtm[mtmIndxs]
      ds = netCDF4.Dataset(flpth)
      vrnc = ds.variables[varName]
      ndim = len(vrnc.shape)
      itm = vrnc.dimensions.index(timeVarName)
      iii = []
      for idim in range(ndim):
        ss = slice(min(mtmIndxs), max(mtmIndxs) + 1) if idim == itm else slice(None)
        iii.append(ss)
      monthVals = vrnc[iii]
      ds.close()
      ncUpdateFile(nflpth, varName, monthDtm, monthVals, timeVarName)

    for f in fls:
      if nflpth != '':
        updateOutputFile()
        mtmIndxs = []
      flpth = os.path.join(ncDir, f)
      ds = netCDF4.Dataset(flpth)
      timenc = ds.variables[timeVarName]
      try:
        clndr = timenc.calendar
      except:
        clndr = 'standard'
      dtm = netCDF4.num2date(timenc[:], timenc.units, clndr)
      vrvals = ds.variables[varName][:]
      ds.close()
      for dt, idt in zip(dtm, range(len(dtm))):
        if dt.year == yr and dt.month == mnt:
          mtmIndxs.append(idt)
        else:
          if nflpth != '':
            # computing update slice
            if len(mtmIndxs) > 0:
              updateOutputFile()
            yield yr, mnt, nflpth
          mtmIndxs = [idt]
          yr, mnt = dt.year, dt.month
          nflname = outFilePrefix + str(yr).zfill(4) + str(mnt).zfill(2) + '.nc'
          nflpth = os.path.join(outNcDir, nflname)
          self._print('      generating file ' + nflpth + ' ...')
          ncCloneFileStructure(flpth, nflpth, varName, timeVarName, timeVarUnits, self.defaultMissingValue)
    
    if nflpth != '':
      # computing update slice
      if len(mtmIndxs) > 0:
        updateOutputFile()
      yield yr, mnt, nflpth



  def iterateByYear(self, offsetTimeDelta=None, timeStep=relativedelta(hours=6)):
    ncDir = self.ncDir
    outNcDir = self.outNcDir
    varName = self.varName
    flPattern = self.flPattern
    timeVarName = self.timeVarName
    timeVarUnits = self.timeVarUnits
    outFilePrefix = self.outFilePrefix

    offsetTimeDelta = relativedelta(days=0) if offsetTimeDelta is None else offsetTimeDelta

   #fls = [f for f in os.listdir(ncDir) if re.match(flPattern, f)]
   #fls.sort()
    fls = self._listFiles(ncDir, flPattern)
    yr = -1
    nflname, nflpth = '', ''
    dtm, mtmIndxs = [], []
    flpth = ''

    def updateOutputFile():
      monthDtm = dtm[mtmIndxs]
      ds = netCDF4.Dataset(flpth)
      vrnc = ds.variables[varName]
      ndim = len(vrnc.shape)
      itm = vrnc.dimensions.index(timeVarName)
      iiiNc = []
      iiiVec = []
      for idim in range(ndim):
        ss = slice(min(mtmIndxs), max(mtmIndxs) + 1) if idim == itm else slice(None)
        iiiNc.append(ss)
        ss = mtmIndxs if idim == itm else slice(None)
        iiiVec.append(ss)
      monthVals = vrnc[iiiNc]
      if not timeStep is None:
        monthVals = monthVals[iiiVec]
      ds.close()
      ncUpdateFile(nflpth, varName, monthDtm, monthVals, timeVarName)

    for f in fls:
      if nflpth != '':
        updateOutputFile()
        mtmIndxs = []
      flpth = os.path.join(ncDir, f)
      ds = netCDF4.Dataset(flpth)
      timenc = ds.variables[timeVarName]
      try:
        clndr = timenc.calendar
      except:
        clndr = 'standard'
      dtm = netCDF4.num2date(timenc[:], timenc.units, clndr)
      dtmShift = dtm + offsetTimeDelta
      vrvals = ds.variables[varName][:]
      ds.close()
      for dt, idt in zip(dtmShift, range(len(dtm))):
        dtAct = dtm[idt]
        if dt.year == yr:
          if timeStep is None or (dtAct >= prevDtAct + timeStep):
            mtmIndxs.append(idt)
            prevDtAct = dtAct - relativedelta(seconds=1)
          else:
            print('     skipping time step ' + str(dtAct) + ': too close to previous time step')
        else:
          if nflpth != '':
            # computing update slice
            if len(mtmIndxs) > 0:
              updateOutputFile()
            yield yr, nflpth
          mtmIndxs = [idt]
          prevDtAct = dtAct - relativedelta(seconds=1)
          yr = dt.year
          nflname = outFilePrefix + str(yr).zfill(4) + '.nc'
          nflpth = os.path.join(outNcDir, nflname)
          self._print('      generating file ' + nflpth + ' ...')
          ncCloneFileStructure(flpth, nflpth, varName, timeVarName, timeVarUnits)
    
    if nflpth != '':
      # computing update slice
      if len(mtmIndxs) > 0:
        updateOutputFile()
      yield yr, nflpth



  def generateSingleOutFile(self, outNcFile):
    ncDir = self.ncDir
    outNcDir = self.outNcDir
    varName = self.varName
    flPattern = self.flPattern
    timeVarName = self.timeVarName
    timeVarUnits = self.timeVarUnits
    outFilePrefix = self.outFilePrefix

   #fls = [f for f in os.listdir(ncDir) if re.match(flPattern, f)]
   #fls.sort()
    fls = self._listFiles(ncDir, flPattern)

    if os.path.isfile(outNcFile):
      os.remove(outNcFile)

    print('  merging all the files')
    for f in fls:
      flpth = os.path.join(ncDir, f)
      print('    merging file ' + flpth)
      ds = netCDF4.Dataset(flpth)
      timenc = ds.variables[timeVarName]
      try:
        clndr = timenc.calendar
      except:
        clndr = 'standard'
      dtm = netCDF4.num2date(timenc[:], timenc.units, clndr)
      vrvals = ds.variables[varName][:]
      ds.close()

      if not os.path.isfile(outNcFile):
        ncCloneFileStructure(flpth, outNcFile, varName, timeVarName, timeVarUnits, self.defaultMissingValue)
      ncUpdateFile(outNcFile, varName, dtm, vrvals, timeVarName)
    print('  ... done')
    
    

          
          
  
      

def ncCloneFileStructure(inputFilePath, outputFilePath, varName, timeVarName='time', timeVarUnits='', defaultMissingValue=1E20):
  ids = netCDF4.Dataset(inputFilePath)
  ods = netCDF4.Dataset(outputFilePath, 'w')

  try:

    #Copying attributes
    for k in ids.ncattrs():
      att = ids.getncattr(k)
      ods.setncattr(k, att)

    #Copying dimensions
    for dname, dm in ids.dimensions.iteritems():
      ods.createDimension(dname, len(dm) if (not dm.isunlimited()) and (dname!=timeVarName) else None)
      if not ids.variables.has_key(dname):
        continue
      vrbl = ids.variables[dname]
      ovrbl = ods.createVariable(dname, vrbl.datatype, vrbl.dimensions)
      ovrbl.setncatts({k: vrbl.getncattr(k) for k in vrbl.ncattrs()})
      if dname == timeVarName:
        try:
          clndr = vrbl.calendar
        except:
          clndr = 'gregorian'
        ovrbl.calendar = clndr
        if timeVarUnits != '':
          ovrbl.units = timeVarUnits
      else:
        ovrbl[:] = vrbl[:]
    vrbl = ids.variables[varName]
    fillValue = vrbl._FillValue if '_FillValue' in vrbl.ncattrs() else defaultMissingValue
    ovrbl = ods.createVariable(vrbl.name, vrbl.datatype, vrbl.dimensions, fill_value=fillValue)
    ovrbl.setncatts({k: vrbl.getncattr(k) for k in vrbl.ncattrs()})
    if (not 'missing_value' in ovrbl.ncattrs()): 
      ovrbl.setncattr('missing_value', fillValue)
  finally:
    ids.close()
    ods.close()

  


def ncUpdateFile(flpth, varName, datetimes, values, timeVarName='time'):
  ds = netCDF4.Dataset(flpth, 'r+')
  try:
    tmnc = ds.variables[timeVarName]
    try:
      clndr = tmnc.calendar
    except:
      clndr = 'standard'
    tms = netCDF4.date2num(datetimes, tmnc.units, clndr)
    l0 = len(tmnc)
    l1 = len(tms)
    tmnc[l0:l0 + l1] = tms
  
    vrnc = ds.variables[varName]
    missingVal = vrnc.missing_value
    values[np.isnan(values)] = missingVal
    #computing update array slice
    itm = vrnc.dimensions.index(timeVarName)
    ndim = len(vrnc.shape)
    indx = []
    for idim in range(ndim):
      ss = slice(l0, l0 + l1) if idim == itm else slice(None)
      indx.append(ss)
    vrnc[indx] = values
  finally:
    ds.close()
    

