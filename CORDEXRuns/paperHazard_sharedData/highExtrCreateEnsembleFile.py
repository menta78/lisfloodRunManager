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

def doLoadData(warmingLev=2, retPer=100):

  mdlvls = []
  mdlRetLev = []

  mskDs = netCDF4.Dataset('upArea.nc')
  upArea = mskDs.variables['upArea'][:]
  msk = np.isnan(upArea).transpose()
  mskDs.close()

  fls = [f for f in os.listdir(ncdir) if re.match('returnPeriodShift_(.*).nc', f)]
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
    retpers = ds.variables['baseline_rp'][:]
    irp = retpers == retPer
    rpShift = ds.variables['baseline_rp_shift'][iwlev, irp, :, :].squeeze()
    rpShift[msk] = np.nan
    mdlvls.append(rpShift)
    retLev = ds.variables['return_level'][iwlev, irp, :, :].squeeze()
    mdlRetLev.append(retLev)
    
  mdlvls = np.array(mdlvls)
  mdn = np.nanmedian(mdlvls, 0)
 #mdn = np.nanmean(np.array(mdlvls), 0)
  mdlRetLev = np.array(mdlRetLev)

  return lon, lat, mdn, mdlvls, mdlRetLev


def doLoadBaseline(retPer=100):

  mdlvls = []

  mskDs = netCDF4.Dataset('upArea.nc')
  upArea = mskDs.variables['upArea'][:]
  msk = np.isnan(upArea).transpose()
  mskDs.close()

  fls = [f for f in os.listdir(ncdir) if re.match('returnPeriodShift_(.*).nc', f)]
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
    
  mdlvls = np.array(mdlvls)
  mdn = np.nanmedian(np.array(mdlvls), 0)
 #mdn = np.nanmean(np.array(mdlvls), 0)

  return lon, lat, x, y, mdn, mdlvls
    

  
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
  lon, lat, futRp_15, _, rlByMdl_15 = doLoadData(warmingLev=1.5)
  lon, lat, futRp_20, _, rlByMdl_20 = doLoadData(warmingLev=2.0)
  lon, lat, futRp_30, _, rlByMdl_30 = doLoadData(warmingLev=3.0)
  lon, lat, x, y, retLev, retLevByMdl = doLoadBaseline()
  
  retLevChng_15_mdl = (rlByMdl_15 - retLevByMdl)/retLevByMdl*100
  retLevChng_20_mdl = (rlByMdl_20 - retLevByMdl)/retLevByMdl*100
  retLevChng_30_mdl = (rlByMdl_30 - retLevByMdl)/retLevByMdl*100

  retLevChng_15 = np.nanmedian(retLevChng_15_mdl, 0)
  retLevChng_20 = np.nanmedian(retLevChng_20_mdl, 0)
  retLevChng_30 = np.nanmedian(retLevChng_30_mdl, 0)

  f = plt.figure(figsize=(24,9))

  gs = gridspec.GridSpec(2, 3, height_ratios=[1,.04])

  ax1 = plt.subplot(gs[0, 0])
  txt = '$1.5^\circ C$'
  mp = None
  sc, mp = doPlotRetLevChng(ax1, retLevChng_15, lon, lat, txt, mp)

  ax2 = plt.subplot(gs[0, 1])
  txt = '$2.0^\circ C$'
  sc, mp = doPlotRetLevChng(ax2, retLevChng_20, lon, lat, txt, mp)

  ax3 = plt.subplot(gs[0, 2])
  txt = '$3.0^\circ C$'
  sc, mp = doPlotRetLevChng(ax3, retLevChng_30, lon, lat, txt, mp)

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

  lon, lat, x, y, retLev, retLevByMdl = doLoadBaseline()
  lon, lat, futRp_15, _, rlByMdl_15 = doLoadData(warmingLev=1.5)
  lon, lat, futRp_20, _, rlByMdl_20 = doLoadData(warmingLev=2.0)
  lon, lat, futRp_30, _, rlByMdl_30 = doLoadData(warmingLev=3.0)
  lon, lat, futRp_40, _, rlByMdl_40 = doLoadData(warmingLev=4.0)

  retLevChng_15_mdl = (rlByMdl_15 - retLevByMdl)/retLevByMdl
  retLevChng_20_mdl = (rlByMdl_20 - retLevByMdl)/retLevByMdl
  retLevChng_30_mdl = (rlByMdl_30 - retLevByMdl)/retLevByMdl
  retLevChng_40_mdl = (rlByMdl_40 - retLevByMdl)/retLevByMdl

  retLevChng_15 = np.nanmedian(retLevChng_15_mdl, 0)
  retLevChng_20 = np.nanmedian(retLevChng_20_mdl, 0)
  retLevChng_30 = np.nanmedian(retLevChng_30_mdl, 0)
  retLevChng_40 = np.nanmedian(retLevChng_40_mdl, 0)

  sing15 = getSignificance(retLevChng_15, retLevChng_15_mdl)
  sing20 = getSignificance(retLevChng_20, retLevChng_20_mdl)
  sing30 = getSignificance(retLevChng_30, retLevChng_30_mdl)
  sing40 = getSignificance(retLevChng_40, retLevChng_40_mdl)

  dsout = netCDF4.Dataset(outputNcFlPath, 'w')
  dsout.title = 'Future Changes of River Runoff in Europe (Mentaschi et al. 2020). Extreme heights'
  dsout.institution = 'European Commission, Joint European Research Center (JRC)'
  dsout.summary = 'Projected changes of extreme high river runoff (100-year return level) at 1.5°, 2.0°, 3.0°, 4.0° of global warming. From the project PESETA IV'

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

  bslnRetLevNc = dsout.createVariable('baseline_return_level', 'f4', ('x', 'y'))
  bslnRetLevNc.description = 'magnitude of the baseline 100-year event (year 1995)'
  bslnRetLevNc.units = 'm^3 * s^{-1}'
  bslnRetLevNc[:] = retLev

  rlChng15 = dsout.createVariable('return_level_perc_chng_15', 'f4', ('x', 'y'))
  rlChng15.description = 'percentage changes in magnitude of the 100-year event, at warming level 1.5°'
  rlChng15[:] = retLevChng_15*100

  rlChng20 = dsout.createVariable('return_level_perc_chng_20', 'f4', ('x', 'y'))
  rlChng20.description = 'percentage changes in magnitude of the 100-year event, at warming level 2.0°'
  rlChng20[:] = retLevChng_20*100

  rlChng30 = dsout.createVariable('return_level_perc_chng_30', 'f4', ('x', 'y'))
  rlChng30.description = 'percentage changes in magnitude of the 100-year event, at warming level 3.0°'
  rlChng30[:] = retLevChng_30*100

  rlChng40 = dsout.createVariable('return_level_perc_chng_40', 'f4', ('x', 'y'))
  rlChng40.description = 'percentage changes in magnitude of the 100-year event, at warming level 4.0°'
  rlChng40[:] = retLevChng_40*100

  rpshift15 = dsout.createVariable('baseline_rp_shift_15', 'f4', ('x', 'y'))
  rpshift15.description = 'return period at wariming level 1.5°, of the event with the same mangitude as the baseline 100-year one. This variable is a proxy for the change in frequency'
  rpshift15.units = 'years'
  rpshift15[:] = futRp_15

  rpshift20 = dsout.createVariable('baseline_rp_shift_20', 'f4', ('x', 'y'))
  rpshift20.description = 'return period at wariming level 2.0°, of the event with the same mangitude as the baseline 100-year one. This variable is a proxy for the change in frequency'
  rpshift20.units = 'years'
  rpshift20[:] = futRp_20

  rpshift30 = dsout.createVariable('baseline_rp_shift_30', 'f4', ('x', 'y'))
  rpshift30.description = 'return period at wariming level 3.0°, of the event with the same mangitude as the baseline 100-year one. This variable is a proxy for the change in frequency'
  rpshift30.units = 'years'
  rpshift30[:] = futRp_30

  rpshift40 = dsout.createVariable('baseline_rp_shift_40', 'f4', ('x', 'y'))
  rpshift40.description = 'return period at wariming level 4.0°, of the event with the same mangitude as the baseline 100-year one. This variable is a proxy for the change in frequency'
  rpshift40.units = 'years'
  rpshift40[:] = futRp_40

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
  ncdir = '/ClimateRun4/multi-hazard/eva/eamonn/'
  outputNcFlPath = '/DATA/mentalo/Dropbox/notSynced/pesetaRunoffRpShift/disEnsemble_highExtremes.nc'
 #plotRlChange15_20_30deg()
  saveEnsembleFile()

  plt.show()

