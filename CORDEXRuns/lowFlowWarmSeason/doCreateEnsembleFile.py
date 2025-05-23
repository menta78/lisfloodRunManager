import re, os
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import gridspec
from alphaBetaLab import abFixBasemap
from mpl_toolkits import basemap as bm
from scipy.interpolate import interp1d
import netCDF4
import pickle


ncdir = None
outputNcFlPath = None
diagnosticDataDir = None
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
  pltvls[futRp <= 1] = 1
  pltvls[np.logical_and(futRp > 1, futRp <= 2)] = 2
  pltvls[np.logical_and(futRp > 2, futRp <= 3)] = 3
  pltvls[np.logical_and(futRp > 3, futRp <= 5)] = 4
  pltvls[np.logical_and(futRp > 5, futRp <= 8)] = 5
  pltvls[np.logical_and(futRp > 8, futRp <= 12)] = 6
  pltvls[np.logical_and(futRp > 12, futRp <= 25)] = 7
  pltvls[futRp > 25] = 8
  x, y = mp(lon, lat)
  sc = plt.scatter(x, y, s=1, c=pltvls, vmin=1, vmax=8, linewidth=0, cmap='bwr_r')
 #sc = plt.scatter(x, y, s=1, c=pltvls, vmin=1, vmax=8, linewidth=0, cmap='RdBu')
  txtpos = mp(-22, 68)
  plt.annotate(txt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=19)
  return sc, mp

def doLoadData(warmingLev=2, retPer=5):

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


def doLoadBaseline(retPer=5):

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



def doLoadDiagnosticData(diagnosticDataDir, warmingLev):
  import getWarmingLevels
  print('  loading data at ' + str(warmingLev) + '°')

  fls = [f for f in os.listdir(diagnosticsDataDir) if re.match('(.*).npy', f)]
  fls.sort()
  mtchs = [re.match('droughtFrqDiagnostics_(.*)_(.*)_(.*)\.npy', f) for f in fls]
  mdls_ = [m.groups(0)[0] for m in mtchs]
  scns_ = [m.groups(0)[1] for m in mtchs]
  yrs = [int(float(m.groups(0)[2])) for m in mtchs]

  dtprot = np.load(os.path.join(diagnosticsDataDir, fls[0]))
  nx, ny = dtprot.shape

  mns = []

  mdls = set(mdls_)
  scns = set(scns_)
  for scn in scns:
    if warmingLev == 0:
      wls = {}
    else:
      wls = getWarmingLevels.getWarmingLevels(scn, warmingLev)
    if wls is None:
      for mdl in mdls:
        mns.append(np.zeros([nx, ny])*np.nan)
      continue
    for mdl in mdls:
      print('    loading model / scenario == ' + mdl + ' / ' + scn)
      if warmingLev == 0:
        ywl = 1995
      else:
        ywl = wls[mdl]
      ymin = max(ywl-15, 1981)
      ymax = min(ywl+14, 2100)
      dt = np.zeros([30, nx, ny])*np.nan
      yrsMdl = range(ymin, ymax+1)
      for iyr, yr in zip(range(len(yrsMdl)), yrsMdl):
        flPth = os.path.join(diagnosticsDataDir, '_'.join(['droughtFrqDiagnostics', mdl, scn, str(yr)])) + '.0.npy'
        if not os.path.isfile(flPth):
          print('     ... file ' + flPth + ' not found, skipping ...')
          continue
        dt[iyr] = np.load(flPth)
      mn = np.nanmedian(dt, 0)
     #mn = np.nanmean(dt, 0)
      mns.append(mn)
  mns = np.array(mns)
  frq = np.nanmedian(mns, 0)
  retper = 1/frq
  return retper, 1/mns
    

  
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
  cb.ax.set_yticklabels(['<1', '1-2', '2-3', '3-5', '5-8', '8-12', '12-25', '>25'], fontsize=15)
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


