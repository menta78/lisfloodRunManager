import numpy as np
import os, netCDF4
from scipy.interpolate import interp1d

from getWarmingLevels import getWarmingLevels


def loadWlVsScenChange(ncDir='/ClimateRun4/multi-hazard/eva', bslnYear=1995, warmingLev=2, retPer=100):
  flpattern = 'projection_dis_{scen}_{mdl}_wuChang_statistics.nc'

  wlyR8 = getWarmingLevels('rcp85', warmingLev)
  wlyR4 = getWarmingLevels('rcp45', warmingLev)

  models = wlyR8.keys()

  rl_r4 = []
  rl_r8 = [] 
  for mdl, imdl in zip(models, range(len(models))):
    print('model ' + mdl)
    flr8 = flpattern.format(scen='rcp85', mdl=mdl)
    flr8pth = os.path.join(ncDir, flr8)
    flr4 = flpattern.format(scen='rcp45', mdl=mdl)
    flr4pth = os.path.join(ncDir, flr4)

    r8year = wlyR8[mdl]
    r8yearInf = int(np.floor(r8year/float(5))*5)
    print('  rcp85 w.l. year: ' + str(r8year))
    r4year = wlyR4[mdl]
    r4yearInf = int(np.floor(r4year/float(5))*5)
    print('  rcp45 w.l. year: ' + str(r4year))

    print('  loading file ' + flr8pth)
    ds = netCDF4.Dataset(flr8pth)
    retper_ = ds.variables['return_period'][:]
    rpIndx = np.where(retper_==retPer)[0][0]
    year_ = ds.variables['year'][:]
    yIndxBsln = np.where(year_ == bslnYear)[0][0]
    rlBslnR8 = ds.variables['rl'][rpIndx, yIndxBsln, :, :]
    yIndx = np.where(year_==r8yearInf)[0][0]
    rlR8_ = ds.variables['rl'][rpIndx, yIndx:yIndx+2, :, :]
    ds.close()
    rlR8 = interp1d(year_[yIndx:yIndx+2], rlR8_, axis=0)(r8year)
    r8RelChng = (rlR8-rlBslnR8)/rlBslnR8

    print('  loading file ' + flr4pth)
    ds = netCDF4.Dataset(flr4pth)
    rlBslnR4 = ds.variables['rl'][rpIndx, yIndxBsln, :, :]
    yIndx = np.where(year_==r4yearInf)[0][0]
    rlR4_ = ds.variables['rl'][rpIndx, yIndx:yIndx+2, :, :]
    ds.close()
    rlR4 = interp1d(year_[yIndx:yIndx+2], rlR4_, axis=0)(r4year)
    r4RelChng = (rlR4-rlBslnR4)/rlBslnR4

    rl_r8.append(r8RelChng)
    rl_r4.append(r4RelChng)

  rl_r8 = np.array(rl_r8)
  rl_r4 = np.array(rl_r4)

  relChngDiff = np.nanmean(rl_r8-rl_r4, 0)

  return relChngDiff, np.nanmean(rl_r8, 0), np.nanmean(rl_r4, 0), rl_r8, rl_r4


