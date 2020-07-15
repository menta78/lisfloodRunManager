import netCDF4
import numpy as np
import os, re
from scipy.interpolate import interp1d

from getWarmingLevels import getWarmingLevels

seasons = ['DJF', 'MAM', 'JJA', 'SON']
seasonMonth = [1, 4, 7, 10]

def extract1Model(scen, model, inputHistNcFlPath, inputRcNcFlPath, outputNcFlPath, season, varnames=['pr']):
  wls = [1.5, 2.0, 3.0]
  bslnYear = 1995
  seasonInx = seasons.index(season)
  ssnmnt = seasonMonth[seasonInx]

  print('  loading the data ...')
  dsin = netCDF4.Dataset(inputHistNcFlPath)
  x = dsin.variables['x'][:]
  y = dsin.variables['y'][:]
  val = None
  for varname in varnames:
    if varname in dsin.variables:
      val = dsin.variables[varname][:]
      break
  if val is None:
    raise Exception('variables ' + str(varnames) + ' not found in file ' + inputHistNcFlPath)
  valHist = val
  tmnc = dsin.variables['time']
  valDtHist = [d for d in netCDF4.num2date(tmnc[:], tmnc.units, tmnc.calendar)]
  dsin.close()

  dsin = netCDF4.Dataset(inputRcNcFlPath)
  val = None
  for varname in varnames:
    if varname in dsin.variables:
      val = dsin.variables[varname][:]
      break
  if val is None:
    raise Exception('variables ' + str(varnames) + ' not found in file' + inputRcNcFlPath)
  valRc = val
  tmnc = dsin.variables['time']
  valDtRc = [d for d in netCDF4.num2date(tmnc[:], tmnc.units, tmnc.calendar)]
  dsin.close()

  val = np.concatenate([valHist, valRc], 0)
  valDt = np.concatenate([valDtHist, valDtRc], 0)
  valMnth = np.array([d.month for d in valDt])
  valYrs = np.array([d.year for d in valDt])
  iitime = valMnth == ssnmnt
  valYrs = valYrs[iitime]
  val = val[iitime, :, :]

  def getLonLat():
    lonLatFile = 'lonlat.nc'
    ds = netCDF4.Dataset(lonLatFile)
    lon = ds.variables['lon'][:].transpose()
    lat = ds.variables['lat'][:].transpose()
    return lon, lat

  def getValAtYear(valAll, yearAll, year, halfTmWindowSize=14):
    yindx = np.where(yearAll == year)[0][0]
    val = np.nanmean(valAll[yindx-halfTmWindowSize:yindx+halfTmWindowSize, :], 0).squeeze()
    return val
    
  bslnVal = getValAtYear(val, valYrs, bslnYear)

  print('  elaborating ...')
  noutWls = len(wls)
  shp_ = bslnVal.shape
  shpOut = [noutWls, shp_[0], shp_[1]]
  outYrVal = np.zeros(shpOut)*np.nan
  for wl, iwl in zip(wls, range(noutWls)):
    ywls = getWarmingLevels(scen, wl)
    if ywls == None:
      continue
    outYr = ywls[model]
    yrVal = getValAtYear(val, valYrs, outYr)
    outYrVal[iwl, :, :] = yrVal
    
  bslnVal3d = np.tile(bslnVal, [3, 1, 1])
  dlt = (outYrVal/bslnVal3d - 1)*100.
  absDlt = outYrVal - bslnVal3d

  print('  saving the output ...')
  if os.path.isfile(outputNcFlPath):
    os.remove(outputNcFlPath)
  dsout = netCDF4.Dataset(outputNcFlPath, 'w')
  dsout.createDimension('x', len(x))
  dsout.createDimension('y', len(y))
  dsout.createDimension('warming_lev', noutWls)

  xnc = dsout.createVariable('x', 'f8', ('x'))
  xnc.description = 'x'
  xnc[:] = x

  ync = dsout.createVariable('y', 'f8', ('y'))
  ync.description = 'y'
  ync[:] = y

  lon, lat = getLonLat()
  lon, lat = lon.transpose(), lat.transpose()
  lonnc = dsout.createVariable('lon', 'f8', ('y', 'x'))
  lonnc.description = 'longitude mtx'
  lonnc[:] = lon

  latnc = dsout.createVariable('lat', 'f8', ('y', 'x'))
  latnc.description = 'latitude mtx'
  latnc[:] = lat

  wlsnc = dsout.createVariable('warming_lev', 'f4', ('warming_lev'))
  wlsnc.description = 'warming_lev'
  wlsnc[:] = wls

  bslnYrNc = dsout.createVariable('baseline_year', 'i4')
  bslnYrNc.description = 'baseline year'
  bslnYrNc[:] = bslnYear

  bslnValNc = dsout.createVariable('baseline_val', 'f4', ('y', 'x'))
  bslnValNc.description = 'value at baseline (deg or mm or m3 or ...)'
  bslnValNc[:] = bslnVal

  valNc = dsout.createVariable('value', 'f4', ('warming_lev', 'y', 'x'))
  valNc.description = 'values at warming levels (deg or mm or m3 or ...)'
  valNc[:] = outYrVal

  valNc = dsout.createVariable('value_perc_chng', 'f4', ('warming_lev', 'y', 'x'))
  valNc.description = 'percentage change at warming levels (%)'
  valNc[:] = dlt

  valNc = dsout.createVariable('value_abs_chng', 'f4', ('warming_lev', 'y', 'x'))
  valNc.description = 'absolute change at warming levels (deg or mm or m3 or ...)'
  valNc[:] = absDlt

  dsout.close()
  

