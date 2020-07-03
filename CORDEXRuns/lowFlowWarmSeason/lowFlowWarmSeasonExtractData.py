import netCDF4
import numpy as np
import os, re
from scipy.interpolate import interp1d

from getWarmingLevels import getWarmingLevels


def extract1Model(scen, model, inputNcFlPath, outputNcFlPath):
  wls = [1.5, 2.0, 3.0, 4.0]
  bslnYear = 1995
  
  outRetPer = [1.5, 2., 5, 10., 20., 50., 100., 200., 500.]

  print('  loading the data ...')
  dsin = netCDF4.Dataset(inputNcFlPath)
  x = dsin.variables['x'][:]
  y = dsin.variables['y'][:]
  inRetPer = dsin.variables['return_period'][:]
  retLev = dsin.variables['rl_min_ws'][:]
  rlYrs = dsin.variables['year'][:]
  dsin.close()

  def getLonLat():
    lonLatFile = 'lonlat.nc'
    ds = netCDF4.Dataset(lonLatFile)
    lon = ds.variables['lon'][:].transpose()
    lat = ds.variables['lat'][:].transpose()
    return lon, lat

  def getRetLevAtYear(retLevAll, yearAll, year, interpFunc=None):
    interpFunc = interp1d(yearAll, retLevAll, axis=1) if interpFunc is None else interpFunc
    retLev = interpFunc(year)
    return retLev, interpFunc

  def getOutRetLev(inRetLev, inRetPer, outRetPer):
    interpFunc = interp1d(inRetPer, inRetLev, axis=0)
    outRetLev = interpFunc(outRetPer)
    return outRetLev

  def getOutRetPer(inRetPer, retLevCurrent, retLevBsln):
    nx = retLevCurrent.shape[1]
    ny = retLevCurrent.shape[2]
    nOutRL = retLevBsln.shape[0]
    outRetPer = np.zeros([nOutRL, nx, ny])*np.nan
    for ix in range(nx):
      for iy in range(ny):
        rlcri = retLevCurrent[:, ix, iy]
        if np.sum(np.isnan(rlcri)) > 0:
          continue
        rlbsln = retLevBsln[:, ix, iy]
        outRetPer[:, ix, iy] = interp1d(rlcri, inRetPer, axis=0, fill_value='extrapolate')(rlbsln)
    return outRetPer
    
  interpFunc = None
  bslnRetLev_, interpFunc = getRetLevAtYear(retLev, rlYrs, bslnYear, interpFunc)
  bslnRetLev = getOutRetLev(bslnRetLev_, inRetPer, outRetPer)

  print('  elaborating ...')
  noutWls = len(wls)
  shp_ = bslnRetLev.shape
  shpOut = [noutWls, shp_[0], shp_[1], shp_[2]]
  outYrRetPer = np.zeros(shpOut)*np.nan
  outYrRetLev = np.zeros(shpOut)*np.nan
  for wl, iwl in zip(wls, range(noutWls)):
    ywls = getWarmingLevels(scen, wl)
    if ywls == None:
      continue
    outYr = ywls[model]
    yrRetLev, interpFunc = getRetLevAtYear(retLev, rlYrs, outYr, interpFunc)
    outYrRetLev[iwl, :, :, :] = getOutRetLev(yrRetLev, inRetPer, outRetPer)
    outYrRetPer[iwl, :, :, :] = getOutRetPer(inRetPer, yrRetLev, bslnRetLev)
    
  outYrRetPer[outYrRetPer < 1] = 1
  print('  saving the output ...')
  if os.path.isfile(outputNcFlPath):
    os.remove(outputNcFlPath)
  dsout = netCDF4.Dataset(outputNcFlPath, 'w')
  dsout.createDimension('x', len(x))
  dsout.createDimension('y', len(y))
  dsout.createDimension('warming_lev', noutWls)
  dsout.createDimension('baseline_rp', len(outRetPer))

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

  bslnRpNc = dsout.createVariable('baseline_rp', 'f4', ('baseline_rp'))
  bslnRpNc.description = 'return period at the baseline (years)'
  bslnRpNc[:] = outRetPer

  bslnYrNc = dsout.createVariable('baseline_year', 'i4')
  bslnYrNc.description = 'baseline year'
  bslnYrNc[:] = bslnYear

  bslnRetLevNc = dsout.createVariable('baseline_return_level', 'f4', ('baseline_rp', 'x', 'y'))
  bslnRetLevNc.description = 'return levels at baseline'
  bslnRetLevNc[:] = bslnRetLev

  retPerNc = dsout.createVariable('baseline_rp_shift', 'f4', ('warming_lev', 'baseline_rp', 'x', 'y'))
  retPerNc.description = 'shifted return periods of the baseline return values (years)'
  retPerNc[:] = outYrRetPer

  retLevNc = dsout.createVariable('return_level', 'f4', ('warming_lev', 'baseline_rp', 'x', 'y'))
  retLevNc.description = 'return levels at warming levels (m**3)'
  retLevNc[:] = outYrRetLev

  dsout.close()
  

def loopModels(inputDir, inputFlPattern, outputDir):

  
  infls = [fl for fl in os.listdir(inputDir) if re.match(inputFlPattern, fl)]
  for fl in infls:
    print('elaborating file ' + fl)
    flpth = os.path.join(inputDir, fl)
    outflpth = os.path.join(outputDir, fl.replace('projection_', 'returnPeriodShift_'))
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
  outputDir = '/ClimateRun4/multi-hazard/eva/lowFlowWarmSeason/'

 # precipitations
 #inputDir = '/ClimateRun4/multi-hazard/eva/'
 #inputDir = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/lisfloodEVA_pr/test'
 #inputFlPattern = 'projection_pr_(rcp45|rcp85)_(.*)_statistics.nc'
 #outputDir = '/ClimateRun4/multi-hazard/eva/prFrequencyShift/'

  loopModels(inputDir, inputFlPattern, outputDir)

