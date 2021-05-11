import re, os
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import gridspec
from alphaBetaLab import abFixBasemap
from mpl_toolkits import basemap as bm
from scipy.interpolate import interp1d
import netCDF4
import pickle
import glob

import getWarmingLevels

ncdir = None
outputNcFlPath = None
diagnosticsDataDir = None
lowflowthreshold = .05
lowflowthreshold = .03


def loadFrqDataForModel(diagnosticsDataDir, scn, mdl, warmingLev):
  if warmingLev == 0:
    ywl = 1995 # baseline
  else:
    wls = getWarmingLevels.getWarmingLevels(scn, warmingLev)
    ywl = wls[mdl]
  ymin = max(ywl-15, 1981)
  ymax = min(ywl+14, 2100)
  yrsMdl = range(ymin, ymax+1)
  dt = None
  for iyr, yr in zip(range(len(yrsMdl)), yrsMdl):
    flPth = os.path.join(diagnosticsDataDir, '_'.join(['droughtFrqDiagnostics', mdl, scn, str(yr)])) + '.0.npy'
    if not os.path.isfile(flPth):
      print('     ... file ' + flPth + ' not found, skipping ...')
      continue
    dti = np.load(flPth)
    nx, ny = dti.shape
    dt = np.zeros([30, nx, ny])*np.nan if dt is None else dt
    dt[iyr] = dti
  mn = np.nanmedian(dt, 0)
  return 1/mn

def getFrqDataPercChng(diagnosticsDataDir, scn, mdl, warmingLev, baseline):
  futFq = loadFrqDataForModel(diagnosticsDataDir, scn, mdl, warmingLev)
  baseline = loadFrqDataForModel(diagnosticsDataDir, scn, mdl, 0) if baseline is None else baseline
  fqdlt = (futFq - baseline)/baseline
  return fqdlt, baseline
  
def generateFrqFileForModel(diagnosticsDataDir, scn, mdl, outdir):
  prototypeFlPth = 'upArea.nc' 
  outputNcFlPath = os.path.join(outdir, 'frq_' + mdl.replace('-', '') + '_' + scn + '.nc') 
  print('  ... saving file ' + outputNcFlPath)
  
  dsout = netCDF4.Dataset(outputNcFlPath, 'w')

  dsprot = netCDF4.Dataset(prototypeFlPth)
  xncpt = dsprot.variables['x']
  x = xncpt[:]
  dsout.createDimension('x', len(x))
  xnc = dsout.createVariable('x', xncpt.datatype, xncpt.dimensions)
  xnc[:] = x
  xnc.setncatts(xncpt.__dict__)

  yncpt = dsprot.variables['y']
  y = yncpt[:]
  dsout.createDimension('y', len(y))
  ync = dsout.createVariable('y', yncpt.datatype, yncpt.dimensions)
  ync[:] = y
  ync.setncatts(yncpt.__dict__)

  laeancpt = dsprot.variables['laea']
  laeanc = dsout.createVariable('laea', laeancpt.datatype, laeancpt.dimensions)
  laeanc[:] = laeancpt[:]
  laeanc.setncatts(laeancpt.__dict__)
  dsprot.close()

  wlevs = [1.5, 2.0, 3.0, 4.0]
  baseline = None
  for wlev in wlevs:
    if wlev in [3.0, 4.0] and scn == 'rcp45':
      dlt = np.zeros( (len(x), len(y)) )*np.nan
    else:
      dlt, baseline = getFrqDataPercChng(diagnosticsDataDir, scn, mdl, wlev, baseline)
      dlt = dlt*100

    wlevstr = str(wlev).replace('.', '')
    varname = 'frequency_prc_chng_' + wlevstr
    fqshift = dsout.createVariable(varname, 'f4', ('x', 'y'))
    fqshift[:] = dlt
  dsout.close() 


def doCreateAllFiles(diagnosticsDataDir, outdir):
  scenarios = ['rcp85', 'rcp45']
  wls = getWarmingLevels.getWarmingLevels('rcp85', 1.5)
  models = wls.keys()
  for scn in scenarios:
    for mdl in models:
      generateFrqFileForModel(diagnosticsDataDir, scn, mdl, outdir)

def plotMedian(outdir, varname='frequency_prc_chng_40'):
  fls = glob.glob(os.path.join(outdir, '*.nc'))
  vlss = []
  for fl in fls:
    ds = netCDF4.Dataset(fl)
    vls = ds.variables[varname][:]
    vlss.append(vls)
    ds.close()
  md = np.nanmedian(np.array(vlss), 0)

  def getLonLat():
    lonLatFile = 'lonlat.nc'
    ds = netCDF4.Dataset(lonLatFile)
    lon = ds.variables['lon'][:]
    lat = ds.variables['lat'][:]
    ds.close()
    return lon, lat

  lon, lat = getLonLat()
  lon, lat = lon.transpose(), lat.transpose()
  cnd = ~np.isnan(md)

  plt.figure()
  plt.scatter(lon[cnd], lat[cnd], s=1, c=md[cnd], vmin=-100, vmax=100, linewidth=0, cmap='bwr')
  plt.colorbar()

  oldmedianfile = '/DATA/mentalo/Dropbox/notSynced/xAlessandra/minDisWrmSsnEnsemble_20y_meanFrq_90_10.nc'
  ds = netCDF4.Dataset(oldmedianfile)
  oldmd = ds.variables[varname][:]
  ds.close()
  plt.figure()
  plt.scatter(lon[cnd], lat[cnd], s=1, c=oldmd[cnd], vmin=-100, vmax=100, linewidth=0, cmap='bwr')
  plt.colorbar()

  plt.show()


if __name__ == '__main__':
  diagnosticsDataDir = '/DATA/ClimateRuns/droughtFreqDiagnostics/'
  outdir = '/DATA/mentalo/Dropbox/notSynced/xAlessandra/dataByModel/'
  import pdb; pdb.set_trace()
 #doCreateAllFiles(diagnosticsDataDir, outdir)
  plotMedian(outdir)

