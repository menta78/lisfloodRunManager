import numpy as np
import os, netCDF4
from scipy.interpolate import interp1d

from getWarmingLevels import getWarmingLevels
from loadOutletRetLevFromNc import getAfricaAndTurkeyMask



def loadWlVsScenChange(ncDir='/ClimateRun4/multi-hazard/eva', bslnYear=1995, warmingLev=2, retPer=100, threshold=0, rlVarName='rl'):
  # computes the mean relative change
  flpattern = 'projection_dis_{scen}_{mdl}_wuChang_statistics.nc'

  wlyR8 = getWarmingLevels('rcp85', warmingLev)
  wlyR4 = getWarmingLevels('rcp45', warmingLev)

  dsuparea = netCDF4.Dataset('upArea.nc')
  upArea = dsuparea.variables['upArea'][:].transpose()
  dsuparea.close()

  models = wlyR8.keys()
  # menta
 #models = [models[0], models[1]]
  tamask, _, _ = getAfricaAndTurkeyMask()
  tamask = tamask.transpose()

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
    rlBslnR8 = ds.variables[rlVarName][rpIndx, yIndxBsln, :, :]
    yIndx = np.where(year_==r8yearInf)[0][0]
    rlR8_ = ds.variables[rlVarName][rpIndx, yIndx:yIndx+2, :, :]
    ds.close()
    rlR8 = interp1d(year_[yIndx:yIndx+2], rlR8_, axis=0)(r8year)
    r8RelChng = (rlR8-rlBslnR8)/rlBslnR8
    if threshold > 0:
      cnd = rlBslnR8 < threshold
      r8RelChng[cnd] = np.nan
     #r8RelChng[r8RelChng < -.15] = np.nan

    print('  loading file ' + flr4pth)
    ds = netCDF4.Dataset(flr4pth)
   #rlBslnR4 = ds.variables[rlVarName][rpIndx, yIndxBsln, :, :]
    rlBslnR4 = rlBslnR8
    yIndx = np.where(year_==r4yearInf)[0][0]
    rlR4_ = ds.variables[rlVarName][rpIndx, yIndx:yIndx+2, :, :]
    ds.close()
    rlR4 = interp1d(year_[yIndx:yIndx+2], rlR4_, axis=0)(r4year)
    r4RelChng = (rlR4-rlBslnR4)/rlBslnR4
    if threshold > 0:
      cnd = rlBslnR4 < threshold
      r4RelChng[cnd] = np.nan
     #r4RelChng[r4RelChng < -.15] = np.nan

    r8RelChng[upArea < 1e9] = np.nan
    r4RelChng[upArea < 1e9] = np.nan

    r8RelChng[~tamask] = np.nan
    r4RelChng[~tamask] = np.nan

    rl_r8.append(r8RelChng)
    rl_r4.append(r4RelChng)

  rl_r8 = np.array(rl_r8)
  rl_r4 = np.array(rl_r4)

  relChngDiff = np.nanmean(rl_r8-rl_r4, 0)
  relChngDiff[~tamask] = np.nan

  return relChngDiff, np.nanmean(rl_r8, 0), np.nanmean(rl_r4, 0), rl_r8, rl_r4



def loadWlVsScenChange2(ncDir='/ClimateRun4/multi-hazard/eva', bslnYear=1995, warmingLev=2, retPer=100, threshold=0, rlVarName='rl'):
  # computes the relative change of the ensemble
  flpattern = 'projection_dis_{scen}_{mdl}_wuChang_statistics.nc'

  wlyR8 = getWarmingLevels('rcp85', warmingLev)
  wlyR4 = getWarmingLevels('rcp45', warmingLev)

  dsuparea = netCDF4.Dataset('upArea.nc')
  upArea = dsuparea.variables['upArea'][:].transpose()
  dsuparea.close()

  models = wlyR8.keys()
  # menta
 #models = [models[0], models[1]]
  tamask, _, _ = getAfricaAndTurkeyMask()
  tamask = tamask.transpose()

  rl_bsln = []
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
    rlBslnR8 = ds.variables[rlVarName][rpIndx, yIndxBsln, :, :]
    yIndx = np.where(year_==r8yearInf)[0][0]
    rlR8_ = ds.variables[rlVarName][rpIndx, yIndx:yIndx+2, :, :]
    ds.close()
    rlR8 = interp1d(year_[yIndx:yIndx+2], rlR8_, axis=0)(r8year)

    print('  loading file ' + flr4pth)
    ds = netCDF4.Dataset(flr4pth)
    yIndx = np.where(year_==r4yearInf)[0][0]
    rlR4_ = ds.variables[rlVarName][rpIndx, yIndx:yIndx+2, :, :]
    ds.close()
    rlR4 = interp1d(year_[yIndx:yIndx+2], rlR4_, axis=0)(r4year)

    rlR8[upArea < 1e9] = np.nan
    rlR4[upArea < 1e9] = np.nan

    rlR8[~tamask] = np.nan
    rlR4[~tamask] = np.nan

    rl_r8.append(rlR8)
    rl_r4.append(rlR4)
    rl_bsln.append(rlBslnR8)

  rl_r8 = np.array(rl_r8)
  rl_r4 = np.array(rl_r4)
  rl_bsln = np.array(rl_bsln)

  mnbsln = np.nanmean(rl_bsln, 0)
  mnbsln[mnbsln < threshold] = np.nan
  rc_r8 = (np.nanmean(rl_r8, 0) - mnbsln)/mnbsln
  rc_r4 = (np.nanmean(rl_r4, 0) - mnbsln)/mnbsln

  relChngDiff = rc_r8-rc_r4
  relChngDiff[~tamask] = np.nan

  nmdl = rl_bsln.shape[0]
  std_r8 = np.std(rl_r8 - rl_bsln, 0)/np.sqrt(np.sum(rl_bsln**2., 0)/nmdl)
  std_r4 = np.std(rl_r4 - rl_bsln, 0)/np.sqrt(np.sum(rl_bsln**2., 0)/nmdl)
  std_diff = np.std(rl_r8 - rl_r4, 0)/np.sqrt(np.sum(rl_bsln**2., 0)/nmdl)

  return relChngDiff, rc_r8, rc_r4, std_r8, std_r4, std_diff


