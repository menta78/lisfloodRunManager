import numpy as np
import os, re
from scipy.stats import ttest_ind
import netCDF4
import pickle
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d

from getWarmingLevels import getWarmingLevels




sigThreshold = .2

def computeRlChngPValueMontecarlo(rlBsl, rlErrBsl, rlRcp, rlErrRcp):
  nMontecarlo = 50

  nmodel = rlBsl.shape[0]

  bslnRandom = []
  rcpRandom = []

  cnd = np.logical_not(np.isnan(rlBsl[0]))

  print('randomizing ...')
  for imdl in range(nmodel):
    print('  ' + str(imdl))
    bsln = np.squeeze(rlBsl[imdl])
    bslnErr = np.squeeze(rlErrBsl[imdl])
    loc, sigma = bsln[cnd], bslnErr[cnd]
    sigma[np.isnan(sigma)] = 1.1
    sigma[sigma < 1.1] = 1.1
    # assuming a lognormal distribution of the fitting error.
    # estimating mean and std-dev of the lognormal
    mul = np.log(loc**2./np.sqrt(sigma + loc**2))
    sigl = np.sqrt(np.log(sigma/loc**2+1))
    # randomizing on the lognormal
    bslnRnd_ = np.array([np.random.lognormal(mul, sigl) for i in range(nMontecarlo)])
    bslnRandom.append(bslnRnd_)

    rcp = np.squeeze(rlRcp[imdl])
    rcpErr = np.squeeze(rlErrRcp[imdl])
    loc, sigma = rcp[cnd], rcpErr[cnd]
    sigma[np.isnan(sigma)] = 1.1
    sigma[sigma < 1.1] = 1.1
    # assuming a lognormal distribution of the fitting error.
    # estimating mean and std-dev of the lognormal
    mul = np.log(loc**2./np.sqrt(sigma + loc**2))
    sigl = np.sqrt(np.log(sigma/loc**2+1))
    # randomizing on the lognormal
    rcpRnd_ = np.array([np.random.lognormal(mul, sigl) for i in range(nMontecarlo)])
    rcpRandom.append(rcpRnd_)

  bslnRandom = np.array(bslnRandom)
  rcpRandom = np.array(rcpRandom)
    
  print('computing the pvalue ...')
  _, pvalue = ttest_ind(bslnRandom, rcpRandom, equal_var=False, axis=0)
  nmpvalue = np.mean(pvalue, 0)

  percSig = np.sum(nmpvalue < sigThreshold)/float(len(nmpvalue))*100
  print('% significant: ' + str(percSig))

  pValueMap = np.ones(rlBsl[0].shape)*np.nan
  pValueMap[cnd] = nmpvalue

  return pValueMap




def computeRlChngPValueMeansOnly(rlBsl, rlRcp):
  rlBsl = np.array(rlBsl)
  rlRcp = np.array(rlRcp)

  _, pValueMap = ttest_ind(rlBsl, rlRcp, equal_var=True, axis=0)
  pvalue = pValueMap[np.logical_not(np.isnan(pValueMap))]

  percSig = np.sum(pvalue < sigThreshold)/float(len(pvalue))*100
  print('% significant: ' + str(percSig))

  return pValueMap




def countAgreeingModelsAndGetStdDev(rlBsl, rlRcp):
  rlBsl = np.array(rlBsl)
  rlRcp = np.array(rlRcp)

  rldiff = rlRcp - rlBsl
  
  rldiffMn = np.mean(rldiff, 0)
  rldiffMn3d = np.tile(rldiffMn, [rlBsl.shape[0], 1, 1])

  cnt = np.ones(rldiffMn.shape)*np.nan
  cnt[rldiffMn > 0] = np.sum(rldiff > 0, 0)[rldiffMn > 0]
  cnt[rldiffMn < 0] = np.sum(rldiff < 0, 0)[rldiffMn < 0]

  dff = rlRcp - rlBsl
  stddff = np.std(dff, 0)
  std = stddff/np.nanmean(rlBsl, 0)

  return cnt, std
  



def getLonLat():
  lonLatFile = 'lonlat.nc'
  ds = netCDF4.Dataset(lonLatFile)
  lon = ds.variables['lon'][:]
  lat = ds.variables['lat'][:]
  return lon, lat


  