def saveEnsembleFile(retPer=10, percUp=90, percDown=10):
  prototypeFlPth = 'upArea.nc' 

  lon, lat, x, y, retLev, retLevByMdl = doLoadBaseline(retPer=retPer)
  lon, lat, futRp_15, _, rlByMdl_15 = doLoadData(warmingLev=1.5, retPer=retPer)
  lon, lat, futRp_20, _, rlByMdl_20 = doLoadData(warmingLev=2.0, retPer=retPer)
  lon, lat, futRp_30, _, rlByMdl_30 = doLoadData(warmingLev=3.0, retPer=retPer)
  lon, lat, futRp_40, _, rlByMdl_40 = doLoadData(warmingLev=4.0, retPer=retPer)
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
  retLevChng_15_up = np.nanpercentile(retLevChng_15_mdl, percUp, 0)
  retLevChng_15_dn = np.nanpercentile(retLevChng_15_mdl, percDown, 0)
  retLevChng_20 = np.nanmedian(retLevChng_20_mdl, 0)
  retLevChng_20_up = np.nanpercentile(retLevChng_20_mdl, percUp, 0)
  retLevChng_20_dn = np.nanpercentile(retLevChng_20_mdl, percDown, 0)
  retLevChng_30 = np.nanmedian(retLevChng_30_mdl, 0)
  retLevChng_30_up = np.nanpercentile(retLevChng_30_mdl, percUp, 0)
  retLevChng_30_dn = np.nanpercentile(retLevChng_30_mdl, percDown, 0)
  retLevChng_40 = np.nanmedian(retLevChng_40_mdl, 0)
  retLevChng_40_up = np.nanpercentile(retLevChng_40_mdl, percUp, 0)
  retLevChng_40_dn = np.nanpercentile(retLevChng_40_mdl, percDown, 0)
  retLevChng_15[cnd] = np.nan
  retLevChng_15_up[cnd] = np.nan
  retLevChng_15_dn[cnd] = np.nan
  retLevChng_20[cnd] = np.nan
  retLevChng_20_up[cnd] = np.nan
  retLevChng_20_dn[cnd] = np.nan
  retLevChng_30[cnd] = np.nan
  retLevChng_30_up[cnd] = np.nan
  retLevChng_30_dn[cnd] = np.nan
  retLevChng_40[cnd] = np.nan
  retLevChng_40_up[cnd] = np.nan
  retLevChng_40_dn[cnd] = np.nan



  futFq_15, futFq_15_mdls = doLoadDiagnosticData(diagnosticsDataDir, 1.5)
  futFq_20, futFq_20_mdls = doLoadDiagnosticData(diagnosticsDataDir, 2.0)
  futFq_30, futFq_30_mdls = doLoadDiagnosticData(diagnosticsDataDir, 3.0)
  futFq_40, futFq_40_mdls = doLoadDiagnosticData(diagnosticsDataDir, 4.0)
  baseline, baseline_mdls = doLoadDiagnosticData(diagnosticsDataDir, 0)

  futFq_15_up = np.percentile(futFq_15_mdls, percUp, 0)


  fqdlt15 = (futFq_15 - baseline)/baseline
  fqdlt20 = (futFq_20 - baseline)/baseline
  fqdlt30 = (futFq_30 - baseline)/baseline
  fqdlt40 = (futFq_40 - baseline)/baseline
  ch15mdls = (futFq_15_mdls - baseline_mdls)/baseline_mdls
  ch20mdls = (futFq_20_mdls - baseline_mdls)/baseline_mdls
  ch30mdls = (futFq_30_mdls - baseline_mdls)/baseline_mdls
  ch40mdls = (futFq_40_mdls - baseline_mdls)/baseline_mdls
  
  fqchng15_md = np.median(ch15mdls, 0)
  fqchng15_up = np.nanpercentile(ch15mdls, percUp, 0)
  fqchng15_dn = np.nanpercentile(ch15mdls, percDown, 0)
  fqchng15_up[fqchng15_up < fqdlt15] = fqdlt15[fqchng15_up < fqdlt15]
  fqchng15_dn[fqchng15_dn > fqdlt15] = fqdlt15[fqchng15_dn > fqdlt15]
  
  fqchng20_md = np.median(ch20mdls, 0)
  fqchng20_up = np.nanpercentile(ch20mdls, percUp, 0)
  fqchng20_dn = np.nanpercentile(ch20mdls, percDown, 0)
  fqchng20_up[fqchng20_up < fqdlt20] = fqdlt20[fqchng20_up < fqdlt20]
  fqchng20_dn[fqchng20_dn > fqdlt20] = fqdlt20[fqchng20_dn > fqdlt20]
  
  fqchng30_md = np.median(ch30mdls, 0)
  fqchng30_up = np.nanpercentile(ch30mdls, percUp, 0)
  fqchng30_dn = np.nanpercentile(ch30mdls, percDown, 0)
  fqchng30_up[fqchng30_up < fqdlt30] = fqdlt30[fqchng30_up < fqdlt30]
  fqchng30_dn[fqchng30_dn > fqdlt30] = fqdlt30[fqchng30_dn > fqdlt30]
  
  fqchng40_md = np.median(ch40mdls, 0)
  fqchng40_up = np.nanpercentile(ch40mdls, percUp, 0)
  fqchng40_dn = np.nanpercentile(ch40mdls, percDown, 0)
  fqchng40_up[fqchng40_up < fqdlt40] = fqdlt40[fqchng40_up < fqdlt40]
  fqchng40_dn[fqchng40_dn > fqdlt40] = fqdlt40[fqchng40_dn > fqdlt40]

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
  rlChng15_up = dsout.createVariable('return_level_perc_chng_15_up', 'f4', ('x', 'y'))
  rlChng15_up[:] = retLevChng_15_up*100
  rlChng15_dn = dsout.createVariable('return_level_perc_chng_15_dn', 'f4', ('x', 'y'))
  rlChng15_dn[:] = retLevChng_15_dn*100

  rlChng20 = dsout.createVariable('return_level_perc_chng_20', 'f4', ('x', 'y'))
  rlChng20[:] = retLevChng_20*100
  rlChng20_up = dsout.createVariable('return_level_perc_chng_20_up', 'f4', ('x', 'y'))
  rlChng20_up[:] = retLevChng_20_up*100
  rlChng20_dn = dsout.createVariable('return_level_perc_chng_20_dn', 'f4', ('x', 'y'))
  rlChng20_dn[:] = retLevChng_20_dn*100

  rlChng30 = dsout.createVariable('return_level_perc_chng_30', 'f4', ('x', 'y'))
  rlChng30[:] = retLevChng_30*100
  rlChng30_up = dsout.createVariable('return_level_perc_chng_30_up', 'f4', ('x', 'y'))
  rlChng30_up[:] = retLevChng_30_up*100
  rlChng30_dn = dsout.createVariable('return_level_perc_chng_30_dn', 'f4', ('x', 'y'))
  rlChng30_dn[:] = retLevChng_30_dn*100

  rlChng40 = dsout.createVariable('return_level_perc_chng_40', 'f4', ('x', 'y'))
  rlChng40[:] = retLevChng_40*100
  rlChng40_up = dsout.createVariable('return_level_perc_chng_40_up', 'f4', ('x', 'y'))
  rlChng40_up[:] = retLevChng_40_up*100
  rlChng40_dn = dsout.createVariable('return_level_perc_chng_40_dn', 'f4', ('x', 'y'))
  rlChng40_dn[:] = retLevChng_40_dn*100

  rpshift15 = dsout.createVariable('baseline_rp_shift_15', 'f4', ('x', 'y'))
  rpshift15[:] = futRp_15

  rpshift20 = dsout.createVariable('baseline_rp_shift_20', 'f4', ('x', 'y'))
  rpshift20[:] = futRp_20

  rpshift30 = dsout.createVariable('baseline_rp_shift_30', 'f4', ('x', 'y'))
  rpshift30[:] = futRp_30

  rpshift40 = dsout.createVariable('baseline_rp_shift_40', 'f4', ('x', 'y'))
  rpshift40[:] = futRp_40

  dlt = (futFq_15 - baseline)/baseline*100
  fqshift15 = dsout.createVariable('frequency_prc_chng_15', 'f4', ('x', 'y'))
  fqshift15[:] = dlt
  fqshift15_up = dsout.createVariable('frequency_prc_chng_15_up', 'f4', ('x', 'y'))
  fqshift15_up[:] = fqchng15_up*100
  fqshift15_dn = dsout.createVariable('frequency_prc_chng_15_dn', 'f4', ('x', 'y'))
  fqshift15_dn[:] = fqchng15_dn*100

  dlt = (futFq_20 - baseline)/baseline*100
  fqshift20 = dsout.createVariable('frequency_prc_chng_20', 'f4', ('x', 'y'))
  fqshift20[:] = dlt
  fqshift20_up = dsout.createVariable('frequency_prc_chng_20_up', 'f4', ('x', 'y'))
  fqshift20_up[:] = fqchng20_up*100
  fqshift20_dn = dsout.createVariable('frequency_prc_chng_20_dn', 'f4', ('x', 'y'))
  fqshift20_dn[:] = fqchng20_dn*100

  dlt = (futFq_30 - baseline)/baseline*100
  fqshift30 = dsout.createVariable('frequency_prc_chng_30', 'f4', ('x', 'y'))
  fqshift30[:] = dlt
  fqshift30_up = dsout.createVariable('frequency_prc_chng_30_up', 'f4', ('x', 'y'))
  fqshift30_up[:] = fqchng30_up*100
  fqshift30_dn = dsout.createVariable('frequency_prc_chng_30_dn', 'f4', ('x', 'y'))
  fqshift30_dn[:] = fqchng30_dn*100

  dlt = (futFq_40 - baseline)/baseline*100
  fqshift40 = dsout.createVariable('frequency_prc_chng_40', 'f4', ('x', 'y'))
  fqshift40[:] = dlt
  fqshift40_up = dsout.createVariable('frequency_prc_chng_40_up', 'f4', ('x', 'y'))
  fqshift40_up[:] = fqchng40_up*100
  fqshift40_dn = dsout.createVariable('frequency_prc_chng_40_dn', 'f4', ('x', 'y'))
  fqshift40_dn[:] = fqchng40_dn*100

  dsout.close()

  
  
  
