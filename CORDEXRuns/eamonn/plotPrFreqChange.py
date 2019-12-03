import re, os
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import gridspec
from mpl_toolkits import basemap as bm
from scipy.interpolate import interp1d
import netCDF4
import pickle



def doPlotMinDisFreq(ax, futRp, lon, lat, txt, mp):
  if mp == None:
   #llcrnrlon = -11.5
   #llcrnrlat = 23
   #urcrnrlon = 44
   #urcrnrlat = 74

   #llcrnrlon = -25
   #llcrnrlat = 31
   #urcrnrlon = 37
   #urcrnrlat = 71.5

    llcrnrlon = -25
    llcrnrlat = 25
    urcrnrlon = 44
    urcrnrlat = 71.5

    mp = bm.Basemap(llcrnrlon=llcrnrlon, llcrnrlat=llcrnrlat, urcrnrlon=urcrnrlon, 
             urcrnrlat=urcrnrlat, resolution='l', projection='lcc', lon_0=-15, lat_1=-15, lat_2=10)
  plt.axes(ax)
  mp.drawcoastlines(linewidth=.25)
  pltvls = np.zeros(futRp.shape)*np.nan
  pltvls[futRp <= 20] = 1
  pltvls[np.logical_and(futRp > 20, futRp <= 40)] = 2
  pltvls[np.logical_and(futRp > 40, futRp <= 70)] = 3
  pltvls[np.logical_and(futRp > 70, futRp <= 100)] = 4
  pltvls[np.logical_and(futRp > 100, futRp <= 150)] = 5
  pltvls[np.logical_and(futRp > 150, futRp <= 250)] = 6
  pltvls[np.logical_and(futRp > 250, futRp <= 400)] = 7
  pltvls[futRp > 400] = 8
  x, y = mp(lon, lat)
  sc = plt.scatter(x, y, s=1, c=pltvls, vmin=1, vmax=8, linewidth=0, cmap='bwr')
  txtpos = mp(-22, 68)
  plt.annotate(txt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=19)
  return sc, mp


def doLoadData(warmingLev=2, retPer=100):

  mdlvls = []

  mskDs = netCDF4.Dataset('upArea.nc')
  upArea = mskDs.variables['upArea'][:]
  msk = np.isnan(upArea).transpose()
  mskDs.close()

  ncdir = '/ClimateRun4/multi-hazard/eva/prFrequencyShift_std/'
  fls = [f for f in os.listdir(ncdir) if re.match('(.*).nc', f)]
  for f, ifl in zip(fls, range(len(fls))):
    fpth = os.path.join(ncdir, f)
    print('  loading ' + fpth)
    ds = netCDF4.Dataset(fpth)

    if ifl == 0:
      lon = ds.variables['lon'][:]
      lat = ds.variables['lat'][:]

    wlev = ds.variables['warming_lev'][:]
    iwlev = wlev == warmingLev
    retpers = ds.variables['baseline_rp'][:]
    irp = retpers == retPer
    rpShift = ds.variables['baseline_rp_shift'][iwlev, irp, :, :].squeeze()
    rpShift[msk] = np.nan
    mdlvls.append(rpShift)
    
  mdn = np.nanmedian(np.array(mdlvls), 0)
 #mdn = np.nanmean(np.array(mdlvls), 0)

  return lon, lat, mdn


def doLoadBaseline(retPer=100):

  mdlvls = []

  mskDs = netCDF4.Dataset('upArea.nc')
  upArea = mskDs.variables['upArea'][:]
  msk = np.isnan(upArea).transpose()
  mskDs.close()

  ncdir = '/ClimateRun4/multi-hazard/eva/prFrequencyShift/'
  fls = [f for f in os.listdir(ncdir) if re.match('(.*).nc', f)]
  for f, ifl in zip(fls, range(len(fls))):
    fpth = os.path.join(ncdir, f)
    print('  loading ' + fpth)
    ds = netCDF4.Dataset(fpth)

    if ifl == 0:
      lon = ds.variables['lon'][:]
      lat = ds.variables['lat'][:]
      x = ds.variables['x'][:]
      y = ds.variables['y'][:]

    wlev = ds.variables['warming_lev'][:]
    retpers = ds.variables['baseline_rp'][:]
    irp = retpers == retPer
    if 'baseline_return_level' in ds.variables:
      retlev = ds.variables['baseline_return_level'][irp, :, :].squeeze()
    else:
      retlev = np.zeros([len(x), len(y)])*np.nan
   #iwlev = wlev == 1.5
   #retlev = ds.variables['return_level'][iwlev, irp, :, :].squeeze()
    retlev[msk] = np.nan
    mdlvls.append(retlev)
    
  mdn = np.nanmedian(np.array(mdlvls), 0)
 #mdn = np.nanmean(np.array(mdlvls), 0)

  return lon, lat, x, y, mdn
    

  