def getGrossEnsembleAtYear(ryear, ncDir='/ClimateRun4/multi-hazard/eva', bslnYear=1995, retPer=100, threshold=200):
  flpattern = 'projection_dis_{scen}_{mdl}_wuChang_statistics.nc'

  wlyR8 = getWarmingLevels('rcp85', 2.0)
 #wlyR4 = getWarmingLevels('rcp45', warmingLev)

  models = wlyR8.keys()
  tamask, _, _ = getAfricaAndTurkeyMask()
  tamask = tamask.transpose()

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
    if threshold > 0:
      cnd = rlBslnR8 < threshold
      r8RelChng[cnd] = np.nan

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
    if threshold > 0:
      cnd = rlBslnR4 < threshold
      r4RelChng[cnd] = np.nan

    r8RelChng[~tamask] = np.nan
    r4RelChng[~tamask] = np.nan

    rl_all.append(r8RelChng)
    rl_all.append(r4RelChng)
    
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
    flrpth = os.path.join(ncDir, flr)
    
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
    rl.append(rRelChng)
    
  rl = np.array(rl)

  ensembleRelChng = np.nanmean(rl, 0)

  return ensembleRelChng

  



def loadMdlsAtWl(ncDir='/ClimateRun4/multi-hazard/eva', bslnYear=1995, warmingLev=2, rlVarName='rl', numberOfModels=-1):
  flpattern = 'projection_dis_{scen}_{mdl}_wuChang_statistics.nc'

  wlyR8 = getWarmingLevels('rcp85', warmingLev)
  wlyR4 = getWarmingLevels('rcp45', warmingLev)

  models = wlyR8.keys()
  models.sort()
  numberOfModels = len(models) if numberOfModels==-1 else numberOfModels
 #tamask, _, _ = getAfricaAndTurkeyMask()
 #tamask = tamask.transpose()

  bsln = []
  rl_r4 = []
  rl_r8 = [] 
  for mdl, imdl in zip(models[:numberOfModels], range(numberOfModels)):
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
    year_ = ds.variables['year'][:]
    yIndxBsln = np.where(year_ == bslnYear)[0][0]
    rlBslnR8 = ds.variables[rlVarName][:, yIndxBsln, :, :]
    yIndx = np.where(year_==r8yearInf)[0][0]
    rlR8_ = ds.variables[rlVarName][:, yIndx:yIndx+2, :, :]
    ds.close()
    rlR8 = interp1d(year_[yIndx:yIndx+2], rlR8_, axis=1)(r8year)

    print('  loading file ' + flr4pth)
    ds = netCDF4.Dataset(flr4pth)
    rlBslnR4 = ds.variables[rlVarName][:, yIndxBsln, :, :]
    yIndx = np.where(year_==r4yearInf)[0][0]
    rlR4_ = ds.variables[rlVarName][:, yIndx:yIndx+2, :, :]
    ds.close()
    rlR4 = interp1d(year_[yIndx:yIndx+2], rlR4_, axis=1)(r4year)

    rlBsln = rlBslnR8
   #rlBsln[~tamask] = np.nan
   #rlR4[~tamask] = np.nan
   #rlR8[~tamask] = np.nan

    bsln.append(rlBsln)
    rl_r8.append(rlR8)
    rl_r4.append(rlR4)

  bsln = np.array(bsln)
  rl_r8 = np.array(rl_r8)
  rl_r4 = np.array(rl_r4)

  return bsln, rl_r8, rl_r4, retper_


