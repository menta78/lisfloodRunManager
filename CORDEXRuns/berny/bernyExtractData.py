import netCDF4
import numpy as np
import os, re
from scipy.interpolate import interp1d

from getWarmingLevels import getWarmingLevels


def extract1Model(scen, model, inputNcFlPath, outputNcFlPath):
  wls = [1.5, 2.0, 3.0, 4.0]
  bslnYear = 1995

  print('  loading the data ...')
  dsin = netCDF4.Dataset(inputNcFlPath)
  x = dsin.variables['x'][:]
  y = dsin.variables['y'][:]
  vals = dsin.variables['year_mean'][:]
  yrs = dsin.variables['year_all'][:]
  dsin.close()

  def getLonLat():
    lonLatFile = 'lonlat.nc'
    ds = netCDF4.Dataset(lonLatFile)
    lon = ds.variables['lon'][:].transpose()
    lat = ds.variables['lat'][:].transpose()
    return lon, lat

  def getValAtYear(vlsAll, yearAll, year):
    iyear = np.where(yearAll==year)[0][0]
    minIndx = max(iyear-14,0)
    vly = np.nanmean(vlsAll[minIndx:iyear+15,:,:], 0).squeeze()
    return vly
    
  bslnVal = getValAtYear(vals, yrs, bslnYear)

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
    yrVal = getValAtYear(vals, yrs, outYr)
    outYrVal[iwl, :, :] = yrVal
    
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
  lonnc = dsout.createVariable('lon', 'f8', ('x', 'y'))
  lonnc.description = 'longitude mtx'
  lonnc[:] = lon

  latnc = dsout.createVariable('lat', 'f8', ('x', 'y'))
  latnc.description = 'latitude mtx'
  latnc[:] = lat

  wlsnc = dsout.createVariable('warming_lev', 'f4', ('warming_lev'))
  wlsnc.description = 'warming_lev'
  wlsnc[:] = wls

  bslnYrNc = dsout.createVariable('baseline_year', 'i4')
  bslnYrNc.description = 'baseline year'
  bslnYrNc[:] = bslnYear

  bslnValNc = dsout.createVariable('baseline_mean_dis', 'f4', ('x', 'y'))
  bslnValNc.description = 'mean discharge at baseline (m**3)'
  bslnValNc[:] = bslnVal

  valNc = dsout.createVariable('mean_dis', 'f4', ('warming_lev', 'x', 'y'))
  valNc.description = 'mean discharge at warming levels (m**3)'
  valNc[:] = outYrVal

  prcChngNc = dsout.createVariable('perc_change', 'f4', ('warming_lev', 'x', 'y'))
  prcChngNc.description = 'change of mean discharge at warming levels (%)'
  prcChngNc[:] = (outYrVal-bslnVal)/bslnVal*100

  dsout.close()
  

def loopModels(inputDir, inputFlPattern, outputDir):

  
  infls = [fl for fl in os.listdir(inputDir) if re.match(inputFlPattern, fl)]
  for fl in infls:
    print('elaborating file ' + fl)
    flpth = os.path.join(inputDir, fl)
    outflpth = os.path.join(outputDir, fl.replace('projection_', 'meanDisChng_'))
    print('  output file path: ' + outflpth)
    m = re.match(inputFlPattern, fl)
    scen = m.groups()[0]
    model = m.groups()[1]
    extract1Model(scen, model, flpth, outflpth)


def plotResults1Mdl():
  flpth = '/ClimateRun/menta/xKees/returnPeriodShift_dis_rcp85_IPSL-INERIS-WRF331F_BC_wuChang_statistics.nc'
  testedRp = 10
  testedYear = 2086

  ds = netCDF4.Dataset(flpth)
  lon = ds.variables['lon'][:]
  lat = ds.variables['lat'][:]
  rp = ds.variables['baseline_rp'][:]
  yrs = ds.variables['year'][:]
  irp = np.where(rp == testedRp)[0][0]
  iyr = np.where(yrs == testedYear)[0][0]
  rpsht = ds.variables['baseline_rp_shift'][iyr, irp, :, :]
  ds.close()


  


if __name__ == '__main__':
  import pdb; pdb.set_trace()


 # discharge x Eamonn
  inputDir = '/ClimateRun4/multi-hazard/eva/'
  inputFlPattern = 'projection_dis_(rcp45|rcp85)_(.*)_wuConst_statistics.nc'
  outputDir = '/ClimateRun4/multi-hazard/eva/berny/'

 # precipitations
 #inputDir = '/ClimateRun4/multi-hazard/eva/'
 #inputDir = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/lisfloodEVA_pr/test'
 #inputFlPattern = 'projection_pr_(rcp45|rcp85)_(.*)_statistics.nc'
 #outputDir = '/ClimateRun4/multi-hazard/eva/prFrequencyShift/'

  loopModels(inputDir, inputFlPattern, outputDir)

