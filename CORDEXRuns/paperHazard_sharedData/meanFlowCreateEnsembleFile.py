import re, os
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import gridspec
from alphaBetaLab import abFixBasemap
from mpl_toolkits import basemap as bm
from scipy.interpolate import interp1d
import netCDF4
import pickle

from sharedDataUtil import *


ncdir = '/ClimateRun4/multi-hazard/eva/prFrequencyShift_std/'
outputNcFlPath = './precipitationEnsemble.nc'


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

def doLoadData(warmingLev=2):

  mdlchng = []
  mdlRetLev = []

  mskDs = netCDF4.Dataset('upArea.nc')
  upArea = mskDs.variables['upArea'][:]
  msk = np.isnan(upArea).transpose()
  mskDs.close()

  fls = [f for f in os.listdir(ncdir) if re.match('meanDisChng_(.*).nc', f)]
  fls.sort()
  for f, ifl in zip(fls, range(len(fls))):
    fpth = os.path.join(ncdir, f)
    print('  loading ' + fpth)
    ds = netCDF4.Dataset(fpth)

    if ifl == 0:
      lon = ds.variables['lon'][:]
      lat = ds.variables['lat'][:]

    wlev = ds.variables['warming_lev'][:]
    iwlev = wlev == warmingLev
    vls = ds.variables['baseline_mean_dis'][:]
    rlChng = ds.variables['perc_change'][iwlev, :, :].squeeze()
    rlChng[msk] = np.nan
    rlChng[np.abs(rlChng) >= 10000] = np.nan
    mdlchng.append(rlChng)
    
  mdlchng = np.array(mdlchng)
  mdn = np.nanmedian(mdlchng, 0)
 #mdn = np.nanmean(np.array(mdlchng), 0)

  return lon, lat, mdn, mdlchng


def doLoadBaseline():

  mdlmns = []

  mskDs = netCDF4.Dataset('upArea.nc')
  upArea = mskDs.variables['upArea'][:]
  msk = np.isnan(upArea).transpose()
  mskDs.close()

  fls = [f for f in os.listdir(ncdir) if re.match('meanDisChng_(.*).nc', f)]
  fls.sort()
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
    if 'baseline_mean_dis' in ds.variables:
      meanvl = ds.variables['baseline_mean_dis'][:, :].squeeze()
    else:
      meanvl = np.zeros([len(x), len(y)])*np.nan
   #iwlev = wlev == 1.5
   #meanvl = ds.variables['return_level'][iwlev, irp, :, :].squeeze()
    meanvl[msk] = np.nan
    mdlmns.append(meanvl)
    
  mdlmns = np.array(mdlmns)
  mdn = np.nanmedian(np.array(mdlmns), 0)
 #mdn = np.nanmean(np.array(mdlmns), 0)

  return lon, lat, x, y, mdn, mdlmns
    

  
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
  lon, lat, futRp_15, _, rlByMdl_15 = doLoadData(warmingLev=1.5)
  lon, lat, futRp_20, _, rlByMdl_20 = doLoadData(warmingLev=2.0)
  lon, lat, futRp_30, _, rlByMdl_30 = doLoadData(warmingLev=3.0)
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
    


def doPlotRetLevChng(ax, rlChng, lon, lat, txt, mp):
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
  pltvls = rlChng
  x, y = mp(lon, lat)
  sc = plt.scatter(x, y, s=1, c=pltvls, vmin=-40, vmax=40, linewidth=0, cmap='bwr_r')
  txtpos = mp(-22, 68)
  plt.annotate(txt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=19)
  return sc, mp


  
def plotRlChange15_20_30deg(): 
  lon, lat, _, meanDisChng15_mdl = doLoadData(warmingLev=1.5)
  lon, lat, _, meanDisChng20_mdl = doLoadData(warmingLev=2.0)
  lon, lat, _, meanDisChng30_mdl = doLoadData(warmingLev=3.0)
  lon, lat, x, y, bslnMean, bslnMeanByMdl = doLoadBaseline()

  meanDisChng15 = np.nanmedian(meanDisChng15_mdl, 0)
  meanDisChng20 = np.nanmedian(meanDisChng20_mdl, 0)
  meanDisChng30 = np.nanmedian(meanDisChng30_mdl, 0)

  f = plt.figure(figsize=(24,9))

  gs = gridspec.GridSpec(2, 3, height_ratios=[1,.04])

  ax1 = plt.subplot(gs[0, 0])
  txt = '$1.5^\circ C$'
  mp = None
  sc, mp = doPlotRetLevChng(ax1, meanDisChng15, lon, lat, txt, mp)

  ax2 = plt.subplot(gs[0, 1])
  txt = '$2.0^\circ C$'
  sc, mp = doPlotRetLevChng(ax2, meanDisChng20, lon, lat, txt, mp)

  ax3 = plt.subplot(gs[0, 2])
  txt = '$3.0^\circ C$'
  sc, mp = doPlotRetLevChng(ax3, meanDisChng30, lon, lat, txt, mp)

  cax = plt.subplot(gs[1, :])
  cb = plt.colorbar(sc, ax=ax2, cax=cax, orientation='horizontal')
 #cb.ax.set_xticklabels(['<20', '20-40', '40-70', '70-100', '100-150', '150-250', '250-400', '>400'], fontsize=15)
  cb.set_label('% change', fontsize=16)

  ax1.set_aspect('auto')
  ax2.set_aspect('auto')
  ax3.set_aspect('auto')
  cax.set_aspect('auto')
  plt.tight_layout()

  f.savefig('rlPercChng.png', dpi=200)


