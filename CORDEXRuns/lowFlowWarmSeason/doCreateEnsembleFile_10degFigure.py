import re, os
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import gridspec
from alphaBetaLab import abFixBasemap
from mpl_toolkits import basemap as bm
from scipy.interpolate import interp1d
import netCDF4
import pickle


ncdir = '/ClimateRun4/multi-hazard/eva/prFrequencyShift_std/'
outputNcFlPath = './precipitationEnsemble.nc'
lowflowthreshold = .05
lowflowthreshold = .03


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
  pltvls[futRp <= 2] = 1
  pltvls[np.logical_and(futRp > 2, futRp <= 4)] = 2
  pltvls[np.logical_and(futRp > 4, futRp <= 7)] = 3
  pltvls[np.logical_and(futRp > 7, futRp <= 10)] = 4
  pltvls[np.logical_and(futRp > 10, futRp <= 15)] = 5
  pltvls[np.logical_and(futRp > 15, futRp <= 25)] = 6
  pltvls[np.logical_and(futRp > 25, futRp <= 50)] = 7
  pltvls[futRp > 50] = 8
  x, y = mp(lon, lat)
  sc = plt.scatter(x, y, s=1, c=pltvls, vmin=1, vmax=8, linewidth=0, cmap='bwr_r')
 #sc = plt.scatter(x, y, s=1, c=pltvls, vmin=1, vmax=8, linewidth=0, cmap='RdBu')
  txtpos = mp(-22, 68)
  plt.annotate(txt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=19)
  return sc, mp

def doLoadData(warmingLev=2, retPer=10):

  mdlvls = []
  mdlRetLev = []

  mskDs = netCDF4.Dataset('upArea.nc')
  upArea = mskDs.variables['upArea'][:].transpose()
  smallCtchArea = upArea  < 1e9
  msk = smallCtchArea
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
    retLev = ds.variables['return_level'][iwlev, irp, :, :].squeeze()
   #cnd = retLev < lowflowthreshold
   #retLev[cnd] = np.nan
    mdlRetLev.append(retLev)
    rpShift = ds.variables['baseline_rp_shift'][iwlev, irp, :, :].squeeze()
    rpShift[msk] = np.nan
   #rpShift[cnd] = np.nan
    mdlvls.append(rpShift)
    
  mdlvls = np.array(mdlvls)
  mdn = np.nanmedian(mdlvls, 0)
 #mdn = np.nanmean(np.array(mdlvls), 0)
  mdlRetLev = np.array(mdlRetLev)

  mdnRetLev = np.nanmedian(mdlRetLev, 0)
 #cnd = mdnRetLev < lowflowthreshold
 #mdn[cnd] = np.nan
  return lon, lat, mdn, mdlvls, mdlRetLev


def doLoadBaseline(retPer=10):

  mdlvls = []

  mskDs = netCDF4.Dataset('upArea.nc')
  upArea = mskDs.variables['upArea'][:].transpose()
  smallCtchArea = upArea  < 1e9
  msk = smallCtchArea
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
   #cnd = retLev < lowflowthreshold
   #retLev[cnd] = np.nan
   #retpers[cnd] = np.nan
    mdlvls.append(retlev)
    
  mdlvls = np.array(mdlvls)
  mdn = np.nanmedian(np.array(mdlvls), 0)
 #mdn = np.nanmean(np.array(mdlvls), 0)

  return lon, lat, x, y, mdn, mdlvls
    

  
