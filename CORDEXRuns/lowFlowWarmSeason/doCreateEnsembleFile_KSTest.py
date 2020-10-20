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
   # putting the pixels that failed the KS test to nan
    significantKS = ds.variables['significance'][iwlev, :, :].squeeze()
    retLev[significantKS != 1] = np.nan
   #cnd = retLev < lowflowthreshold
   #retLev[cnd] = np.nan
    mdlRetLev.append(retLev)
    rpShift = ds.variables['baseline_rp_shift'][iwlev, irp, :, :].squeeze()
    rpShift[msk] = np.nan
    rpShift[significantKS != 1] = np.nan
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


def saveEnsembleFile(retPer=10):
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
  retLevChng_20 = np.nanmedian(retLevChng_20_mdl, 0)
  retLevChng_30 = np.nanmedian(retLevChng_30_mdl, 0)
  retLevChng_40 = np.nanmedian(retLevChng_40_mdl, 0)
  retLevChng_15[cnd] = np.nan
  retLevChng_20[cnd] = np.nan
  retLevChng_30[cnd] = np.nan
  retLevChng_40[cnd] = np.nan



  futFq_15, futFq_15_mdls = doLoadDiagnosticData(diagnosticsDataDir, 1.5)
  futFq_20, futFq_20_mdls = doLoadDiagnosticData(diagnosticsDataDir, 2.0)
  futFq_30, futFq_30_mdls = doLoadDiagnosticData(diagnosticsDataDir, 3.0)
  futFq_40, futFq_40_mdls = doLoadDiagnosticData(diagnosticsDataDir, 4.0)
  baseline, baseline_mdls = doLoadDiagnosticData(diagnosticsDataDir, 0)


  
  def getSignificance(chmdn, chByModel, nmodel):
    posi = np.zeros(chByModel.shape)*np.nan
    posi[chByModel > 0] = 1
    nega = np.zeros(chByModel.shape)*np.nan
    nega[chByModel < 0] = 1
    mdlvalid = ~np.isnan(chByModel)
    nmdl = np.nansum(mdlvalid, 0)
    sigthr = np.floor(nmdl/3*2)
   #sigthr = np.ceil(nmdl/3*2)
   #sigthr = np.floor(nmdl*.8)
   #sigthr = np.ceil(nmdl*.8)
    smposi = np.nansum(posi, 0)
    smnega = np.nansum(nega, 0)
    sgn = np.zeros(chmdn.shape)
    sgn[chmdn > 0] = (smposi >= sigthr)[chmdn > 0]
    sgn[chmdn < 0] = (smnega >= sigthr)[chmdn < 0]
    sgn[np.isnan(chmdn)] = np.nan
    # removing the pixels with < 50% models in agreement
    sgn[nmdl < nmodel/2] = 0
    return sgn

  sing15 = getSignificance(retLevChng_15, retLevChng_15_mdl, 22)
  sing20 = getSignificance(retLevChng_20, retLevChng_20_mdl, 22)
  sing30 = getSignificance(retLevChng_30, retLevChng_30_mdl, 11)
  sing40 = getSignificance(retLevChng_40, retLevChng_40_mdl, 11)

  fqdlt15 = (futFq_15 - baseline)/baseline
  fqdlt20 = (futFq_20 - baseline)/baseline
  fqdlt30 = (futFq_30 - baseline)/baseline
  fqdlt40 = (futFq_40 - baseline)/baseline
  ch15mdls = (futFq_15_mdls - baseline_mdls)/baseline_mdls
  ch20mdls = (futFq_20_mdls - baseline_mdls)/baseline_mdls
  ch30mdls = (futFq_30_mdls - baseline_mdls)/baseline_mdls
  ch40mdls = (futFq_40_mdls - baseline_mdls)/baseline_mdls
  sing15_fq = getSignificance(fqdlt15, ch15mdls, 22)
  sing20_fq = getSignificance(fqdlt20, ch20mdls, 22)
  sing30_fq = getSignificance(fqdlt30, ch30mdls, 11)
  sing40_fq = getSignificance(fqdlt40, ch40mdls, 11)

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

  sign15Nc = dsout.createVariable('significant_15', 'i1', ('x', 'y'))
  sign15Nc[:] = sing15

  rlChng20 = dsout.createVariable('return_level_perc_chng_20', 'f4', ('x', 'y'))
  rlChng20[:] = retLevChng_20*100

  sign20Nc = dsout.createVariable('significant_20', 'i1', ('x', 'y'))
  sign20Nc[:] = sing20

  rlChng30 = dsout.createVariable('return_level_perc_chng_30', 'f4', ('x', 'y'))
  rlChng30[:] = retLevChng_30*100

  sign30Nc = dsout.createVariable('significant_30', 'i1', ('x', 'y'))
  sign30Nc[:] = sing30

  rlChng40 = dsout.createVariable('return_level_perc_chng_40', 'f4', ('x', 'y'))
  rlChng40[:] = retLevChng_40*100

  sign40Nc = dsout.createVariable('significant_40', 'i1', ('x', 'y'))
  sign40Nc[:] = sing40

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

  sign15FqNc = dsout.createVariable('significant_fq_chng_15', 'i1', ('x', 'y'))
  sign15FqNc[:] = sing15_fq

  dlt = (futFq_20 - baseline)/baseline*100
  fqshift20 = dsout.createVariable('frequency_prc_chng_20', 'f4', ('x', 'y'))
  fqshift20[:] = dlt

  sign20FqNc = dsout.createVariable('significant_fq_chng_20', 'i1', ('x', 'y'))
  sign20FqNc[:] = sing20_fq

  dlt = (futFq_30 - baseline)/baseline*100
  fqshift30 = dsout.createVariable('frequency_prc_chng_30', 'f4', ('x', 'y'))
  fqshift30[:] = dlt

  sign30FqNc = dsout.createVariable('significant_fq_chng_30', 'i1', ('x', 'y'))
  sign30FqNc[:] = sing30_fq

  dlt = (futFq_40 - baseline)/baseline*100
  fqshift40 = dsout.createVariable('frequency_prc_chng_40', 'f4', ('x', 'y'))
  fqshift40[:] = dlt

  sign40FqNc = dsout.createVariable('significant_fq_chng_40', 'i1', ('x', 'y'))
  sign40FqNc[:] = sing40_fq

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

  outputNcFlPath = '/DATA/mentalo/Dropbox/notSynced/xAlessandra/minDisWrmSsnEnsemble_20y.nc'
  saveEnsembleFile(retPer=20)

 #outputNcFlPath = '/DATA/mentalo/Dropbox/notSynced/pesetaRunoffRpShift/disEnsemble_lowExtremes.nc'
 #saveEnsembleFile(retPer=15)

 #plotFreqChange15_20_30_40deg()
  plt.show()