def plotFreqChange15_20deg(): 
 #cacheFl = 'plotMinDisFreqChange.cache'
 #if os.path.isfile(cacheFl):
 #  lon, lat, futRp_15, futRp_20 = pickle.load(open(cacheFl, 'rb'))
 #else:
 #  lon, lat, futRp_15 = doLoadData(warmingLev=1.5)
 #  lon, lat, futRp_20 = doLoadData(warmingLev=2.0)
 #  pickle.dump((lon, lat, futRp_15, futRp_20), open(cacheFl, 'wb'))
  lon, lat, futRp_15 = doLoadData(warmingLev=1.5)
  lon, lat, futRp_20 = doLoadData(warmingLev=2.0)

  f = plt.figure(figsize=(16,8))

  gs = gridspec.GridSpec(1, 3, width_ratios=[1,1,.05])

  ax1 = plt.subplot(gs[0])
  txt = '$1.5^\circ C$'
  mp = None
  sc, mp = doPlotMinDisFreq(ax1, futRp_15, lon, lat, txt, mp)

  ax2 = plt.subplot(gs[1])
  txt = '$2.0^\circ C$'
  sc, mp = doPlotMinDisFreq(ax2, futRp_20, lon, lat, txt, mp)

  cax = plt.subplot(gs[2])
  cb = plt.colorbar(sc, ax=ax2, cax=cax, ticks=np.arange(1,9))
  cb.ax.set_yticklabels(['<20', '20-40', '40-70', '70-100', '100-150', '150-250', '250-400', '>400'], fontsize=15)
  cb.set_label('years', fontsize=16)

  ax1.set_aspect('auto')
  ax2.set_aspect('auto')
  cax.set_aspect('auto')
  plt.tight_layout()

  f.savefig('retperDelta.png', dpi=200)
    

  
def plotFreqChange15_20_30deg(): 
  lon, lat, futRp_15 = doLoadData(warmingLev=1.5)
  lon, lat, futRp_20 = doLoadData(warmingLev=2.0)
  lon, lat, futRp_30 = doLoadData(warmingLev=3.0)
 #lon, lat, x, y, retLev = doLoadBaseline()

  f = plt.figure(figsize=(24,9))

  gs = gridspec.GridSpec(2, 3, height_ratios=[1,.04])

  ax1 = plt.subplot(gs[0, 0])
  txt = '$1.5^\circ C$'
  mp = None
  sc, mp = doPlotMinDisFreq(ax1, futRp_15, lon, lat, txt, mp)

  ax2 = plt.subplot(gs[0, 1])
  txt = '$2.0^\circ C$'
  sc, mp = doPlotMinDisFreq(ax2, futRp_20, lon, lat, txt, mp)

  ax3 = plt.subplot(gs[0, 2])
  txt = '$3.0^\circ C$'
  sc, mp = doPlotMinDisFreq(ax3, futRp_30, lon, lat, txt, mp)

  cax = plt.subplot(gs[1, :])
  cb = plt.colorbar(sc, ax=ax2, cax=cax, ticks=np.arange(1,9), orientation='horizontal')
  cb.ax.set_xticklabels(['<20', '20-40', '40-70', '70-100', '100-150', '150-250', '250-400', '>400'], fontsize=15)
  cb.set_label('years', fontsize=16)

  ax1.set_aspect('auto')
  ax2.set_aspect('auto')
  ax3.set_aspect('auto')
  cax.set_aspect('auto')
  plt.tight_layout()

  f.savefig('retperDelta.png', dpi=200)


def saveEnsembleFile():
  lon, lat, x, y, retLev = doLoadBaseline()
  lon, lat, futRp_15 = doLoadData(warmingLev=1.5)
  lon, lat, futRp_20 = doLoadData(warmingLev=2.0)
  lon, lat, futRp_30 = doLoadData(warmingLev=3.0)

  outputNcFlPath = './precipitationEnsemble.nc'
  dsout = netCDF4.Dataset(outputNcFlPath, 'w')
  dsout.createDimension('x', len(x))
  dsout.createDimension('y', len(y))
  
  lonnc = dsout.createVariable('lon', 'f8', ('x', 'y'))
  lonnc.description = 'longitude mtx'
  lonnc[:] = lon

  latnc = dsout.createVariable('lat', 'f8', ('x', 'y'))
  latnc.description = 'latitude mtx'
  latnc[:] = lat

  bslnRetLevNc = dsout.createVariable('baseline_return_level', 'f4', ('x', 'y'))
  bslnRetLevNc.description = 'return levels at baseline'
  bslnRetLevNc[:] = retLev

  rpshift15 = dsout.createVariable('baseline_rp_shift_15', 'f4', ('x', 'y'))
  rpshift15[:] = futRp_15

  rpshift20 = dsout.createVariable('baseline_rp_shift_20', 'f4', ('x', 'y'))
  rpshift20[:] = futRp_20

  rpshift30 = dsout.createVariable('baseline_rp_shift_30', 'f4', ('x', 'y'))
  rpshift30[:] = futRp_30

  dsout.close()

  
  
  
if __name__ == '__main__':
  import pdb; pdb.set_trace()
 #plotFreqChange15_20_30deg()
  saveEnsembleFile()
  plt.show()

