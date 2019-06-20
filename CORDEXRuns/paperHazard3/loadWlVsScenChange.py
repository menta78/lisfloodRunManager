import numpy as np
import os, netCDF4
from scipy.interpolate import interp1d
from scipy import stats

from getWarmingLevels import getWarmingLevels
from loadOutletRetLevFromNc import getAfricaAndTurkeyMask



def loadWlVsScenChange(ncDir='/ClimateRun4/multi-hazard/eva', bslnYear=1995, warmingLev=2, 
    retPer=100, threshold=0, rlVarName='rl',
    flpattern='projection_dis_{scen}_{mdl}_wuConst_statistics.nc',
    nmodels=-1, shapeParamNcVarName='', minNumModels=8):
  # computes the mean relative change

  wlyR8 = getWarmingLevels('rcp85', warmingLev)
  wlyR4 = getWarmingLevels('rcp45', warmingLev)

  dsuparea = netCDF4.Dataset('upArea.nc')
  upArea = dsuparea.variables['upArea'][:].transpose()
  dsuparea.close()

  maskInvalidShapeParamPts = shapeParamNcVarName != ''

  models = wlyR8.keys()
  if nmodels > -1:
    models = models[:nmodels]
  # menta
 #models = [models[0], models[1]]
  tamask, _, _ = getAfricaAndTurkeyMask()
  tamask = tamask.transpose()

  if minNumModels > nmodels:
    minNumModels = nmodels

  rl_r4 = []
  rl_r8 = [] 
  mdlCountR4 = np.zeros(upArea.shape)
  mdlCountR8 = np.zeros(upArea.shape)
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
    rlR8 = interp1d(year_[yIndx:yIndx+2], rlR8_, axis=0)(r8year)
    if maskInvalidShapeParamPts:
      shapeParam = ds.variables[shapeParamNcVarName][:]
      cnd = shapeParam <= -.4
      rlBslnR8[cnd] = np.nan
      rlR8[cnd] = np.nan
    ds.close()
    r8RelChng = (rlR8-rlBslnR8)/rlBslnR8
    if threshold > 0:
      cnd = rlBslnR8 < threshold
      r8RelChng[cnd] = np.nan
     #r8RelChng[r8RelChng < -.15] = np.nan

    print('  loading file ' + flr4pth)
    ds = netCDF4.Dataset(flr4pth)
    rlBslnR4 = ds.variables[rlVarName][rpIndx, yIndxBsln, :, :]
   #rlBslnR4 = rlBslnR8
    yIndx = np.where(year_==r4yearInf)[0][0]
    rlR4_ = ds.variables[rlVarName][rpIndx, yIndx:yIndx+2, :, :]
    rlR4 = interp1d(year_[yIndx:yIndx+2], rlR4_, axis=0)(r4year)
    if maskInvalidShapeParamPts:
      shapeParam = ds.variables[shapeParamNcVarName][:]
      cnd = shapeParam <= -.4
      rlBslnR4[cnd] = np.nan
      rlR4[cnd] = np.nan
    ds.close()
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
    
    mdlCountR8 += ~np.isnan(r8RelChng)
    mdlCountR4 += ~np.isnan(r4RelChng)

  rl_r8 = np.array(rl_r8)
  rl_r4 = np.array(rl_r4)

  mdlCountMskR8 = mdlCountR8 >= minNumModels
  mdlCountMskR4 = mdlCountR4 >= minNumModels
  mskR8 = np.tile(mdlCountMskR8, [rl_r8.shape[0], 1, 1])
  mskR4 = np.tile(mdlCountMskR4, [rl_r8.shape[0], 1, 1])

  rl_r8[mskR8 != 1] = np.nan
  rl_r4[mskR4 != 1] = np.nan

  relChngDiff = np.nanmean(rl_r8-rl_r4, 0)
  relChngDiff[~tamask] = np.nan

  return relChngDiff, np.nanmean(rl_r8, 0), np.nanmean(rl_r4, 0), rl_r8, rl_r4



def loadWlVsScenChange2(ncDir='/ClimateRun4/multi-hazard/eva', bslnYear=1995, warmingLev=2, retPer=100, threshold=0, rlVarName='rl'):
  # computes the relative change of the ensemble
  flpattern = 'projection_dis_{scen}_{mdl}_wuConst_statistics.nc'

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

  _, pval_r8 = stats.ttest_ind(rl_r8, rl_bsln, 0)
  _, pval_r4 = stats.ttest_ind(rl_r4, rl_bsln, 0)
  _, pval_diff = stats.ttest_ind(rl_r8, rl_r4, 0)

  return relChngDiff, rc_r8, rc_r4, std_r8, std_r4, std_diff, pval_r8, pval_r4, pval_diff



