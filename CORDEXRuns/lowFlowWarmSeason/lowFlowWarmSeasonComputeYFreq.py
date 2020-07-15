import netCDF4
import numpy as np
import pandas
import os, re
from scipy.interpolate import interp1d
import multiprocessing as mp


def getCountries():
  cntrs = pandas.read_csv('countries.csv')
  ds = netCDF4.Dataset('EU27plusUK_code.nc')
  cdMap = ds.variables['code'][:]
  ds.close()
  return cntrs, cdMap


def elabModel(scen, model, inputNcFlPath, outputCsvFlPath, mask, 
              diagnosticsDataDir, _lock):
  print('elaborating scen,model = ' + scen + ',' + model)

  bslnYear = 1995

  try:
    print('  loading the data ...')
    _lock.acquire()
    dsin = netCDF4.Dataset(inputNcFlPath)
    x = dsin.variables['x'][:]
    y = dsin.variables['y'][:]
    inRetPer = dsin.variables['return_period'][:]
    rlYrs = dsin.variables['year'][:]
    bslnYIndx = np.where(rlYrs ==  bslnYear)[0][0]
    retLev = dsin.variables['rl_min_ws'][:, bslnYIndx, :, :].squeeze()
    yrsAll = dsin.variables['year_all'][:]
    yrMinFlw = dsin.variables['year_min_ws'][:]
    dsin.close()
  finally:
    _lock.release()

  cntrs, cntrMap = getCountries()

 #mskDs = netCDF4.Dataset('upArea.nc')
 #upArea = mskDs.variables['upArea'][:].transpose()
 #smallCtchArea = upArea  < 1e9
 #mskDs.close()

  def getOutFrq(inRetPer, currentLev, retLevBsln):
    nx = currentLev.shape[0]
    ny = currentLev.shape[1]
    outRetPer = np.zeros([nx, ny])*np.nan
    for ix in range(nx):
      for iy in range(ny):
        rlcri = currentLev[ix, iy]
        if np.sum(np.isnan(rlcri)) > 0:
          continue
        rlbsln = retLevBsln[:, ix, iy]
        if rlbsln[0] < .3:
          continue
        outRetPer[ix, iy] = max(interp1d(rlbsln, inRetPer, axis=0, fill_value='extrapolate')(rlcri), 0)
    frq = 1/outRetPer
    frq[frq < 0] = np.nan
    frq[np.isinf(frq)] = np.nan
    return frq

  cols = ['COUNTRY']
  cols.extend(str(int(y)) for y in yrsAll)
  outdf = pandas.DataFrame(columns=cols, index=cntrs.values[:,1])
  for cnt in cntrs.values:
    outdf.loc[cnt[1]]['COUNTRY'] = cnt[0]

  for yr, mnfl in zip(yrsAll, yrMinFlw):
    print('  elaborating year ' + str(int(yr)))
    print('    interpolating ...')
   #mnfl[smallCtchArea] = np.nan
    mnfl[~mask] = np.nan
    frq = getOutFrq(inRetPer, mnfl, retLev)
    if not diagnosticsDataDir is None:
      outFlName = os.path.join(diagnosticsDataDir, '_'.join(['droughtFrqDiagnostics', model, scen, str(yr)]))
     #try:
     #  _lock.acquire()
      np.save(outFlName, frq)
     #finally:
     #  _lock.release()
    print('    compute median by country ...')
    for cnt in cntrs.values:
      print('      ' + cnt[0])
      msk_ = cntrMap == cnt[1]
      frqC = np.nanmedian(frq[msk_.transpose()])
      outdf.loc[cnt[1]][str(int(yr))] = frqC
      
  outdf.to_csv(outputCsvFlPath)


def _elabFileParallel(fl):
  print('elaborating file ' + fl)
  flpth = os.path.join(inputDir, fl)
  outflpth = os.path.join(outputDir, fl.replace('projection_', 'freqByCountry_').replace('.nc', '.csv'))
  print('  output file path: ' + outflpth)
  if os.path.isfile(outflpth):
    print('    file already exists, skipping ...')
    return fl
  m = re.match(inputFlPattern, fl)
  scen = m.groups()[0]
  model = m.groups()[1]
  elabModel(scen, model, flpth, outflpth, _mask, _diagnosticsDataDir, _lock)
  return fl


def loadMask(baselineEnsembleFilePath):
  ds = netCDF4.Dataset(baselineEnsembleFilePath)
  rl = ds.variables['baseline_return_level']
  mask = ~np.isnan(rl)
  return mask


def loopModels(inputDir, inputFlPattern, outputDir, 
    baselineEnsembleFilePath, diagnosticsDataDir=None, nParWorker=12):
  if not os.path.isfile(baselineEnsembleFilePath):
    raise Exception('file ' + baselineEnsembleFilePath + ' does not exist. Generate it with the script doCreateEnsembleFile.py')
  mask = loadMask(baselineEnsembleFilePath)
  infls = [fl for fl in os.listdir(inputDir) if re.match(inputFlPattern, fl)]

  print('initializing parallel pool')
  global _lock, _diagnosticsDataDir, _mask
  _lock = mp.Lock()
  _diagnosticsDataDir = diagnosticsDataDir
  _mask = mask
  p = mp.Pool(nParWorker)
  flitr = p.imap(_elabFileParallel, infls)
  for fl in flitr:
    print('... file ' + fl + ' complete')
  p.close()



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
      mns.append(mn)
  mns = np.array(mns)
  frq = np.nanmedian(mns, 0)
 #retper = 1/frq
  return frq

  