##### end-of-century change significance #####
def computeRlChngPValueFromNcs(ncDir='/ClimateRun4/multi-hazard/eva', 
      ncFlPattern='projection_dis_(.*)rcp85(.*)_wuChang_statistics.nc', bslnYear=1995, projYear=2085, retPer=100):

  fls = [os.path.join(ncDir, f) for f in os.listdir(ncDir) if re.match(ncFlPattern, f)]

  rl_bsln = []
  serl_bsln = []
  rl_rcp = [] 
  serl_rcp = []
  for fl, ifl in zip(fls, range(len(fls))):
    print('loading file ' + fl)
    ds = netCDF4.Dataset(fl)

    retper_ = ds.variables['return_period'][:]
    rpIndx = np.where(retper_==retPer)[0][0]
   
    year_ = ds.variables['year'][:]
    byIndx = np.where(year_==bslnYear)[0][0]
    ryIndx = np.where(year_==projYear)[0][0]

    rlbsln = ds.variables['rl'][rpIndx, byIndx, :, :]
    serlbsln = ds.variables['se_rl'][rpIndx, byIndx, :, :]
    rlrcp = ds.variables['rl'][rpIndx, ryIndx, :, :]
    serlrcp = ds.variables['se_rl'][rpIndx, ryIndx, :, :]

    rl_bsln.append(rlbsln)
    serl_bsln.append(serlbsln)
    rl_rcp.append(rlrcp)
    serl_rcp.append(serlrcp)

  rl_bsln = np.array(rl_bsln)
  rl_bsln[rl_bsln <= .1] = .1
  serl_bsln = np.array(serl_bsln)
  serl_bsln[serl_bsln <= .1] = .1
  

  rl_rcp = np.array(rl_rcp)
  rl_rcp[rl_rcp <= .1] = .1
  serl_rcp = np.array(rl_rcp)
  serl_rcp[serl_rcp <= .1] = .1

 #pvalue = computeRlChngPValueMontecarlo(rl_bsln, serl_bsln, rl_rcp, serl_rcp)
  pvalue = computeRlChngPValueMeansOnly(rl_bsln, rl_rcp)

  agrMdlCnt, std = countAgreeingModelsAndGetStdDev(rl_bsln, rl_rcp)

  return pvalue, agrMdlCnt, std


def saveRlChngPValueToFile(outFilePath, **kwargs):
  pvalue = computeRlChngPValueFromNcs(**kwargs)
 #outFl = open(outFilePath, 'w')
 #pickle.dump([lon, lat, pvalue], outFl)
 #outFl.close()
  np.savetxt(outFilePath, pvalue)
  return pvalue


def plotRlChngPvalue(pvalue):
  lon, lat = getLonLat()
  pvl = pvalue.copy()
  pvl[pvl > .2] = np.nan
  plt.pcolor(lon, lat, pvl.transpose(), cmap='Reds_r'); plt.colorbar()


def saveRlChngPValueToFileRcp85(outFilePath='./pvalue_rcp85.csv'):
  pvalue = saveRlChngPValueToFile(outFilePath, ncFlPattern='projection_dis_(.*)rcp85(.*)_wuChang_statistics.nc')
  plotRlChngPvalue(pvalue)
  plt.show()


def saveRlChngPValueToFileRcp45(outFilePath='./pvalue_rcp45.csv'):
  pvalue = saveRlChngPValueToFile(outFilePath, ncFlPattern='projection_dis_(.*)rcp45(.*)_wuChang_statistics.nc')
  plotRlChngPvalue(pvalue)
  plt.show()
##########################################






########### change at warming level between scenarios #########
def computeRlChngPValueAtWarmingLevBtwScen(ncDir='/ClimateRun4/multi-hazard/eva', warmingLev=2, retPer=100, minThreshold=0):
  flpattern = 'projection_dis_{scen}_{mdl}_wuChang_statistics.nc'

  wlyR8 = getWarmingLevels('rcp85', warmingLev)
  wlyR4 = getWarmingLevels('rcp45', warmingLev)

  models = wlyR8.keys()

  rl_r4 = []
  serl_r4 = []
  rl_r8 = [] 
  serl_r8 = []
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
    yIndx = np.where(year_==r8yearInf)[0][0]
    rlR8_ = ds.variables['rl'][rpIndx, yIndx:yIndx+2, :, :]
    serlR8_ = ds.variables['se_rl'][rpIndx, yIndx:yIndx+2, :, :]
    ds.close()
    rlR8 = interp1d(year_[yIndx:yIndx+2], rlR8_, axis=0)(r8year)
    serlR8 = interp1d(year_[yIndx:yIndx+2], serlR8_, axis=0)(r8year)

    print('  loading file ' + flr4pth)
    ds = netCDF4.Dataset(flr4pth)
    yIndx = np.where(year_==r4yearInf)[0][0]
    rlR4_ = ds.variables['rl'][rpIndx, yIndx:yIndx+2, :, :]
    serlR4_ = ds.variables['se_rl'][rpIndx, yIndx:yIndx+2, :, :]
    ds.close()
    rlR4 = interp1d(year_[yIndx:yIndx+2], rlR4_, axis=0)(r4year)
    serlR4 = interp1d(year_[yIndx:yIndx+2], serlR4_, axis=0)(r4year)

    rl_r8.append(rlR8)
    serl_r8.append(serlR8)
    rl_r4.append(rlR4)
    serl_r4.append(serlR4)

  rl_r8 = np.array(rl_r8)
  rl_r8[rl_r8 <= .1] = .1
  serl_r8 = np.array(serl_r8)
  serl_r8[serl_r8 <= .1] = .1

  rl_r4 = np.array(rl_r4)
  rl_r4[rl_r4 <= .1] = .1
  serl_r4 = np.array(rl_r4)
  serl_r4[serl_r4 <= .1] = .1

  cnd = np.nanmean(rl_r8, 0) < minThreshold
  cnd = np.tile(cnd, [len(models), 1, 1])
  rl_r8[cnd] = np.nan
  serl_r8[cnd] = np.nan
  rl_r4[cnd] = np.nan
  serl_r4[cnd] = np.nan

  pvalue = computeRlChngPValueMontecarlo(rl_r4, serl_r4, rl_r8, serl_r8)
 #pvalue = computeRlChngPValueMeansOnly(rl_r4, rl_r8)

  agrMdlCnt, _ = countAgreeingModelsAndGetStdDev(rl_r4, rl_r8)

  return pvalue, agrMdlCnt