def saveEnsembleFile():
  prototypeFlPth = 'upArea.nc' 

  lon, lat, _, meanDisChng15_mdl = doLoadData(warmingLev=1.5)
  lon, lat, _, meanDisChng20_mdl = doLoadData(warmingLev=2.0)
  lon, lat, _, meanDisChng30_mdl = doLoadData(warmingLev=3.0)
  lon, lat, _, meanDisChng40_mdl = doLoadData(warmingLev=4.0)
  lon, lat, x, y, bslnMean, bslnMeanByMdl = doLoadBaseline()

  meanDisChng15 = np.nanmedian(meanDisChng15_mdl, 0)
  meanDisChng20 = np.nanmedian(meanDisChng20_mdl, 0)
  meanDisChng30 = np.nanmedian(meanDisChng30_mdl, 0)
  meanDisChng40 = np.nanmedian(meanDisChng40_mdl, 0)

  sing15 = getSignificance(meanDisChng15, meanDisChng15_mdl)
  sing20 = getSignificance(meanDisChng20, meanDisChng20_mdl)
  sing30 = getSignificance(meanDisChng30, meanDisChng30_mdl)
  sing40 = getSignificance(meanDisChng40, meanDisChng40_mdl)

  dsout = netCDF4.Dataset(outputNcFlPath, 'w')
  dsout.title = 'Future Changes of River Runoff in Europe (Mentaschi et al. 2020). Annual means'
  dsout.institution = 'European Commission, Joint European Research Center (JRC)'
  dsout.summary = 'Projected changes of annual mean river runoff at 1.5°, 2.0°, 3.0°, 4.0° of global warming. From the project PESETA IV'
  dsout.createDimension('x', len(x))
  dsout.createDimension('y', len(y))

  dsprot = netCDF4.Dataset(prototypeFlPth)
  xncpt = dsprot.variables['x']
  xnc = dsout.createVariable('x', xncpt.datatype, xncpt.dimensions)
  xnc[:] = xncpt[:]
  xnc.setncatts(xncpt.__dict__)

  yncpt = dsprot.variables['y']
  ync = dsout.createVariable('y', yncpt.datatype, yncpt.dimensions)
  ync[:] = yncpt[:]
  ync.setncatts(yncpt.__dict__)

  laeancpt = dsprot.variables['laea']
  laeanc = dsout.createVariable('laea', laeancpt.datatype, laeancpt.dimensions)
  laeanc[:] = laeancpt[:]
  laeanc.setncatts(laeancpt.__dict__)
  dsprot.close()
  
  lonnc = dsout.createVariable('lon', 'f8', ('x', 'y'))
  lonnc.description = 'longitude mtx'
  lonnc[:] = lon

  latnc = dsout.createVariable('lat', 'f8', ('x', 'y'))
  latnc.description = 'latitude mtx'
  latnc[:] = lat

  bslnRetLevNc = dsout.createVariable('baseline_median', 'f4', ('x', 'y'))
  bslnRetLevNc.description = 'magnitude of the baseline annual mean river runoff'
  bslnRetLevNc.units = 'm^3 * s^{-1}'
  bslnRetLevNc[:] = bslnMean

  rlChng15 = dsout.createVariable('median_perc_chng_15', 'f4', ('x', 'y'))
  rlChng15.description = 'percentage changes in magnitude of the annual mean river runoff, at warming level 1.5°'
  rlChng15[:] = meanDisChng15

  rlChng20 = dsout.createVariable('median_perc_chng_20', 'f4', ('x', 'y'))
  rlChng20.description = 'percentage changes in magnitude of the annual mean river runoff, at warming level 2.0°'
  rlChng20[:] = meanDisChng20

  rlChng30 = dsout.createVariable('median_perc_chng_30', 'f4', ('x', 'y'))
  rlChng30.description = 'percentage changes in magnitude of the annual mean river runoff, at warming level 3.0°'
  rlChng30[:] = meanDisChng30

  rlChng40 = dsout.createVariable('median_perc_chng_40', 'f4', ('x', 'y'))
  rlChng40.description = 'percentage changes in magnitude of the annual mean river runoff, at warming level 4.0°'
  rlChng40[:] = meanDisChng40

  sign15Nc = dsout.createVariable('significant_15', 'i1', ('x', 'y'))
  sign15Nc.description = 'significance of the 1.5° projected change. 1: significant, 0: not significant'
  sign15Nc[:] = sing15

  sign20Nc = dsout.createVariable('significant_20', 'i1', ('x', 'y'))
  sign20Nc.description = 'significance of the 2.0° projected change. 1: significant, 0: not significant'
  sign20Nc[:] = sing20

  sign30Nc = dsout.createVariable('significant_30', 'i1', ('x', 'y'))
  sign30Nc.description = 'significance of the 3.0° projected change. 1: significant, 0: not significant'
  sign30Nc[:] = sing30

  sign40Nc = dsout.createVariable('significant_40', 'i1', ('x', 'y'))
  sign40Nc.description = 'significance of the 4.0° projected change. 1: significant, 0: not significant'
  sign40Nc[:] = sing40

  dsout.close()

  
  
  
if __name__ == '__main__':
  import pdb; pdb.set_trace()

 #ncdir = '/ClimateRun4/multi-hazard/eva/prFrequencyShift_std/'
 #outputNcFlPath = './precipitationEnsemble.nc'
 #plotFreqChange15_20_30deg()
 #saveEnsembleFile()

 #ncdir = '/DATA/mentalo/Dropbox/notSynced/xEamonn'
  ncdir = '/ClimateRun4/multi-hazard/eva/berny/'
  outputNcFlPath = '/DATA/mentalo/Dropbox/notSynced/pesetaRunoffRpShift/disEnsemble_annualMean.nc'
 #plotRlChange15_20_30deg()
  saveEnsembleFile()

  plt.show()

