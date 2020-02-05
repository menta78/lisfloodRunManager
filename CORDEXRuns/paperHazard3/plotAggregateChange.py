import numpy as np
from scipy import stats
from scipy.interpolate import interp1d
from matplotlib import pyplot as plt
from matplotlib import gridspec
from mpl_toolkits import basemap as bm
from scipy.interpolate import griddata
import netCDF4

import loadWlVsScenChange
from getWarmingLevels import getWarmingLevels

nmodels = -1
axFontSize = 14
positiveChanges = False
#excludedModels = ['IPSL-INERIS-WRF331F_BC']
excludedModels = []


def getNYrsTimeSeriesAroundWl(years, timeSeries, warmingLevelYears, models, halfWindowSize=0):
  tsshp = timeSeries.shape
  outTs = np.zeros([tsshp[0], halfWindowSize*2+1, tsshp[2], tsshp[3]])*np.nan
  for mdl, imdl in zip(models, range(len(models))):
    ywl_ = warmingLevelYears[mdl]
    # rounding to 5 years
    ywl = np.round(ywl_/5.)*5
    iywl = np.where(years == ywl)[0][0]
    outTs[imdl, :] = timeSeries[imdl, iywl-halfWindowSize:iywl+halfWindowSize+1]
  return outTs

def getRelChng(yrs, tmsrs, baselineYear=1995):
  ibsln = yrs == baselineYear
  vlbsln_ = tmsrs[:, ibsln, :, :]
  vlbsln = np.tile(vlbsln_, [1, tmsrs.shape[1], 1, 1])
  relChng = (tmsrs-vlbsln)/vlbsln
  return relChng

def getMeanAndSigma(srs):
  timeSz = srs.shape[1]
  yindx = timeSz / 2
  srs_ = srs[:, yindx, :, :]
  srs_[srs_ == np.inf] = np.nan
  srsMean = np.nanmean(srs_, 0)
  srsSigma = np.std(srs_, 0)
  return srsMean, srsSigma

def getLonLat():
  lonLatFile = 'lonlat.nc'
  ds = netCDF4.Dataset(lonLatFile)
  lon = ds.variables['lon'][:]
  lat = ds.variables['lat'][:]
  return lon, lat

def doPlotChanges(ax, warmingLev, meanTot, stdDevTot, r8spmean, r4spmean, r8mean, r4mean, plotXLabel, plotYLabel, yLabelStr):
  pstdDev = plt.plot([warmingLev, warmingLev], [meanTot+stdDevTot, meanTot-stdDevTot], color='silver', linewidth=14, label='$\sigma={sgm:1.0f}\%$'.format(sgm=stdDevTot[int(np.floor(len(stdDevTot)/2))]))
  pmdlr8 = plt.plot(warmingLev, r8spmean.transpose()*100, 'o', color='darkgreen', markersize=8, label='models'); 
  pmdlr4 = plt.plot(warmingLev, r4spmean.transpose()*100, 'o', color='darkgreen', markersize=8, label='models'); 
  pmn = plt.plot(warmingLev, (r4mean+r8mean)/2.*100, 'o', color='k', markersize=12, label='ens. mean'); 
  plt.xticks([])
  plt.grid('on')
  lgndLoc = 2 if positiveChanges else 3
 #plt.legend(handles=[pmdlr8[0], pmedr8[0], pmdlr4[0], pmedr4[0], pstdDev], fontsize=12, loc=lgndLoc)
  plt.legend(handles=[pmdlr8[0], pmn[0], pstdDev[0]], fontsize=10, loc=lgndLoc)
  ax.yaxis.tick_right()
  ax.yaxis.set_label_position("right")
  if plotXLabel:
    plt.xlabel('$' + str(warmingLev) + '^\circ$C w.l.', fontsize=15)
  else:
    ax.set_xticklabels([])
  if plotYLabel:
    plt.ylabel(yLabelStr, fontsize=17)
  else:
    ax.set_yticklabels([])
  ax.tick_params(axis="x", labelsize=axFontSize)
  ax.tick_params(axis="y", labelsize=axFontSize)

  xlm = ax.get_xlim()
  dlt = max(xlm) - min(xlm)
  pzr = plt.plot([min(xlm)-dlt*4, max(xlm)+dlt*4], [0, 0], 'k', linewidth=2)
  pzr[0].set_zorder(1)
  ax.set_xlim(xlm)