def loadMeanChangesAtWl(ncDir='/ClimateRun4/multi-hazard/eva', bslnYear=1995, warmingLev=2, 
    threshold=0, rlVarName='year_mean',
    flpattern='projection_dis_{scen}_{mdl}_wuConst_statistics.nc',
    nmodels=-1, timeWindowHalfSize=15):
  # computes the mean relative change

  wlyR8 = getWarmingLevels('rcp85', warmingLev)
  wlyR4 = getWarmingLevels('rcp45', warmingLev)

  dsuparea = netCDF4.Dataset('upArea.nc')
  upArea = dsuparea.variables['upArea'][:].transpose()
  dsuparea.close()

  models = wlyR8.keys()
  if nmodels > -1:
    models = models[:nmodels]
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
    r4year = wlyR4[mdl]

    print('  loading file ' + flr8pth)
    ds = netCDF4.Dataset(flr8pth)
    year_ = ds.variables['year_all'][:]
    yIndxBsln = np.where(year_ == bslnYear)[0][0]
    minIndx = np.max([yIndxBsln-timeWindowHalfSize, 0])
    maxIndx = np.min([yIndxBsln+timeWindowHalfSize, len(year_)])
    rlBslnR8 = np.nanmean(ds.variables[rlVarName][minIndx:maxIndx, :, :], 0)
    yIndx = np.where(year_==r8year)[0][0]
    minIndx = np.max([yIndx-timeWindowHalfSize, 0])
    maxIndx = np.min([yIndx+timeWindowHalfSize, len(year_)])
    rlR8 = np.nanmean(ds.variables[rlVarName][minIndx:maxIndx, :, :], 0)
    r8RelChng = (rlR8-rlBslnR8)/rlBslnR8
    if threshold > 0:
      cnd = rlBslnR8 < threshold
      r8RelChng[cnd] = np.nan
     #r8RelChng[r8RelChng < -.15] = np.nan

    print('  loading file ' + flr4pth)
    ds = netCDF4.Dataset(flr4pth)
    rlBslnR4 = rlBslnR8
    yIndx = np.where(year_==r4year)[0][0]
    minIndx = np.max([yIndx-timeWindowHalfSize, 0])
    maxIndx = np.min([yIndx+timeWindowHalfSize, len(year_)])
    rlR4 = np.nanmean(ds.variables[rlVarName][minIndx:maxIndx, :, :], 0)
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




def getGrossEnsembleAtYear(ryear, ncDir='/ClimateRun4/multi-hazard/eva', bslnYear=1995, retPer=100, threshold=200):
  flpattern = 'projection_dis_{scen}_{mdl}_wuConst_statistics.nc'

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
  flpattern = 'projection_dis_{scen}_{mdl}_wuConst_statistics.nc'

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
  flpattern = 'projection_dis_{scen}_{mdl}_wuConst_statistics.nc'

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



def loadWlVsScenChangeYMax(ncDir='/ClimateRun4/multi-hazard/eva', bslnYear=1995, warmingLev=2, retPer=100, 
  threshold=0, rlVarName='year_max', windowHalfSize=10, flpattern='projection_dis_{scen}_{mdl}_wuConst_statistics.nc'):
  # computes the mean relative change

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
    print('  rcp85 w.l. year: ' + str(r8year))
    r4year = wlyR4[mdl]
    print('  rcp45 w.l. year: ' + str(r4year))

    hsz = windowHalfSize

    print('  loading file ' + flr8pth)
    ds = netCDF4.Dataset(flr8pth)
    year_ = ds.variables['year_all'][:]
    yIndxBsln = np.where(year_ == bslnYear)[0][0]
    rlBslnR8 = np.nanmean(ds.variables[rlVarName][yIndxBsln-hsz:yIndxBsln+hsz, :, :], 0)
    yIndx = np.where(year_==r8year)[0][0]
    rlR8 = np.nanmean(ds.variables[rlVarName][yIndx-hsz:yIndx+hsz, :, :], 0)
    ds.close()
    r8RelChng = (rlR8-rlBslnR8)/rlBslnR8
    if threshold > 0:
      cnd = rlBslnR8 < threshold
      r8RelChng[cnd] = np.nan
     #r8RelChng[r8RelChng < -.15] = np.nan

    print('  loading file ' + flr4pth)
    ds = netCDF4.Dataset(flr4pth)
   #rlBslnR4 = ds.variables[rlVarName][rpIndx, yIndxBsln, :, :]
    rlBslnR4 = rlBslnR8
    yIndx = np.where(year_==r4year)[0][0]
    rlR4 = np.nanmean(ds.variables[rlVarName][yIndx-hsz:yIndx+hsz, :, :], 0)
    ds.close()
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