if __name__ == '__main__':
  import pdb; pdb.set_trace()

 #ncdir = '/ClimateRun4/multi-hazard/eva/prFrequencyShift_std/'
 #outputNcFlPath = './precipitationEnsemble.nc'
 #plotFreqChange15_20_30deg()
 #saveEnsembleFile()

 #ncdir = '/DATA/mentalo/Dropbox/notSynced/xEamonn'
  ncdir = '/ClimateRun4/multi-hazard/eva/lowFlowWarmSeason/'
 #plotRlChange15_20_30deg()
  diagnosticsDataDir = '/DATA/ClimateRuns/droughtFreqDiagnostics/'

 #outputNcFlPath = '/DATA/mentalo/Dropbox/notSynced/xAlessandra/minDisWrmSsnEnsemble_5y.nc'
 #saveEnsembleFile(retPer=5)

 #outputNcFlPath = '/DATA/mentalo/Dropbox/notSynced/xAlessandra/minDisWrmSsnEnsemble_10y.nc'
 #saveEnsembleFile(retPer=10)

  outputNcFlPath = '/DATA/mentalo/Dropbox/notSynced/xAlessandra/minDisWrmSsnEnsemble_20y_meanFrq.nc'
  saveEnsembleFile(retPer=20)

 #outputNcFlPath = '/DATA/mentalo/Dropbox/notSynced/pesetaRunoffRpShift/disEnsemble_lowExtremes.nc'
 #saveEnsembleFile(retPer=15)

 #plotFreqChange15_20_30_40deg()
  plt.show()