def doPlotAreaMap(ax, chng, mp):
  if mp == None:
   #llcrnrlon = -11.5
   #llcrnrlat = 23
   #urcrnrlon = 44
   #urcrnrlat = 74
    llcrnrlon = -25
    llcrnrlat = 31
    urcrnrlon = 37
    urcrnrlat = 71.5
    mp = bm.Basemap(llcrnrlon=llcrnrlon, llcrnrlat=llcrnrlat, urcrnrlon=urcrnrlon, 
             urcrnrlat=urcrnrlat, resolution='l', projection='lcc', lon_0=-15, lat_1=-15, lat_2=10)

  lon, lat = getLonLat()
  lon, lat = lon.transpose(), lat.transpose()

  cnd = ~np.isnan(chng)
  lonFt, latFt = lon[cnd], lat[cnd]
  chngFt = chng[cnd]

  longrd, latgrd = np.meshgrid(np.linspace(min(lonFt), max(lonFt), 50), np.linspace(min(latFt), max(latFt), 50))
  chngMap = griddata((lonFt, latFt), chngFt, (longrd, latgrd))
  cnd = chngMap > 0 if positiveChanges else chngMap < 0
  cnd = bm.maskoceans(longrd, latgrd, cnd).astype(float).filled(np.nan)
  chngMap = bm.maskoceans(longrd, latgrd, chngMap).filled(np.nan)
  mskEast = np.logical_and(latgrd <= 66.47, longrd >= 34.88)
  mskTrk0 = np.logical_and( np.logical_and(36. <= latgrd, latgrd <= 39.13), longrd >= 26.17)
  mskTrk1 = np.logical_and( np.logical_and(39.13 <= latgrd, latgrd <= 42.57), longrd >= 31)
  mskTrk2 = np.logical_and( latgrd <= 41.3, longrd >= 26.22)
  mskNAfrica = np.logical_and( np.logical_and(-1 <= longrd, longrd <= 11.55), latgrd <= 36.66)
  cnd[mskEast] = np.nan
  cnd[mskTrk0] = np.nan
  cnd[mskTrk1] = np.nan
  cnd[mskTrk2] = np.nan
  cnd[mskNAfrica] = np.nan
 #if positiveChanges:
 #  chngMap[chngMap <= 0] = np.nan
 #else:
 #  chngMap[chngMap >= 0] = np.nan

  x, y = mp(longrd, latgrd)

  plt.axes(ax)
  cmap = 'Blues' if positiveChanges else 'Reds'
 #clr = chngFt.copy()
 #clr[clr > .2] = .2
 #plt.scatter(x, y, clr, c=clr, cmap=cmap)
  mp.contourf(x, y, cnd, cmap=cmap, levels=[.4999, .5], extend='both')
  mp.drawcoastlines(linewidth=.25)
  mp.fillcontinents(color=[.95, .95, .95], lake_color=[.95, .95, .95], zorder=0)

  return mp
  


