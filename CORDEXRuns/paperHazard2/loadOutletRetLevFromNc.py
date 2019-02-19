import netCDF4
import numpy as np
import os
from matplotlib import path


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



def loadAllRetLevFromNc(ncEvaMapPth, returnPeriod, maskOutAfricaAndTurkey=True):
  disDs = netCDF4.Dataset(ncEvaMapPth)
  year = disDs.variables['year'][:]
  retper = disDs.variables['return_period'][:]
  rpIndx = np.where(retper == returnPeriod)[0][0]
  rl = np.squeeze(disDs.variables['rl'][rpIndx, :, :, :])

  if maskOutAfricaAndTurkey:
    msk, lon, lat = getAfricaAndTurkeyMask()
    msk = np.tile(msk.transpose(), [rl.shape[0], 1, 1])
    rl[~msk] = np.nan

  return year, rl



def getAfricaAndTurkeyMask(lon=None, lat=None):
  if lon is None:
    ds = netCDF4.Dataset('lonlat.nc')
    lon = ds.variables['lon'][:]
    lat = ds.variables['lat'][:]
  p = [
     [-13, 35.944728],
     [-1, 35.944728],
     [-1, 37.4],
     [11.5, 37.5],
     [12, 34.5],
     [34.8, 33.5],
     [35.34, 36.123],
     [27.59, 35.93],
     [25.89, 39.98],
     [36.66, 43.5],
     [41.34, 50.],
     [53.93, 48.77],
     [40.28, 25.24],
     [-13.27, 30]
     ]
  plg = path.Path(p) 
  mskflt = ~plg.contains_points(np.array([lon.flatten(), lat.flatten()]).transpose())
  msk = mskflt.reshape(lon.shape)
  return msk, lon, lat
  

