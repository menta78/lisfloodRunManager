import netCDF4
import numpy as np
import os


def loadOutletRetLevFromNc(ncEvaMapPth, returnPeriod, ncOutletPth=''):
  if ncOutletPth == '':
    ncOutletPth = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outlets.nc')

  outletDs = netCDF4.Dataset(ncOutletPth)
  outlets = outletDs.variables['outlets'][:]
  oirow, oicol = np.where(np.logical_not(outlets.mask))

  disDs = netCDF4.Dataset(ncEvaMapPth)
  year = disDs.variables['year'][:]
  retper = disDs.variables['return_period'][:]
  rpIndx = np.where(retper == returnPeriod)[0][0]
  rl = disDs.variables['rl']

  outPtIds = []
  timeSrs = []
  npts = len(oirow)
  for irow, icol in zip(oirow, oicol):
    
    outPtIdAct = outlets[irow, icol]
    outPtIds.append(outPtIdAct)
    timeSrsAct = rl[rpIndx, :, icol, irow]
    timeSrs.append(timeSrsAct)
  outPtIds = np.array(outPtIds)
 #timeSrsWithNan = np.array(timeSrs).transpose()
 #timeSrs = timeSrsWithNan
 #timeSrs[np.isnan(timeSrs)] = 1e31

  outPtIdsFinal = np.arange(max(outPtIds)) + 1
  timeSrs = np.array(timeSrs)
  timeSrsFinal = np.ones([outPtIdsFinal.shape[0], timeSrs.shape[1]])*np.nan
  outPtIndxs = outPtIds - 1
  timeSrsFinal[outPtIndxs, :] = timeSrs
  return year, outPtIdsFinal, timeSrsFinal



def loadAllRetLevFromNc(ncEvaMapPth, returnPeriod):
  disDs = netCDF4.Dataset(ncEvaMapPth)
  year = disDs.variables['year'][:]
  retper = disDs.variables['return_period'][:]
  rpIndx = np.where(retper == returnPeriod)[0][0]
  rl = np.squeeze(disDs.variables['rl'][rpIndx, :, :, :])

  return year, rl