def plotTimeSerieVariabilityAtWl_hiExt(ax=None, axmap=None, plotXLabel=True, plotYLabel=True, warmingLev=2.0, bsmp=None):
  yrs, rpR8Srs, rpR4Srs, models = loadWlVsScenChange.loadRetPerAllYears(nmodels=nmodels, excludedModels=excludedModels)
  rpR8 = getRelChng(yrs, rpR8Srs)
  rpR4 = getRelChng(yrs, rpR4Srs)

  wlyR8 = getWarmingLevels('rcp85', warmingLev)
  r8srs = getNYrsTimeSeriesAroundWl(yrs, rpR8, wlyR8, models)
  wlyR4 = getWarmingLevels('rcp45', warmingLev)
  r4srs = getNYrsTimeSeriesAroundWl(yrs, rpR4, wlyR4, models)

  srstot = np.concatenate([r8srs, r4srs], 0)
  rallmeanWl, rallsigmaWl = getMeanAndSigma(r8srs)
  cndPosi = rallmeanWl > 0
  cndNega = rallmeanWl < 0
  cnd = cndPosi if positiveChanges else cndNega

  r8meanWl, r8sigmaWl = getMeanAndSigma(r8srs)
  cndMtx = np.tile(cnd, [r8srs.shape[0], r8srs.shape[1], 1, 1])
  r8srs[~cndMtx] = np.nan
  r8mean_ = np.nanmean(r8srs, 0)
  r8mean = r8mean_.reshape(r8mean_.shape[0], r8mean_.shape[1]*r8mean_.shape[2])
 #r8mean = np.nanmedian(r8mean, 1)
  r8mean = np.nanmean(r8mean, 1)

  r8spmean = r8srs.reshape(r8srs.shape[0], r8srs.shape[1], r8srs.shape[2]*r8srs.shape[3])
  r8spmean = np.nanmean(r8spmean, 2)
 #r8spmean = np.nanmean(r8spmean, 2)
  r8skew = stats.skew(r8spmean[:, 0])
  r8sigma = np.std(r8spmean[:, 0])
  r8mean = np.nanmean(r8spmean, 0)

  r4meanWl, r4sigmaWl = getMeanAndSigma(r4srs)
  cndMtx = np.tile(cnd, [r4srs.shape[0], r4srs.shape[1], 1, 1])
  r4srs[~cndMtx] = np.nan
  r4mean_ = np.nanmean(r4srs, 0)
  r4mean = r4mean_.reshape(r4mean_.shape[0], r4mean_.shape[1]*r4mean_.shape[2])
 #r4mean = np.nanmedian(r4mean, 1)
  r4mean = np.nanmean(r4mean, 1)

  r4spmean = r4srs.reshape(r4srs.shape[0], r4srs.shape[1], r4srs.shape[2]*r4srs.shape[3])
  r4spmean = np.nanmean(r4spmean, 2)
 #r4spmean = np.nanmean(r4spmean, 2)
  r4skew = stats.skew(r4spmean[:, 0])
  r4sigma = np.std(r4spmean[:, 0])
  r4mean = np.nanmean(r4spmean, 0)

  ensTot = np.concatenate([r8spmean, r4spmean], 0)
  stdDevTot = np.std(ensTot, 0)*100.
  meanTot = (r4mean + r8mean)/2.*100.

  if ax is None:
    fg = plt.figure(figsize=[5, 5])
    ax = fg.gca()
  doPlotChanges(ax, warmingLev, meanTot, stdDevTot, r8spmean, r4spmean, r8mean, r4mean, plotXLabel, plotYLabel, 'aggr. $\Delta Q_{H100}$ (%)')

  if not axmap is None:
    bsmp = doPlotAreaMap(axmap, rallmeanWl, bsmp)
  plt.tight_layout()

  if ax is None:
    fg.savefig('./ensemblesVariabilityAround2deg.png', dpi=400)
  return bsmp