def getGrossEnsembleAtYear(ryear, ncDir='/ClimateRun4/multi-hazard/eva', bslnYear=1995, retPer=100):
  flpattern = 'projection_dis_{scen}_{mdl}_wuChang_statistics.nc'

  wlyR8 = getWarmingLevels('rcp85', 2.0)
 #wlyR4 = getWarmingLevels('rcp45', warmingLev)

  models = wlyR8.keys()

  rl_all = []
  for mdl, imdl in zip(models, range(len(models))):
    print('model ' + mdl)
    flr8 = flpattern.format(scen='rcp85', mdl=mdl)
    flr8pth = os.path.join(ncDir, flr8)
    flr4 = flpattern.format(scen='rcp45', mdl=mdl)
    flr4pth = os.path.join(ncDir, flr4)

   #r8year = wlyR8[mdl] + wlOffset
   #r8yearInf = int(np.floor(r8year/float(5))*5)
   #print('  rcp85 w.l. year: ' + str(r8year))
   #r4year = wlyR4[mdl] + wlOffset
   #r4yearInf = int(np.floor(r4year/float(5))*5)
   #print('  rcp45 w.l. year: ' + str(r4year))
    
    ryearInf = int(np.floor(ryear/float(5))*5)

    print('  loading file ' + flr8pth)
    ds = netCDF4.Dataset(flr8pth)
    retper_ = ds.variables['return_period'][:]
    rpIndx = np.where(retper_==retPer)[0][0]
    year_ = ds.variables['year'][:]
    yIndxBsln = np.where(year_ == bslnYear)[0][0]
    rlBslnR8 = ds.variables['rl'][rpIndx, yIndxBsln, :, :]
   #yIndx = np.where(year_==r8yearInf)[0][0]
    yIndx = np.where(year_==ryearInf)[0][0]
    rlR8_ = ds.variables['rl'][rpIndx, yIndx:yIndx+2, :, :]
    ds.close()
   #rlR8 = interp1d(year_[yIndx:yIndx+2], rlR8_, axis=0)(r8year)
    rlR8 = interp1d(year_[yIndx:yIndx+2], rlR8_, axis=0)(ryear)
    r8RelChng = (rlR8-rlBslnR8)/rlBslnR8

    print('  loading file ' + flr4pth)
    ds = netCDF4.Dataset(flr4pth)
    rlBslnR4 = ds.variables['rl'][rpIndx, yIndxBsln, :, :]
   #yIndx = np.where(year_==r4yearInf)[0][0]
    yIndx = np.where(year_==ryearInf)[0][0]
    rlR4_ = ds.variables['rl'][rpIndx, yIndx:yIndx+2, :, :]
    ds.close()
   #rlR4 = interp1d(year_[yIndx:yIndx+2], rlR4_, axis=0)(r4year)
    rlR4 = interp1d(year_[yIndx:yIndx+2], rlR4_, axis=0)(ryear)
    r4RelChng = (rlR4-rlBslnR4)/rlBslnR4

    rl_all.append(r8RelChng)
    rl_all.append(r4RelChng)
   #if imdl == 1:
   #  break
    
  rl_all = np.array(rl_all)

  ensembleRelChngAll = np.nanmean(rl_all, 0)

  return ensembleRelChngAll


def getRcpEnsembleAtYear(ryear, ncDir='/ClimateRun4/multi-hazard/eva', bslnYear=1995, retPer=100, scen='rcp85'):
  flpattern = 'projection_dis_{scen}_{mdl}_wuChang_statistics.nc'

  wlyR = getWarmingLevels(scen, 2.0)
 #wlyR4 = getWarmingLevels('rcp45', warmingLev)

  models = wlyR.keys()

  rl = []
  for mdl, imdl in zip(models, range(len(models))):
    print('model ' + mdl)
    flr = flpattern.format(scen=scen, mdl=mdl)
    flrpth = os.path.join(ncDir, flr8)
    
    ryearInf = int(np.floor(ryear/float(5))*5)

    print('  loading file ' + flrpth)
    ds = netCDF4.Dataset(flrpth)
    retper_ = ds.variables['return_period'][:]
    rpIndx = np.where(retper_==retPer)[0][0]
    year_ = ds.variables['year'][:]
    yIndxBsln = np.where(year_ == bslnYear)[0][0]
    rlBslnR = ds.variables['rl'][rpIndx, yIndxBsln, :, :]
    yIndx = np.where(year_==ryearInf)[0][0]
    rlR_ = ds.variables['rl'][rpIndx, yIndx:yIndx+2, :, :]
    ds.close()
   #rlR8 = interp1d(year_[yIndx:yIndx+2], rlR8_, axis=0)(r8year)
    rlR = interp1d(year_[yIndx:yIndx+2], rlR_, axis=0)(ryear)
    rRelChng = (rlR-rlBslnR)/rlBslnR
    rl.append(r8RelChng)
    rl.append(r4RelChng)
    
  rl = np.array(rl)

  ensembleRelChng = np.nanmean(rl, 0)

  return ensembleRelChng

  

