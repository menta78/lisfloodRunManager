import netCDF4
import numpy as np
import os, re
from scipy.interpolate import interp1d
from getWarmingLevels import getWarmingLevels


def extract1Model(model, inputNcFlPath, outputNcFlPath):
  bslnYear = 1995
  wls = [1.5, 2.0, 3.0]
  noutWls = len(wls)
  
  outRetPer = [10., 20., 50., 100., 200., 500.]

  print('  loading the data ...')
  dsin = netCDF4.Dataset(inputNcFlPath)
  lon = dsin.variables['lon'][:]
  lat = dsin.variables['lat'][:]
  inRetPer = dsin.variables['return_period'][:]
  retLev = dsin.variables['rl'][:]
  rlYrs = dsin.variables['year'][:]
  dsin.close()

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
  shp_ = bslnRetLev.shape
  shpOut = [noutWls, shp_[0], shp_[1], shp_[2]]
  outYrRetPer = np.zeros(shpOut)*np.nan
  outYrRetLev = np.zeros(shpOut)*np.nan
  for wl, iwl in zip(wls, range(len(wls))):
    wly = getWarmingLevels('rcp85', wl)
    outYr = wly[model]
    yrRetLev, interpFunc = getRetLevAtYear(retLev, rlYrs, outYr, interpFunc)
    outYrRetLev[iwl, :, :, :] = getOutRetLev(yrRetLev, inRetPer, outRetPer)
    outYrRetPer[iwl, :, :, :] = getOutRetPer(inRetPer, yrRetLev, bslnRetLev)
    
  outYrRetPer[outYrRetPer < 1] = 1
  print('  saving the output ...')
  if os.path.isfile(outputNcFlPath):
    os.remove(outputNcFlPath)
  dsout = netCDF4.Dataset(outputNcFlPath, 'w')
  dsout.createDimension('lat', len(lat))
  dsout.createDimension('lon', len(lon))
  dsout.createDimension('warming_lev', noutWls)
  dsout.createDimension('baseline_rp', len(outRetPer))

  xnc = dsout.createVariable('lon', 'f8', ('lon'))
  xnc.description = 'longitude'
  xnc.long_name = 'longitude'
  xnc.standard_name = 'longitude'
  xnc.units = 'degrees_east'
  xnc[:] = lon

  ync = dsout.createVariable('lat', 'f8', ('lat'))
  ync.description = 'latitude'
  ync.description = 'latitude'
  ync.long_name = 'latitude'
  ync.standard_name = 'latitude'
  ync.units = 'degrees_north'
  ync[:] = lat

  wlnc = dsout.createVariable('warming_lev', 'f4', ('warming_lev'))
  wlnc.description = 'warming level'
  wlnc[:] = wls

  bslnRpNc = dsout.createVariable('baseline_rp', 'f4', ('baseline_rp'))
  bslnRpNc.description = 'return period at the baseline (years)'
  bslnRpNc[:] = outRetPer

  bslnYrNc = dsout.createVariable('baseline_year', 'i4')
  bslnYrNc.description = 'baseline year'
  bslnYrNc[:] = bslnYear

  bslnRetLevNc = dsout.createVariable('baseline_return_level', 'f4', ('baseline_rp', 'lon', 'lat'))
  bslnRetLevNc.description = 'return levels at baseline'
  bslnRetLevNc[:] = bslnRetLev

  retPerNc = dsout.createVariable('baseline_rp_shift', 'f4', ('warming_lev', 'baseline_rp', 'lon', 'lat'))
  retPerNc.description = 'shifted return periods of the baseline return values (years)'
  retPerNc[:] = outYrRetPer
  retPerNc.coordinates = 'warming_lev baseline_rp lon lat'

  retLevNc = dsout.createVariable('return_level', 'f4', ('warming_lev', 'baseline_rp', 'lon', 'lat'))
  retLevNc.description = 'return levels at warming levels (m**3)'
  retLevNc[:] = outYrRetLev
  retLevNc.coordinates = 'warming_lev baseline_rp lon lat'

  dsout.close()
  

def loopModels():
  inputDir = '../tsEvaOut'
  inputFlPattern = 'projection_HELIX_dis_rcp85_r([1-7])_statistics.nc'

  outputDir = '../returnPeriodShift/'
  
  infls = [fl for fl in os.listdir(inputDir) if re.match(inputFlPattern, fl)]
  for fl in infls:
    print('elaborating file ' + fl)
    m = re.match('projection_HELIX_dis_rcp85_(r[1-7])_statistics.nc', fl)
    mdl = m.groups()[0]
    flpth = os.path.join(inputDir, fl)
    outflpth = os.path.join(outputDir, fl.replace('projection_', 'returnPeriodShift_'))
    print('  output file path: ' + outflpth)
    extract1Model(mdl, flpth, outflpth)


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
  loopModels()