def plotTimeSerieVariabilityAtWl_lowExt(ax=None, axmap=None, plotXLabel=True, plotYLabel=True, warmingLev=2.0, bsmp=None):
  yrs, rpR8Srs, rpR4Srs, models = loadWlVsScenChange.loadRetPerAllYears(rlVarName='rl_min', nmodels=nmodels, excludedModels=excludedModels)
  rpR8 = getRelChng(yrs, rpR8Srs)
  rpR4 = getRelChng(yrs, rpR4Srs)

  wlyR8 = getWarmingLevels('rcp85', warmingLev)
  r8srs = getNYrsTimeSeriesAroundWl(yrs, rpR8, wlyR8, models)
  r8srs[r8srs == np.inf] = np.nan
  wlyR4 = getWarmingLevels('rcp45', warmingLev)
  r4srs = getNYrsTimeSeriesAroundWl(yrs, rpR4, wlyR4, models)
  r4srs[r4srs == np.inf] = np.nan

  srstot = np.concatenate([r8srs, r4srs], 0)
  rallmeanWl, rallsigmaWl = getMeanAndSigma(r8srs)
  cndPosi = rallmeanWl > 0
  cndNega = rallmeanWl < 0
  cnd = cndPosi if positiveChanges else cndNega

  r8meanWl, r8sigmaWl = getMeanAndSigma(r8srs)
  cndMtx = np.tile(cnd, [r8srs.shape[0], r8srs.shape[1], 1, 1])
  r8srs[~cndMtx] = np.nan
  r8mean_ = np.nanmean(r8srs, 0)
  r8mean = r8mean_.reshape(r8mean_.shape[0], r8mean_.shape[1]*r8mean_.shape[2])
  r8mean = np.nanmedian(r8mean, 1)
 #r8mean = np.nanmean(r8mean, 1)

  r8spmean = r8srs.reshape(r8srs.shape[0], r8srs.shape[1], r8srs.shape[2]*r8srs.shape[3])
  r8spmean = np.nanmedian(r8spmean, 2)
 #r8spmean = np.nanmean(r8spmean, 2)
  r8skew = stats.skew(r8spmean[:, 0])
  r8sigma = np.std(r8spmean[:, 0])
  r8mean = np.nanmean(r8spmean, 0)

  r4meanWl, r4sigmaWl = getMeanAndSigma(r4srs)
  cndMtx = np.tile(cnd, [r4srs.shape[0], r4srs.shape[1], 1, 1])
  r4srs[~cndMtx] = np.nan
  r4mean_ = np.nanmean(r4srs, 0)
  r4mean = r4mean_.reshape(r4mean_.shape[0], r4mean_.shape[1]*r4mean_.shape[2])
  r4mean = np.nanmedian(r4mean, 1)
 #r4mean = np.nanmean(r4mean, 1)

  r4spmean = r4srs.reshape(r4srs.shape[0], r4srs.shape[1], r4srs.shape[2]*r4srs.shape[3])
  r4spmean = np.nanmedian(r4spmean, 2)
 #r4spmean = np.nanmean(r4spmean, 2)
  r4skew = stats.skew(r4spmean[:, 0])
  r4sigma = np.std(r4spmean[:, 0])
  r4mean = np.nanmean(r4spmean, 0)

  ensTot = np.concatenate([r8spmean, r4spmean], 0)
  stdDevTot = np.std(ensTot, 0)*100.
  meanTot = (r4mean + r8mean)/2.*100.

  yr = [-15, -10, -5, 0, 5, 10, 15]
  if ax is None:
    fg = plt.figure(figsize=[8.46, 4.98])
    ax = fg.gca()
  doPlotChanges(ax, warmingLev, meanTot, stdDevTot, r8spmean, r4spmean, r8mean, r4mean, plotXLabel, plotYLabel, 'aggr. $\Delta Q_{L15}$ (%)')

  if not axmap is None:
    bsmp = doPlotAreaMap(axmap, rallmeanWl, bsmp)

  plt.tight_layout()
  if ax is None:
    fg.savefig('./ensemblesVariabilityAround2deg_lowExt.png', dpi=400)
  return bsmp