def plotRetPerDiagnostic15_20_30_40deg(mapNcFile, diagnosticsDataDir): 
  from matplotlib import pyplot as plt
  from matplotlib import gridspec
  from alphaBetaLab import abFixBasemap
  from mpl_toolkits import basemap as bm

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
   #pltvls = np.zeros(futRp.shape)*np.nan
   #pltvls[futRp <= 2] = 0
   #pltvls[futRp <= 4] = 1
   #pltvls[np.logical_and(futRp > 4, futRp <= 8)] = 2
   #pltvls[np.logical_and(futRp > 8, futRp <= 14)] = 3
   #pltvls[np.logical_and(futRp > 14, futRp <= 20)] = 4
   #pltvls[np.logical_and(futRp > 20, futRp <= 30)] = 5
   #pltvls[np.logical_and(futRp > 30, futRp <= 50)] = 6
   #pltvls[np.logical_and(futRp > 50, futRp <= 80)] = 7
   #pltvls[np.logical_and(futRp > 80, futRp <= 150)] = 8
   #pltvls[futRp > 150] = 9
   #x, y = mp(lon, lat)
   #sc = plt.scatter(x, y, s=1, c=pltvls, vmin=1, vmax=8, linewidth=0, cmap='bwr')
    x, y = mp(lon, lat)
    sc = plt.scatter(x, y, s=1, c=futRp, vmin=-100, vmax=100, linewidth=0, cmap='bwr_r')

    txtpos = mp(-22, 68)
    plt.annotate(txt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=19)
    return sc, mp

  futRp_15 = doLoadDiagnosticData(diagnosticsDataDir, 1.5)
  futRp_20 = doLoadDiagnosticData(diagnosticsDataDir, 2.0)
  futRp_30 = doLoadDiagnosticData(diagnosticsDataDir, 3.0)
  futRp_40 = doLoadDiagnosticData(diagnosticsDataDir, 4.0)
  baseline = doLoadDiagnosticData(diagnosticsDataDir, 0)
  ds = netCDF4.Dataset(mapNcFile)
  lon = ds.variables['lon'][:]
  lat = ds.variables['lat'][:]
  ds.close()

  f = plt.figure(figsize=(16,18))

  gs = gridspec.GridSpec(2, 3, width_ratios=[1,1,.04])

  ax1 = plt.subplot(gs[0, 0])
  txt = '$1.5^\circ C$'
  mp = None
  dlt = (futRp_15 - baseline)/baseline*100
  sc, mp = doPlotMinDisFreq(ax1, dlt, lon, lat, txt, mp)

  ax2 = plt.subplot(gs[0, 1])
  txt = '$2.0^\circ C$'
  dlt = (futRp_20 - baseline)/baseline*100
  sc, mp = doPlotMinDisFreq(ax2, dlt, lon, lat, txt, mp)

  ax3 = plt.subplot(gs[1, 0])
  txt = '$3.0^\circ C$'
  dlt = (futRp_30 - baseline)/baseline*100
  sc, mp = doPlotMinDisFreq(ax3, dlt, lon, lat, txt, mp)

  ax4 = plt.subplot(gs[1, 1])
  txt = '$4.0^\circ C$'
  dlt = (futRp_40 - baseline)/baseline*100
  sc, mp = doPlotMinDisFreq(ax4, dlt, lon, lat, txt, mp)

  cax = plt.subplot(gs[:, 2])
  cb = plt.colorbar(sc, ax=ax4, cax=cax, orientation='vertical')
 #cb.ax.set_yticklabels(['<2', '2-4', '4-8', '8-14', '14-20', '20-30', '30-50', '50-80', '80-150', '>150'], fontsize=15)
  cb.set_label('% change', fontsize=16)

  ax1.set_aspect('auto')
  ax2.set_aspect('auto')
  ax3.set_aspect('auto')
  ax4.set_aspect('auto')
  cax.set_aspect('auto')
  plt.tight_layout()

  f.savefig('freqDeltaValidation.png', dpi=200)
  plt.show()



if __name__ == '__main__':
  import pdb; pdb.set_trace()


  inputDir = '/ClimateRun4/multi-hazard/eva/'
  inputFlPattern = 'projection_dis_(rcp45|rcp85)_(.*)_wuConst_statistics.nc'
  outputDir = '/DATA/mentalo/Dropbox/notSynced/xGustavo/lowFlowWrmSsnByCountry'
  diagnosticsDataDir = '/DATA/ClimateRuns/droughtFreqDiagnostics/'
  #baselineEnsembleFilePath = '/DATA/mentalo/Dropbox/notSynced/xAlessandra/minDisWrmSsnEnsemble.nc'
  baselineEnsembleFilePath = '/DATA/mentalo/Dropbox/notSynced/xAlessandra/minDisWrmSsnEnsemble_5y.nc'

 #loopModels(inputDir, inputFlPattern, outputDir, baselineEnsembleFilePath, diagnosticsDataDir=diagnosticsDataDir)
  plotRetPerDiagnostic15_20_30_40deg(baselineEnsembleFilePath, diagnosticsDataDir)


