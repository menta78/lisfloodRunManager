import re, os
import netCDF4
import numpy as np


def ncCloneFileStructure(inputFilePath, outputFilePath, timeVarName='time', timeVarUnits='', calendar='', defaultMissingValue=1E10, complevel=4):
  if os.path.isfile(outputFilePath):
    os.remove(outputFilePath)

  zlib = complevel > 1
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
      ovrbl = ods.createVariable(dname, vrbl.datatype, vrbl.dimensions, zlib=zlib, complevel=complevel)
      ovrbl.setncatts({k: vrbl.getncattr(k) for k in vrbl.ncattrs()})
      if dname == timeVarName:
        if calendar != '':
          clndr = calendar
        else:
          try:
            clndr = vrbl.calendar
          except:
            clndr = 'gregorian'
        ovrbl.calendar = clndr
        if timeVarUnits != '':
          ovrbl.units = timeVarUnits
      else:
        ovrbl[:] = vrbl[:]
    for varName in ids.variables:
      if varName in ods.variables:
        continue
      vrbl = ids.variables[varName]
      fillValue = vrbl._FillValue if '_FillValue' in vrbl.ncattrs() else defaultMissingValue
      if re.match('(.*)float(.*)', vrbl.datatype.name):
        ovrbl = ods.createVariable(vrbl.name, vrbl.datatype, vrbl.dimensions, fill_value=fillValue, 
                                   zlib=zlib, complevel=complevel)
      else:
        ovrbl = ods.createVariable(vrbl.name, vrbl.datatype, vrbl.dimensions)
      ovrbl.setncatts({k: vrbl.getncattr(k) for k in vrbl.ncattrs()})
      if (not 'missing_value' in ovrbl.ncattrs()):
        ovrbl.setncattr('missing_value', fillValue)
  finally:
    ids.close()
    ods.close()


def lfNcSliceTime(inputFilePath, outputFilePath, startTime, endTime, timeVarName='time', complevel=4):

  # getting time limits
  ids = netCDF4.Dataset(inputFilePath)
  intmnc = ids.variables[timeVarName]
  tmunits = intmnc.units
  try:
    clndr = intmnc.calendar
  except:
    clndr = 'standard'
  intmnum = intmnc[:]
  inTm = netCDF4.num2date(intmnum, tmunits, clndr)
  stTmNum = netCDF4.date2num(startTime, tmunits, clndr)
  stTmNumIndx = np.where(intmnum == stTmNum)[0][0]
  if not endTime is None:
    endTmNum = netCDF4.date2num(endTime, tmunits, clndr)
    endTmNumIndx = np.where(intmnum == endTmNum)[0][0] + 1
  else:
    endTmNumIndx = -1
  if endTmNumIndx >= len(intmnum):
    endTmNumIndx = -1
  ids.close()
  tmslice = slice(stTmNumIndx, endTmNumIndx) if endTmNumIndx != -1 else slice(stTmNumIndx, None)

  #copying file structure
  ncCloneFileStructure(inputFilePath, outputFilePath, timeVarName, tmunits, clndr, complevel=complevel)

  #copying values
  ids = netCDF4.Dataset(inputFilePath)
  ods = netCDF4.Dataset(outputFilePath, 'r+')
  dims = ods.dimensions
  for varName in ids.variables:
    if varName == timeVarName:
      ivrbl = ids.variables[varName]
      ovrbl = ods.variables[varName]
      tmunits = ovrbl.units
      try:
        clndr = ovrbl.calendar
      except:
        clndr = 'standard'
      otmnum = netCDF4.date2num(inTm, tmunits, clndr)
      ovrbl[:] = otmnum[tmslice]
    if varName in dims:
      continue
    ivrbl = ids.variables[varName]
    ovrbl = ods.variables[varName]
    ovdims = ovrbl.dimensions
    if timeVarName in ovdims:
      timeDimIndx = ovdims.index(timeVarName)
      indx = []
      for idim in range(len(ovdims)):
        ss = tmslice if idim==timeDimIndx else slice(None)
        indx.append(ss)
      ovrbl[:] = ivrbl[indx]
    else:
      try:
        ovrbl[:] = ivrbl[:]
      except:
        pass
  ids.close()
  ods.close()
  
  
  

  