def plotTimeSerieVariabilityAtWl_mean(ax=None, axmap=None, plotXLabel=True, plotYLabel=True, warmingLev=2.0, bsmp=None):
  yrs, _, _, r8srs_, r4srs_ = loadWlVsScenChange.loadMeanChangesAtWl_nYearsAroundWLYear(warmingLev=warmingLev, nmodels=nmodels, excludedModels=excludedModels)
  r8srs = r8srs_[:, [3], :, :]
  r4srs = r4srs_[:, [3], :, :]

  wlyR8 = getWarmingLevels('rcp85', warmingLev)
  wlyR4 = getWarmingLevels('rcp45', warmingLev)

  srstot = np.concatenate([r8srs, r4srs], 0)
  rallmeanWl, rallsigmaWl = getMeanAndSigma(r8srs)
  cndPosi = rallmeanWl > 0
  cndNega = rallmeanWl < 0
  cnd = cndPosi if positiveChanges else cndNega

  r8meanWl, r8sigmaWl = getMeanAndSigma(r8srs)
  cndMtx = np.tile(cnd, [r8srs.shape[0], r8srs.shape[1], 1, 1])
  r8srs[~cndMtx] = np.nan
  r8mean_ = np.nanmean(r8srs, 0)
  r8mean = r8mean_.reshape(r8mean_.shape[0], r8mean_.shape[1]*r8mean_.shape[2])
 #r8mean = np.nanmedian(r8mean, 1)
  r8mean = np.nanmean(r8mean, 1)

  r8spmean = r8srs.reshape(r8srs.shape[0], r8srs.shape[1], r8srs.shape[2]*r8srs.shape[3])
  r8spmean = np.nanmean(r8spmean, 2)
  r8skew = stats.skew(r8spmean[:, 0])
  r8sigma = np.std(r8spmean[:, 0])
  r8mean = np.nanmean(r8spmean, 0)

  r4meanWl, r4sigmaWl = getMeanAndSigma(r4srs)
  cndMtx = np.tile(cnd, [r4srs.shape[0], r4srs.shape[1], 1, 1])
  r4srs[~cndMtx] = np.nan
  r4mean_ = np.nanmean(r4srs, 0)
  r4mean = r4mean_.reshape(r4mean_.shape[0], r4mean_.shape[1]*r4mean_.shape[2])
 #r4mean = np.nanmedian(r4mean, 1)
  r4mean = np.nanmean(r4mean, 1)

  r4spmean = r4srs.reshape(r4srs.shape[0], r4srs.shape[1], r4srs.shape[2]*r4srs.shape[3])
  r4spmean = np.nanmean(r4spmean, 2)
  r4skew = stats.skew(r4spmean[:, 0])
  r4sigma = np.std(r4spmean[:, 0])
  r4mean = np.nanmean(r4spmean, 0)

  ensTot = np.concatenate([r8spmean, r4spmean], 0)
  stdDevTot = np.std(ensTot, 0)*100.
  meanTot = (r4mean + r8mean)/2.*100.

  yr = [-15, -10, -5, 0, 5, 10, 15]
  if ax is None:
    fg = plt.figure(figsize=[8.46, 4.98])
    ax = fg.gca()
  doPlotChanges(ax, warmingLev, meanTot, stdDevTot, r8spmean, r4spmean, r8mean, r4mean, plotXLabel, plotYLabel, 'aggr. $\Delta Q_M$ (%)')

  if not axmap is None:
    bsmp = doPlotAreaMap(axmap, rallmeanWl, bsmp)

  plt.tight_layout()
  if ax is None:
    fg.savefig('./ensemblesVariabilityAround2deg_mean.png', dpi=400)

  return bsmp


def plotTimeSerieVariabilityAtWl_hiLowExt(warmingLev=2.0):
  outPng = './ensemblesVariabilityAround2deg_hiLowExt_' + str(warmingLev) + '.png'

  fg = plt.figure(figsize=[10, 4.98*3])
  gs = gridspec.GridSpec(3, 1)
  xtxt = 13

  ax1 = plt.subplot(gs[0,0])
  plotTimeSerieVariabilityAtWl_hiExt(ax1, plotXLabel=False, warmingLev=warmingLev)
  ylm = plt.ylim()
  ytxt = min(ylm) + (max(ylm) - min(ylm))*.93
  plt.text(xtxt, ytxt, 'a', fontsize=17)

  ax2 = plt.subplot(gs[1,0])
  plotTimeSerieVariabilityAtWl_mean(ax2, plotXLabel=False, warmingLev=warmingLev)
  ylm = plt.ylim()
  ytxt = min(ylm) + (max(ylm) - min(ylm))*.93
  plt.text(xtxt, ytxt, 'b', fontsize=17)

  ax3 = plt.subplot(gs[2,0])
  plotTimeSerieVariabilityAtWl_lowExt(ax3, plotXLabel=True, warmingLev=warmingLev)
  ylm = plt.ylim()
  ytxt = min(ylm) + (max(ylm) - min(ylm))*.93
  plt.text(xtxt, ytxt, 'c', fontsize=17)

 #ax1.set_aspect('auto')
 #ax2.set_aspect('auto')
  ax3.set_aspect('auto')

  plt.tight_layout()
  fg.savefig(outPng, dpi=300)