def saveRlChngPValueAtWarmingLevBtwScen(outFilePath, **kwargs):
  pvalue = computeRlChngPValueAtWarmingLevBtwScen(**kwargs)
 #outFl = open(outFilePath, 'w')
 #pickle.dump([lon, lat, pvalue], outFl)
 #outFl.close()
  np.savetxt(outFilePath, pvalue)
  return pvalue


def saveRlChngPValueAtWarmingLevBtwScen_20deg(outFilePath='./pvalue_cfr_2deg.csv', minThreshold=0):
  pvalue = saveRlChngPValueAtWarmingLevBtwScen(outFilePath, warmingLev=2, minThreshold=minThreshold)
  plotRlChngPvalue(pvalue)
  plt.show()


def saveRlChngPValueAtWarmingLevBtwScen_15deg(outFilePath='./pvalue_cfr_2deg.csv', minThreshold=0):
  pvalue = saveRlChngPValueAtWarmingLevBtwScen(outFilePath, warmingLev=1.5, minThreshold=minThreshold)
  plotRlChngPvalue(pvalue)
  plt.show()
#######################################################################





######### significance of chng between baseline and warming level ##
def computeRlChngPValueAtWarmingLev(ncDir='/ClimateRun4/multi-hazard/eva', bslnYear=1995, scen='rcp85', warmingLev=2, retPer=100, minThreshold=0):
  flpattern = 'projection_dis_{scen}_{mdl}_wuChang_statistics.nc'

  wly = getWarmingLevels(scen, warmingLev)

  models = wly.keys()

  rl_bs = []
  serl_bs = []
  rl_rc = [] 
  serl_rc = []
  for mdl, imdl in zip(models, range(len(models))):
    print('model ' + mdl)
    flr = flpattern.format(scen=scen, mdl=mdl)
    flrpth = os.path.join(ncDir, flr)

    rcyear = wly[mdl]
    rcyearInf = int(np.floor(rcyear/float(5))*5)
    print('  ' + scen + ' w.l. year: ' + str(rcyear))

    print('  loading file ' + flrpth)
    ds = netCDF4.Dataset(flrpth)
    retper_ = ds.variables['return_period'][:]
    rpIndx = np.where(retper_==retPer)[0][0]
    year_ = ds.variables['year'][:]
    yIndx = np.where(year_==rcyearInf)[0][0]
    rlR_ = ds.variables['rl'][rpIndx, yIndx:yIndx+2, :, :]
    serlR_ = ds.variables['se_rl'][rpIndx, yIndx:yIndx+2, :, :]
    yBslnIndx = np.where(year_==bslnYear)[0][0]
    rlBsln = ds.variables['rl'][rpIndx, yBslnIndx, :, :]
    serlBsln = ds.variables['se_rl'][rpIndx, yBslnIndx, :, :]
    ds.close()
    rlR = interp1d(year_[yIndx:yIndx+2], rlR_, axis=0)(rcyear)
    serlR = interp1d(year_[yIndx:yIndx+2], serlR_, axis=0)(rcyear)

    rl_rc.append(rlR)
    serl_rc.append(serlR)
    rl_bs.append(rlBsln)
    serl_bs.append(serlBsln)

  rl_rc = np.array(rl_rc)
  rl_rc[rl_rc <= .1] = .1
  serl_rc = np.array(serl_rc)
  serl_rc[serl_rc <= .1] = .1

  rl_bs = np.array(rl_bs)
  rl_bs[rl_bs <= .1] = .1
  serl_bs = np.array(rl_bs)
  serl_bs[serl_bs <= .1] = .1

  cnd = np.nanmean(rl_rc, 0) < minThreshold
  cnd = np.tile(cnd, [len(models), 1, 1])
  rl_rc[cnd] = np.nan
  serl_rc[cnd] = np.nan
  rl_bs[cnd] = np.nan
  serl_bs[cnd] = np.nan

  pvalue = computeRlChngPValueMontecarlo(rl_bs, serl_bs, rl_rc, serl_rc)
 #pvalue = computeRlChngPValueMeansOnly(rl_bs, rl_rc)

  agrMdlCnt, std = countAgreeingModelsAndGetStdDev(rl_bs, rl_rc)

  return pvalue, agrMdlCnt, std


def plotRlChngPValueAtWarmingLev(**kwargs):
  pvalue, agrMdlCnt = computeRlChngPValueAtWarmingLev(**kwargs)
  lon, lat = getLonLat()
  f = plt.figure(figsize=[3,3])
  plt.pcolor(lon.transpose(), lat.transpose(), pvalue, cmap='bwr_r')
  return f

