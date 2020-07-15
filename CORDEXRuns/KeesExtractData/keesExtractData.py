"""
come anticipato l'altro giorno, per il lavoro con Kees, il ragazzo di Deltares, dovremmo stimare la variazione di frequenza tra alluvioni presenti e future.
Potresti calcolarlo per le proiezioni che hai girato con Lisflood per l'Europa?
Ricapitolando, per ciascun tempo di ritorno delle portate al colmo di piena: 10, 20, 50, 100, 200, 500 anni nella baseline, bisogna stimare a quanti anni questo corrisponde in 3 future time slices. Le time slices sono cosi' definite:
 
Baseline:   1981-2010
Window 1: 2016-2045
Window 2: 2041-2070
Window 3: 2071-2100

Il numero totale di mappe sara':
2 (RCP) x 11 (proiezioni climatiche) x 6 (tempi di ritorno) x 3 (future time windows) = 396
"""


import netCDF4
import numpy as np
import os, re
from scipy.interpolate import interp1d


def extract1Model(inputNcFlPath, outputNcFlPath):
 # years for Kees
  bslnYear = 2003

  w0Year = 1996
  w1Year = 2031
  w2Year = 2056
  w3Year = 2086

 # years for Claudia Hahn
  bslnYear = 1996
  w0Year = 1996
  w1Year = 2025
  w2Year = 2055
  w3Year = 2085

  outYrs = [w0Year, bslnYear, w1Year, w2Year, w3Year]
  
  outRetPer = [10., 20., 50., 100., 200., 500.]

  print('  loading the data ...')
  dsin = netCDF4.Dataset(inputNcFlPath)
  x = dsin.variables['x'][:]
  y = dsin.variables['y'][:]
  inRetPer = dsin.variables['return_period'][:]
  retLev = dsin.variables['rl'][:]
  rlYrs = dsin.variables['year'][:]
  dsin.close()

  ncFloodProtectionRp = './floodProtection_v2019_5km_ni2.nc'
  dsfp = netCDF4.Dataset(ncFloodProtectionRp)
 #retPerFloodProtectionBlsn_ = dsfp.variables['floodProtection_v2019_5km_nibbled.tif'][:]
  yfp = dsfp.variables['y'][:]
  ifirstY = np.where(yfp == y[0])[0][0]
  xfp = dsfp.variables['x'][:]
  retPerFloodProtectionBlsn_ = dsfp.variables['floodProtection_v2019_5km_nibbled2.tif'][:]
 #retPerFloodProtectionBlsn_ = np.concatenate(([retPerFloodProtectionBlsn_[0, :]], retPerFloodProtectionBlsn_), 0)
  retPerFloodProtectionBlsn = retPerFloodProtectionBlsn_[ifirstY:ifirstY + 950, 0:1000].transpose().astype(np.double)
  dsfp.close()

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
    interpFunc = interp1d(inRetPer, inRetLev, axis=0, fill_value='extrapolate')
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

  def getOutRetPerFloodProt(inRetPer, retLevCurrent, bslnRetPerFloodProtection, bslnRetLevAll):
    nx = retLevCurrent.shape[1]
    ny = retLevCurrent.shape[2]
    nOutRL = bslnRetLevAll.shape[0]
    outRetPer = np.zeros([nx, ny])*np.nan
    for ix in range(nx):
      for iy in range(ny):
        rlcri = retLevCurrent[:, ix, iy]
        if np.sum(np.isnan(rlcri)) > 0:
          continue
        rlbsln = interp1d(inRetPer, bslnRetLevAll[:, ix, iy], fill_value='extrapolate')(bslnRetPerFloodProtection[ix, iy])
        outRetPer[ix, iy] = interp1d(rlcri, inRetPer, axis=0, fill_value='extrapolate')(rlbsln)
    return outRetPer
    
  interpFunc = None
  bslnRetLev_, interpFunc = getRetLevAtYear(retLev, rlYrs, bslnYear, interpFunc)
  bslnRetLev = getOutRetLev(bslnRetLev_, inRetPer, outRetPer)
  bslnRetLevAll = getOutRetLev(bslnRetLev_, inRetPer, inRetPer)

  print('  elaborating ...')
  noutYrs = len(outYrs)
  shp_ = bslnRetLev.shape
  shpOut = [len(outYrs), shp_[0], shp_[1], shp_[2]]
  outYrRetPer = np.zeros(shpOut)*np.nan
  outYrRetLev = np.zeros(shpOut)*np.nan
  outYrRetPerFP = np.zeros([len(outYrs), shp_[1], shp_[2]])*np.nan
  for outYr, iOutYr in zip(outYrs, range(noutYrs)):
    yrRetLev, interpFunc = getRetLevAtYear(retLev, rlYrs, outYr, interpFunc)
    outYrRetLev[iOutYr, :, :, :] = getOutRetLev(yrRetLev, inRetPer, outRetPer)
    outYrRetPer[iOutYr, :, :, :] = getOutRetPer(inRetPer, yrRetLev, bslnRetLev)
    outYrRetPerFP[iOutYr, :, :] = getOutRetPerFloodProt(inRetPer, yrRetLev, retPerFloodProtectionBlsn, bslnRetLevAll)

  outYrRetPer[outYrRetPer<1] = 1
  outYrRetPerFP[outYrRetPerFP<1] = 1
    
  print('  saving the output ...')
  if os.path.isfile(outputNcFlPath):
    os.remove(outputNcFlPath)
  dsout = netCDF4.Dataset(outputNcFlPath, 'w')
  dsout.createDimension('x', len(x))
  dsout.createDimension('y', len(y))
  dsout.createDimension('year', noutYrs)
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

  yearnc = dsout.createVariable('year', 'i4', ('year'))
  yearnc.description = 'year'
  yearnc[:] = outYrs

  bslnRpNc = dsout.createVariable('baseline_rp', 'f4', ('baseline_rp'))
  bslnRpNc.description = 'return period at the baseline (years)'
  bslnRpNc[:] = outRetPer

  bslnYrNc = dsout.createVariable('baseline_year', 'i4')
  bslnYrNc.description = 'baseline year'
  bslnYrNc[:] = bslnYear

  retPerNc = dsout.createVariable('baseline_rp_shift', 'f4', ('year', 'baseline_rp', 'x', 'y'))
  retPerNc.description = 'shifted return periods of the baseline return values (years)'
  retPerNc[:] = outYrRetPer

  retLevNc = dsout.createVariable('return_level', 'f4', ('year', 'baseline_rp', 'x', 'y'))
  retLevNc.description = 'return levels at years (m**3)'
  retLevNc[:] = outYrRetLev

  bslnRpFloodProt = dsout.createVariable('baseline_rp_fp_shift', 'f4', ('year', 'x', 'y'))
  bslnRpFloodProt.description = 'shifted return period of flood protection'
  bslnRpFloodProt[:] = outYrRetPerFP

  dsout.close()
  

def loopModels():
  inputDir = '/ClimateRun4/multi-hazard/eva/'
  inputFlPattern = 'projection_dis_rcp([48])5_(.*)_wuConst_statistics.nc'

  outputDir = '/ClimateRun4/multi-hazard/eva/kees/'
  outputDir = '/ClimateRun/menta/xKees/'
  outputDir = '/DATA/mentalo/Dropbox/notSynced/xClaudiaHahn/'
  
  infls = [fl for fl in os.listdir(inputDir) if re.match(inputFlPattern, fl)]
  for fl in infls:
    print('elaborating file ' + fl)
    flpth = os.path.join(inputDir, fl)
    outflpth = os.path.join(outputDir, fl.replace('projection_', 'returnPeriodShift_'))
    print('  output file path: ' + outflpth)
    extract1Model(flpth, outflpth)


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
