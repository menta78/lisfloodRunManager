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
from getWarmingLevels import getWarmingLevels
from scipy.interpolate import interp1d


def extract1Model(inputNcFlPath, outputNcFlPath):
  outRetPer = [30.]
  outWarmingLevs = [1.5, 2.0, 3.0]

  m = re.match('(.*)/lonlat_projection_windYMax_(.*)_(.*).nc', inputNcFlPath)
  scen = m.group(1)[0]
  mdl = m.group(2)[0]

  wls = [getWarmingLevels(scen, wl) for wl in outWarmingLevs]

  print('  loading the data ...')
  dsin = netCDF4.Dataset(inputNcFlPath)
  x = dsin.variables['lon'][:]
  y = dsin.variables['lat'][:]
  inRetPer = dsin.variables['retper'][:]
  tmnc = dsin.variables['time']
  tm = netCDF4.num2date(tmnc[:], tmnc.units, tmnc.calendar)
  ystart = tm[0].year
  rlYrs = ystart + np.arange(len(tm))
  dsin.close()

  output = []
  for wl in outWarmingLevs:
    wlyrs = wls[wl]
    if wlyrs is None:
      continue
    wlyr = wlyrs[mdl]
    iyr = np.where(rlYrs == wlyr)
    wlRetPer = 
  

def loopModels():
  inputDir = '/ClimateRun4/multi-hazard/eva/'
  inputFlPattern = 'projection_dis_rcp([48])5_(.*)_wuChang_statistics.nc'

  outputDir = '/ClimateRun4/multi-hazard/eva/kees/'
  outputDir = '/ClimateRun/menta/xKees/'
  
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