def plotTimeSerieVariabilityAtWl_hiLowExt_bothWarmLev():
  posiNegaStr = 'posi' if positiveChanges else 'nega'
  outPng = './ensemblesVariability_hiLowExt_' + posiNegaStr + '.png'

  st1 = 0
  end1 = 8
  st2 = 8
  end2 = 11
  st3 = 13
  end3 = 21
  st4 = 21
  end4 = 24

  fg = plt.figure(figsize=[12, 12])
  gs = gridspec.GridSpec(3, end4+2)
  xtxt, ytxt = -24, 32
 #xtxt2, ytxt2 = -24, 70
  compOpChar = '>' if positiveChanges else '<'

  bsmp = None

  warmingLev = 1.5
  ax1mp = plt.subplot(gs[0,:end1])
  ax1 = plt.subplot(gs[0,st2:end2])
  bsmp = plotTimeSerieVariabilityAtWl_hiExt(ax1, ax1mp, plotXLabel=False, warmingLev=warmingLev, bsmp=bsmp)
  txtpos = bsmp(xtxt, ytxt)
 #txtpos2 = bsmp(xtxt2, ytxt2)
  plt.annotate('a: $\Delta Q_{H100} ' + compOpChar + ' 0$ at $1.5^\circ$ C', xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=13)
  plt.axes(ax1)
  ylm = plt.ylim([-2, 45]) if positiveChanges else plt.ylim([-25, 10])

  ax2mp = plt.subplot(gs[1,:end1])
  ax2 = plt.subplot(gs[1,st2:end2])
  bsmp = plotTimeSerieVariabilityAtWl_mean(ax2, ax2mp, plotXLabel=False, warmingLev=warmingLev, bsmp=bsmp)
  plt.annotate('c: $\Delta Q_M ' + compOpChar + ' 0$ at $1.5^\circ$ C', xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=13)
  plt.axes(ax2)
  ylm = plt.ylim([-2, 50]) if positiveChanges else plt.ylim([-30, 15])

  ax3mp = plt.subplot(gs[2,:end1])
  ax3 = plt.subplot(gs[2,st2:end2])
  bsmp = plotTimeSerieVariabilityAtWl_lowExt(ax3, ax3mp, plotXLabel=True, warmingLev=warmingLev, bsmp=bsmp)
  plt.annotate('e: $\Delta Q_{L15} ' + compOpChar + ' 0$ at $1.5^\circ$ C', xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=13)
  plt.axes(ax3)
  ylm = plt.ylim([-15, 90]) if positiveChanges else plt.ylim([-45, 15])

  warmingLev = 2.0
  ax4mp = plt.subplot(gs[0,st3:end3])
  ax4 = plt.subplot(gs[0,st4:end4])
  bsmp = plotTimeSerieVariabilityAtWl_hiExt(ax4, ax4mp, plotXLabel=False, plotYLabel=True, warmingLev=warmingLev, bsmp=bsmp)
  plt.annotate('b: $\Delta Q_{H100} ' + compOpChar + ' 0$ at $2.0^\circ$ C', xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=13)
  plt.axes(ax4)
  ylm = plt.ylim([-2, 45]) if positiveChanges else plt.ylim([-25, 10])

  ax5mp = plt.subplot(gs[1,st3:end3])
  ax5 = plt.subplot(gs[1,st4:end4])
  bsmp = plotTimeSerieVariabilityAtWl_mean(ax5, ax5mp, plotXLabel=False, plotYLabel=True, warmingLev=warmingLev, bsmp=bsmp)
  plt.annotate('d: $\Delta Q_M ' + compOpChar + ' 0$ at $2.0^\circ$ C', xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=13)
  plt.axes(ax5)
  ylm = plt.ylim([-2, 50]) if positiveChanges else plt.ylim([-30, 15])

  ax6mp = plt.subplot(gs[2,st3:end3])
  ax6 = plt.subplot(gs[2,st4:end4])
  bsmp = plotTimeSerieVariabilityAtWl_lowExt(ax6, ax6mp, plotXLabel=True, plotYLabel=True, warmingLev=warmingLev, bsmp=bsmp)
  plt.annotate('f: $\Delta Q_{L15} ' + compOpChar + ' 0$ at $2.0^\circ$ C', xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=13)
  plt.axes(ax6)
  ylm = plt.ylim([-15, 90]) if positiveChanges else plt.ylim([-45, 15])

  w_pad = -6.3 if positiveChanges else -7.8
  plt.tight_layout(w_pad=w_pad)
 #plt.subplots_adjust(wspace=0)
  fg.savefig(outPng, dpi=300)


if __name__ == '__main__':
 #plotTimeSerieVariabilityAtWl_hiExt(warmingLev=1.5)
 #plotTimeSerieVariabilityAtWl_hiLowExt(warmingLev=2.0)
  plotTimeSerieVariabilityAtWl_hiLowExt_bothWarmLev()
 #plotTimeSerieVariabilityAtWl_hiExt()
 #plotTimeSerieVariabilityAtWl_mean()
  plt.show()