def plotFreqChange15_20_30_40deg(): 
  lon, lat, futRp_15, _, rlByMdl_15 = doLoadData(warmingLev=1.5)
  lon, lat, futRp_20, _, rlByMdl_20 = doLoadData(warmingLev=2.0)
  lon, lat, futRp_30, _, rlByMdl_30 = doLoadData(warmingLev=3.0)
  lon, lat, futRp_40, _, rlByMdl_40 = doLoadData(warmingLev=4.0)
  lon, lat, x, y, retLev, _ = doLoadBaseline(retPer=10)
  cnd = retLev < lowflowthreshold
  futRp_15[cnd] = np.nan
  futRp_20[cnd] = np.nan
  futRp_30[cnd] = np.nan
  futRp_40[cnd] = np.nan

  f = plt.figure(figsize=(16,18))

  gs = gridspec.GridSpec(2, 3, width_ratios=[1,1,.04])

  ax1 = plt.subplot(gs[0, 0])
  txt = '$1.5^\circ C$'
  mp = None
  sc, mp = doPlotMinDisFreq(ax1, futRp_15, lon, lat, txt, mp)

  ax2 = plt.subplot(gs[0, 1])
  txt = '$2.0^\circ C$'
  sc, mp = doPlotMinDisFreq(ax2, futRp_20, lon, lat, txt, mp)

  ax3 = plt.subplot(gs[1, 0])
  txt = '$3.0^\circ C$'
  sc, mp = doPlotMinDisFreq(ax3, futRp_30, lon, lat, txt, mp)

  ax4 = plt.subplot(gs[1, 1])
  txt = '$4.0^\circ C$'
  sc, mp = doPlotMinDisFreq(ax4, futRp_40, lon, lat, txt, mp)

  cax = plt.subplot(gs[:, 2])
  cb = plt.colorbar(sc, ax=ax4, cax=cax, ticks=np.arange(1,9), orientation='vertical')
  cb.ax.set_yticklabels(['<2', '2-4', '4-7', '7-10', '10-15', '15-25', '25-50', '>50'], fontsize=15)
  cb.set_label('years', fontsize=16)

  ax1.set_aspect('auto')
  ax2.set_aspect('auto')
  ax3.set_aspect('auto')
  ax4.set_aspect('auto')
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
  _, _, _, _, retLev10, _ = doLoadBaseline(retPer=10)
  cnd = retLev10 < lowflowthreshold
  retLev[cnd] = np.nan
  futRp_15[cnd] = np.nan
  futRp_20[cnd] = np.nan
  futRp_30[cnd] = np.nan
  futRp_40[cnd] = np.nan

  retLevChng_15_mdl = (rlByMdl_15 - retLevByMdl)/retLevByMdl
  retLevChng_20_mdl = (rlByMdl_20 - retLevByMdl)/retLevByMdl
  retLevChng_30_mdl = (rlByMdl_30 - retLevByMdl)/retLevByMdl
  retLevChng_40_mdl = (rlByMdl_40 - retLevByMdl)/retLevByMdl

  retLevChng_15 = np.nanmedian(retLevChng_15_mdl, 0)
  retLevChng_20 = np.nanmedian(retLevChng_20_mdl, 0)
  retLevChng_30 = np.nanmedian(retLevChng_30_mdl, 0)
  retLevChng_40 = np.nanmedian(retLevChng_40_mdl, 0)
  retLevChng_15[cnd] = np.nan
  retLevChng_20[cnd] = np.nan
  retLevChng_30[cnd] = np.nan
  retLevChng_40[cnd] = np.nan

  dsout = netCDF4.Dataset(outputNcFlPath, 'w')
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
  bslnRetLevNc.description = 'return levels at baseline'
  bslnRetLevNc[:] = retLev

  rlChng15 = dsout.createVariable('return_level_perc_chng_15', 'f4', ('x', 'y'))
  rlChng15[:] = retLevChng_15*100

  rlChng20 = dsout.createVariable('return_level_perc_chng_20', 'f4', ('x', 'y'))
  rlChng20[:] = retLevChng_20*100

  rlChng30 = dsout.createVariable('return_level_perc_chng_30', 'f4', ('x', 'y'))
  rlChng30[:] = retLevChng_30*100

  rlChng40 = dsout.createVariable('return_level_perc_chng_40', 'f4', ('x', 'y'))
  rlChng40[:] = retLevChng_40*100

  rpshift15 = dsout.createVariable('baseline_rp_shift_15', 'f4', ('x', 'y'))
  rpshift15[:] = futRp_15

  rpshift20 = dsout.createVariable('baseline_rp_shift_20', 'f4', ('x', 'y'))
  rpshift20[:] = futRp_20

  rpshift30 = dsout.createVariable('baseline_rp_shift_30', 'f4', ('x', 'y'))
  rpshift30[:] = futRp_30

  rpshift40 = dsout.createVariable('baseline_rp_shift_40', 'f4', ('x', 'y'))
  rpshift40[:] = futRp_40

  dsout.close()

  
  
  
if __name__ == '__main__':
  import pdb; pdb.set_trace()

 #ncdir = '/ClimateRun4/multi-hazard/eva/prFrequencyShift_std/'
 #outputNcFlPath = './precipitationEnsemble.nc'
 #plotFreqChange15_20_30deg()
 #saveEnsembleFile()

 #ncdir = '/DATA/mentalo/Dropbox/notSynced/xEamonn'
  ncdir = '/ClimateRun4/multi-hazard/eva/lowFlowWarmSeason/'
  outputNcFlPath = '/DATA/mentalo/Dropbox/notSynced/xAlessandra/minDisWrmSsnEnsemble.nc'
 #plotRlChange15_20_30deg()
 #saveEnsembleFile()

  plotFreqChange15_20_30_40deg()
  plt.show()