def loopModels(inputDir, inputFlName, ncVarNames, outputDir, season):
  models = [dr for dr in os.listdir(inputDir) if os.path.isdir(os.path.join(inputDir, dr))]
  for mdl in models:
    histFlPath = os.path.join(inputDir, mdl, 'historical', inputFlName)
    r8FlPath = os.path.join(inputDir, mdl, 'rcp85', inputFlName)
    r4FlPath = os.path.join(inputDir, mdl, 'rcp45', inputFlName)

    outR8FlPath = os.path.join(outputDir, 'mean_' + ncVarNames[0] + '_rcp85_' + mdl + '_season_' + season + '_atWarmingLev.nc')
    outR4FlPath = os.path.join(outputDir, 'mean_' + ncVarNames[0] + '_rcp45_' + mdl + '_season_' + season + '_atWarmingLev.nc')

    print('elaborating file ' + outR8FlPath)
    extract1Model('rcp85', mdl, histFlPath, r8FlPath, outR8FlPath, season, varnames=ncVarNames)
    print('elaborating file ' + outR4FlPath)
    extract1Model('rcp45', mdl, histFlPath, r4FlPath, outR4FlPath, season, varnames=ncVarNames)


def computeEnsemble(flsDir, filePrefix, season):
  outFlName = filePrefix + '_season_' + season + '_ensemble.nc'
  outFlPath = os.path.join(flsDir, outFlName)
  fls = [f for f in os.listdir(flsDir) if (f != outFlName) and (re.match(filePrefix + '(.*)season_' + season, f))]
  nfls = len(fls)
  outDlt = None
  outAbsDlt = None
  for f, ifl in zip(fls, range(nfls)):
    fpth = os.path.join(flsDir, f)
    ds = netCDF4.Dataset(fpth)
    vls = ds.variables['value_perc_chng'][:]
    vlsAbs = ds.variables['value_abs_chng'][:]
    if outDlt is None:
      x = ds.variables['x'][:]
      y = ds.variables['y'][:]
      lon = ds.variables['lon'][:]
      lat = ds.variables['lat'][:]
      wls = ds.variables['warming_lev'][:]
      bslnYear = ds.variables['baseline_year'][:]
      shp = [nfls]
      shp.extend(vls.shape)
      outDlt = np.zeros(shp)*np.nan
      outAbsDlt = np.zeros(shp)*np.nan
    ds.close()
    outDlt[ifl, :, :, :] = vls
    outAbsDlt[ifl, :, :, :] = vlsAbs
  outDlt[outDlt > 1e10] = np.nan
  outAbsDlt[outDlt > 1e10] = np.nan
  medianDlt = np.nanmedian(outDlt, 0)
  medianAbsDlt = np.nanmedian(outAbsDlt, 0)
  
  nmdl = np.sum(~np.isnan(outDlt), 0)

  cndGt0 = outDlt > 0
  gt0Sum = np.nansum(cndGt0, 0)
  signPos = gt0Sum > np.floor(nmdl/3.*2.)

  cndLt0 = outDlt < 0
  lt0Sum = np.nansum(cndLt0, 0)
  signNeg = lt0Sum > np.floor(nmdl/3.*2.)

  rbst = np.logical_or(signPos, signNeg)

  print('  saving ensemble file ' + outFlPath)
  if os.path.isfile(outFlPath):
    os.remove(outFlPath)
  dsout = netCDF4.Dataset(outFlPath, 'w')
  dsout.createDimension('x', len(x))
  dsout.createDimension('y', len(y))
  dsout.createDimension('warming_lev', len(wls))

  xnc = dsout.createVariable('x', 'f8', ('x'))
  xnc.description = 'x'
  xnc[:] = x

  ync = dsout.createVariable('y', 'f8', ('y'))
  ync.description = 'y'
  ync[:] = y

  lonnc = dsout.createVariable('lon', 'f8', ('y', 'x'))
  lonnc.description = 'longitude mtx'
  lonnc[:] = lon

  latnc = dsout.createVariable('lat', 'f8', ('y', 'x'))
  latnc.description = 'latitude mtx'
  latnc[:] = lat

  wlsnc = dsout.createVariable('warming_lev', 'f4', ('warming_lev'))
  wlsnc.description = 'warming_lev'
  wlsnc[:] = wls

  bslnYrNc = dsout.createVariable('baseline_year', 'i4')
  bslnYrNc.description = 'baseline year'
  bslnYrNc[:] = bslnYear

  medianChangeNc = dsout.createVariable('ensemble_change', 'f4', ('warming_lev', 'y', 'x'))
  medianChangeNc.description = 'projected ensemble change (%)'
  medianChangeNc[:] = medianDlt

  absChangeNc = dsout.createVariable('ensemble_abs_change', 'f4', ('warming_lev', 'y', 'x'))
  absChangeNc.description = 'projected ensemble absolute change (deg or mm or m3 or ...)'
  absChangeNc[:] = medianAbsDlt

  robustNc = dsout.createVariable('robustness_of_chng', 'int', ('warming_lev', 'y', 'x'))
  robustNc.description = 'robustness of proj. change'
  robustNc[:] = rbst

  dsout.close()



def loopSeasons(inputDir, inputFlName, ncVarNames, outputDir, filePrefix):
  for season in seasons:
    print('elaborating season ' + season)
    loopModels(inputDir, inputFlName, ncVarNames, outputDir, season)
    computeEnsemble(outputDir, filePrefix, season)


  


if __name__ == '__main__':
  import pdb; pdb.set_trace()

 # precipitations
 #inputDir = '/DATA/ClimateData/cordexEurope/seasonmeans/rawData/'
 #inputFlName = 'pr.nc'
 #outputDir = '/DATA/ClimateData/cordexEurope/seasonmeans/atWarmingLev/'
 #ncVarNames = ['pr', 'prAdjust']
 #filePrefix = 'mean_pr'

 # temperatures
  inputDir = '/DATA/ClimateData/cordexEurope/seasonmeans/rawData/'
  inputFlName = 'ta.nc'
  outputDir = '/DATA/ClimateData/cordexEurope/seasonmeans/atWarmingLev/'
  ncVarNames = ['ta', 'tas', 'tasAdjust']
  filePrefix = 'mean_ta'

  loopSeasons(inputDir, inputFlName, ncVarNames, outputDir, filePrefix)