def loadMeanPrecipitationChangesAtWl(ncRootDir='/DATA/ClimateData/cordexEurope/yearlymeans/', bslnYear=1995, warmingLev=2, 
    threshold=0,
    flname='pr.nc',
    nmodels=-1, timeWindowHalfSize=15):
  # computes the mean relative change

  wlyR8 = getWarmingLevels('rcp85', warmingLev)
  wlyR4 = getWarmingLevels('rcp45', warmingLev)

  models = wlyR8.keys()
  if nmodels > -1:
    models = models[:nmodels]

  tamask, _, _ = getAfricaAndTurkeyMask()
  tamask = tamask

  rlVarName1='pr'
  rlVarname2='prAdjust'

  rl_r4 = []
  rl_r8 = [] 
  for mdl, imdl in zip(models, range(len(models))):
    print('model ' + mdl)
    flhistpth = os.path.join(ncRootDir, mdl, 'historical', flname)
    flr8pth = os.path.join(ncRootDir, mdl, 'rcp85', flname)
    flr4pth = os.path.join(ncRootDir, mdl, 'rcp45', flname)

    r8year = wlyR8[mdl]
    r4year = wlyR4[mdl]

    print('  loading file ' + flhistpth)
    ds = netCDF4.Dataset(flhistpth)
    rlVarName = 'pr' if 'pr' in ds.variables else 'prAdjust'
    tmnc = ds.variables['time']
    tm = netCDF4.num2date(tmnc[:], tmnc.units, tmnc.calendar)
    yearHist = np.array([t.year for t in tm])
    yIndxBsln = np.where(yearHist == bslnYear)[0][0]
    minIndx = np.max([yIndxBsln-timeWindowHalfSize, 0])
    maxIndx = np.min([yIndxBsln+timeWindowHalfSize, len(yearHist)])
    rlBsln = np.nanmean(ds.variables[rlVarName][minIndx:maxIndx, :, :], 0)
    ds.close()

    print('  loading file ' + flr8pth)
    ds = netCDF4.Dataset(flr8pth)
    rlVarName = 'pr' if 'pr' in ds.variables else 'prAdjust'
    tmnc = ds.variables['time']
    tm = netCDF4.num2date(tmnc[:], tmnc.units, tmnc.calendar)
    yearR = np.array([t.year for t in tm])
    yIndx = np.where(yearR==r8year)[0][0]
    minIndx = np.max([yIndx-timeWindowHalfSize, 0])
    maxIndx = np.min([yIndx+timeWindowHalfSize, len(yearR)])
    rlR8 = np.nanmean(ds.variables[rlVarName][minIndx:maxIndx, :, :], 0)
    r8RelChng = (rlR8-rlBsln)/rlBsln
    if threshold > 0:
      cnd = rlBslnR8 < threshold
      r8RelChng[cnd] = np.nan
     #r8RelChng[r8RelChng < -.15] = np.nan
    ds.close()

    print('  loading file ' + flr4pth)
    ds = netCDF4.Dataset(flr4pth)
    rlVarName = 'pr' if 'pr' in ds.variables else 'prAdjust'
    tmnc = ds.variables['time']
    tm = netCDF4.num2date(tmnc[:], tmnc.units, tmnc.calendar)
    yearR = np.array([t.year for t in tm])
    yIndx = np.where(yearR==r4year)[0][0]
    minIndx = np.max([yIndx-timeWindowHalfSize, 0])
    maxIndx = np.min([yIndx+timeWindowHalfSize, len(yearR)])
    rlR4 = np.nanmean(ds.variables[rlVarName][minIndx:maxIndx, :, :], 0)
    r4RelChng = (rlR4-rlBsln)/rlBsln
    if threshold > 0:
      cnd = rlBslnR4 < threshold
      r4RelChng[cnd] = np.nan
     #r4RelChng[r4RelChng < -.15] = np.nan
    ds.close()

   #r8RelChng[upArea < 1e9] = np.nan
   #r4RelChng[upArea < 1e9] = np.nan

    r8RelChng[~tamask] = np.nan
    r4RelChng[~tamask] = np.nan

    rl_r8.append(r8RelChng)
    rl_r4.append(r4RelChng)

  rl_r8 = np.array(rl_r8)
  rl_r4 = np.array(rl_r4)

  relChngDiff = np.nanmean(rl_r8-rl_r4, 0)
  relChngDiff[~tamask] = np.nan

  return relChngDiff, np.nanmean(rl_r8, 0), np.nanmean(rl_r4, 0), rl_r8, rl_r4

