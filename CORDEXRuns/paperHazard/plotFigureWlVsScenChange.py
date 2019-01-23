import numpy as np
from matplotlib import pyplot as plt
from matplotlib import gridspec
from mpl_toolkits import basemap as bm

import estimateChngSignificanceAndRobustness
from loadWlVsScenChange import loadWlVsScenChange


def plotRelChngDiff(ax, relChngDiff, mp, txt, cmap='RdBu', vmax=20, vmin=None):
  if mp == None:
    llcrnrlon = -11.5
    llcrnrlat = 23
    urcrnrlon = 44
    urcrnrlat = 74
    mp = bm.Basemap(llcrnrlon=llcrnrlon, llcrnrlat=llcrnrlat, urcrnrlon=urcrnrlon, 
             urcrnrlat=urcrnrlat, resolution='l')

  lon, lat = estimateChngSignificanceAndRobustness.getLonLat()
  lon, lat = lon.transpose(), lat.transpose()

  plt.axes(ax)
  mp.drawcoastlines(linewidth=.25)
 #mp.fillcontinents(color=[.8, .8, .8], lake_color=[.7, .95, .7])
 #mp.drawparallels(np.arange(-180, 180, 10), labels=[1,1])
 #mp.drawmeridians(np.arange(-90, 90, 10), labels=[1,1])
  pcl = mp.pcolor(lon, lat, relChngDiff*100, cmap=cmap)
  vmin = -vmax if vmin is None else vmin
  plt.clim(vmin, vmax)
  print('mean absolute change: ' + str(np.nanmean(np.abs(relChngDiff)*100)) + '%')

  txtpos = mp(-7, 25)
  plt.annotate(txt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=13)

  return pcl, mp
  

def plotPvalue(ax, pValue, relChngDiff, mp, txt):
  if mp == None:
    llcrnrlon = -11.5
    llcrnrlat = 23
    urcrnrlon = 44
    urcrnrlat = 74
    mp = bm.Basemap(llcrnrlon=llcrnrlon, llcrnrlat=llcrnrlat, urcrnrlon=urcrnrlon, 
             urcrnrlat=urcrnrlat, resolution='l')

  lon, lat = estimateChngSignificanceAndRobustness.getLonLat()
  lon, lat = lon.transpose(), lat.transpose()

  plt.axes(ax)
  mp.drawcoastlines(linewidth=.25)

  pvl_ = pValue.copy()
  pvl_[pvl_ > .5] = np.nan
 #pvl_[relChngDiff <= 0] = pvl_[relChngDiff <= 0] - 1
 #pvl_[relChngDiff > 0] = 1 - pvl_[relChngDiff > 0]
 #pcl = mp.pcolor(lon, lat, pvl_, cmap='Spectral')
 #pcl = mp.pcolor(lon, lat, pvl_, cmap='hot', vmin=0, vmax=.5)

  txtpos = mp(-7, 25)
  plt.annotate(txt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=13)

  return pcl, mp
  

def plotSigma(ax, sigma, relChngDiff, mp, txt, sigmamax=2, signSigmaThreshold=1, printSignTxt=True):
  if mp == None:
    llcrnrlon = -11.5
    llcrnrlat = 23
    urcrnrlon = 44
    urcrnrlat = 74
    mp = bm.Basemap(llcrnrlon=llcrnrlon, llcrnrlat=llcrnrlat, urcrnrlon=urcrnrlon, 
             urcrnrlat=urcrnrlat, resolution='l')

  lon, lat = estimateChngSignificanceAndRobustness.getLonLat()
  lon, lat = lon.transpose(), lat.transpose()

  plt.axes(ax)
  mp.drawcoastlines(linewidth=.25)

  absSigma = np.abs(sigma)
 #pcl = mp.pcolor(lon, lat, sigma, cmap='hot_r', vmin=0, vmax=sigmamax)
 #pcl = mp.pcolor(lon, lat, sigma, cmap='Spectral_r', vmin=0, vmax=sigmamax)
 #pcl = mp.pcolor(lon, lat, sigma, cmap='coolwarm', vmin=0, vmax=sigmamax)
 #pcl = mp.pcolor(lon, lat, np.abs(sigma), cmap='RdBu_r', vmin=0, vmax=sigmamax)
  pcl = mp.pcolor(lon, lat, absSigma, cmap='PuBu_r', vmin=0, vmax=sigmamax)
  percSign = float(np.nansum(absSigma <= signSigmaThreshold))/np.nansum(np.logical_not(np.isnan(absSigma)))
  prcTxt = '% of pixel where $\Delta d_{{100-wl}} > \sigma$: {p:2.2f}%'.format(p=percSign*100)
  print(prcTxt)

  txtpos = mp(-7, 25)
  plt.annotate(txt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=13)
  if printSignTxt:
    txtpos = mp(-7, 72)
    plt.annotate(prcTxt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=10)

  return pcl, mp
  

def plotAgreeingMdlCnt(ax, agrMdlCnt, mp, txt):
  if mp == None:
    llcrnrlon = -11.5
    llcrnrlat = 23
    urcrnrlon = 44
    urcrnrlat = 74
    mp = bm.Basemap(llcrnrlon=llcrnrlon, llcrnrlat=llcrnrlat, urcrnrlon=urcrnrlon, 
             urcrnrlat=urcrnrlat, resolution='l')

  lon, lat = estimateChngSignificanceAndRobustness.getLonLat()
  lon, lat = lon.transpose(), lat.transpose()

  plt.axes(ax)
  mp.drawcoastlines(linewidth=.25)

  pcl = mp.pcolor(lon, lat, agrMdlCnt, cmap='hot_r', vmin=6, vmax=11)

  txtpos = mp(-7, 25)
  plt.annotate(txt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data')

  return pcl, mp


def plotFigureWlVsScenChange():
  outPng = 'wlRelChngScenVsScen.png'

  f = plt.figure(figsize=(8.5, 12))
  gs = gridspec.GridSpec(3, 3, width_ratios=[1,1,.5/8.5])

  mp = None

  ax0 = plt.subplot(gs[0,0])
  relChngDiff, _ = loadWlVsScenChange(warmingLev=1.5)
  pcl, mp = plotRelChngDiff(ax0, relChngDiff, mp, 'a: $\Delta rcp85 - \Delta rcp45$, w.l. $1.5^\circ$')

  ax = plt.subplot(gs[0,1])
  relChngDiff, _ = loadWlVsScenChange(warmingLev=2)
  pcl, mp = plotRelChngDiff(ax, relChngDiff, mp, 'b: $\Delta rcp85 - \Delta rcp45$, w.l. $2.0^\circ$')

  cax = plt.subplot(gs[0,2])
  cb = plt.colorbar(pcl, ax=ax, cax=cax)
  cb.set_label('$\Delta rcp85 - \Delta rcp45$ (%)')
  ax0.set_aspect('auto')
  ax.set_aspect('auto')
  cax.set_aspect('auto')


  ax0 = plt.subplot(gs[1,0])  
  pValue, agrMdlCnt15, std15 = estimateChngSignificanceAndRobustness.computeRlChngPValueAtWarmingLevBtwScen(warmingLev=1.5)
  pcl, mp = plotPvalue(ax0, pValue, relChngDiff, mp, 'c: p-value, w.l. $1.5^\circ$')

  ax = plt.subplot(gs[1,1])  
  pValue, agrMdlCnt20, std20 = estimateChngSignificanceAndRobustness.computeRlChngPValueAtWarmingLevBtwScen(warmingLev=2)
  pcl, mp = plotPvalue(ax, pValue, relChngDiff, mp, 'd: p-value. w.l. $2.0^\circ$')

  cax = plt.subplot(gs[1,2])
  cb = plt.colorbar(pcl, ax=ax, cax=cax)
  cb.set_label('p-value')
  ax0.set_aspect('auto')
  ax.set_aspect('auto')
  cax.set_aspect('auto')


  ax0 = plt.subplot(gs[2,0])  
  pcl, mp = plotAgreeingMdlCnt(ax0, agrMdlCnt15, mp, 'e: agr. mdl. count $1.5^\circ$')

  ax = plt.subplot(gs[2,1])  
  pcl, mp = plotAgreeingMdlCnt(ax, agrMdlCnt20, mp, 'f: agr. mdl.c ount $2.0^\circ$')

  cax = plt.subplot(gs[2,2])
  cb = plt.colorbar(pcl, ax=ax, cax=cax)
  cb.set_label('agreeing mdl. count')
  ax0.set_aspect('auto')
  ax.set_aspect('auto')
  cax.set_aspect('auto')


  plt.tight_layout()

  f.savefig(outPng, dpi=300)
  
  


def plotScenVsScen(warmingLev=2.0):
  outPng = 'wlRelChngScenVsScen_wl' + str(warmingLev) + '.png'

  f = plt.figure(figsize=(13, 8))
  gs = gridspec.GridSpec(2, 4, width_ratios=[1,1,1,1./12.])

  mp = None

  relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all = loadWlVsScenChange(warmingLev=warmingLev)
  ax0 = plt.subplot(gs[0,0])
  pcl, mp = plotRelChngDiff(ax0, rc_r8, mp, 'a: rcp85 - hist., w.l. $' + str(warmingLev) +'^\circ$', vmax=40)
  ax1 = plt.subplot(gs[0,1])
  pcl, mp = plotRelChngDiff(ax1, rc_r4, mp, 'b: rcp45 - hist., w.l. $' + str(warmingLev) +'^\circ$', vmax=40)
  ax2 = plt.subplot(gs[0,2])
  pcl, mp = plotRelChngDiff(ax2, relChngDiff, mp, 'c: $\Delta rcp85 - \Delta rcp45$', vmax=40)
  cax = plt.subplot(gs[0,3])
  cb = plt.colorbar(pcl, ax=ax2, cax=cax)
  cb.set_label('$\Delta$ 100-y discharge (%)')
  ax0.set_aspect('auto')
  ax1.set_aspect('auto')
  ax2.set_aspect('auto')
  cax.set_aspect('auto')

  ax0 = plt.subplot(gs[1,0])
  pValue, _, std = estimateChngSignificanceAndRobustness.computeRlChngPValueAtWarmingLev(scen='rcp85', warmingLev=warmingLev)
  std = std/rc_r8
 #pcl, mp = plotPvalue(ax0, pValue, None, mp, 'd: p-value, $\Delta rcp85$')
  pcl, mp = plotSigma(ax0, std, None, mp, 'd: $\sigma$, ratio of $\Delta rcp85$', sigmamax=2)
  ax1 = plt.subplot(gs[1,1])
  pValue, _, std = estimateChngSignificanceAndRobustness.computeRlChngPValueAtWarmingLev(scen='rcp45', warmingLev=warmingLev)
  std = std/rc_r4
 #pcl, mp = plotPvalue(ax1, pValue, None, mp, 'e: p-value, $\Delta rcp45$')
  pcl, mp = plotSigma(ax1, std, None, mp, 'e: $\sigma$, ratio of $\Delta rcp45$', sigmamax=2)
  ax2 = plt.subplot(gs[1,2])  
 #pValue, _, _ = estimateChngSignificanceAndRobustness.computeRlChngPValueAtWarmingLevBtwScen(warmingLev=warmingLev)
 #pcl, mp = plotPvalue(ax2, pValue, relChngDiff, mp, 'f: p-value, $\Delta rcp85 - \Delta rcp45$')
  std = np.std(rc_r8all-rc_r4all, 0)
  std = std/rc_r8
  pcl, mp = plotSigma(ax2, std, relChngDiff, mp, 'f: $\sigma$, $\Delta rcp85 - \Delta rcp45$', sigmamax=2, printSignTxt=False)
  cax = plt.subplot(gs[1,3])
  cb = plt.colorbar(pcl, ax=ax2, cax=cax)
 #cb.set_label('p-value')
  cb.set_label('$\sigma$ (fraction of relative change)')
  ax0.set_aspect('auto')
  ax1.set_aspect('auto')
  ax2.set_aspect('auto')
  cax.set_aspect('auto')

  plt.tight_layout()

  f.savefig(outPng, dpi=300)
  
  


def plotScenVsScenAll():
  outPng = 'wlRelChngScenVsScen_wlAll.png'

  f = plt.figure(figsize=(13, 16))
  gs = gridspec.GridSpec(5, 4, width_ratios=[1,1,1,1./12.], height_ratios=[1,1,1./30.,1.,1.])

  mp = None


  warmingLev = 1.5

  relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all = loadWlVsScenChange(warmingLev=warmingLev)
  ax0 = plt.subplot(gs[0,0])
  pcl, mp = plotRelChngDiff(ax0, rc_r8, mp, 'a: rel. chng. rcp85 at $' + str(warmingLev) +'^\circ$', vmax=40)
  ax1 = plt.subplot(gs[0,1])
  pcl, mp = plotRelChngDiff(ax1, rc_r4, mp, 'b: rel. chng. rcp45 at $' + str(warmingLev) +'^\circ$', vmax=40)
  ax2 = plt.subplot(gs[0,2])
  pcl, mp = plotRelChngDiff(ax2, relChngDiff, mp, 'c: difference rcp85-rcp45 at $' + str(warmingLev) +'^\circ$', vmax=40)
  cax = plt.subplot(gs[0,3])
  cb = plt.colorbar(pcl, ax=ax2, cax=cax)
  cb.set_label('$\Delta$ 100-y discharge (%)')
  ax0.set_aspect('auto')
  ax1.set_aspect('auto')
  ax2.set_aspect('auto')
  cax.set_aspect('auto')

  ax0 = plt.subplot(gs[1,0])
  pValue, _, std = estimateChngSignificanceAndRobustness.computeRlChngPValueAtWarmingLev(scen='rcp85', warmingLev=warmingLev)
  std = std/rc_r8
 #pcl, mp = plotPvalue(ax0, pValue, None, mp, 'd: p-value, $\Delta rcp85$')
  pcl, mp = plotSigma(ax0, std, None, mp, 'd: $\sigma$, % of rel. chng. of rcp85', sigmamax=2)
  ax1 = plt.subplot(gs[1,1])
  pValue, _, std = estimateChngSignificanceAndRobustness.computeRlChngPValueAtWarmingLev(scen='rcp45', warmingLev=warmingLev)
  std = std/rc_r4
 #pcl, mp = plotPvalue(ax1, pValue, None, mp, 'e: p-value, $\Delta rcp45$')
  pcl, mp = plotSigma(ax1, std, None, mp, 'e: $\sigma$, % of rel. chng. of rcp45', sigmamax=2)
  ax2 = plt.subplot(gs[1,2])  
 #pValue, _, _ = estimateChngSignificanceAndRobustness.computeRlChngPValueAtWarmingLevBtwScen(warmingLev=warmingLev)
 #pcl, mp = plotPvalue(ax2, pValue, relChngDiff, mp, 'f: p-value, $\Delta rcp85 - \Delta rcp45$')
  std = np.std(rc_r8all-rc_r4all, 0)
  std = std/rc_r8
  pcl, mp = plotSigma(ax2, std, relChngDiff, mp, 'f: $\sigma$, difference rcp85-rcp45', sigmamax=2)
  cax = plt.subplot(gs[1,3])
  cb = plt.colorbar(pcl, ax=ax2, cax=cax)
 #cb.set_label('p-value')
  cb.set_label('$\sigma$ (fraction of relative change)')
  ax0.set_aspect('auto')
  ax1.set_aspect('auto')
  ax2.set_aspect('auto')
  cax.set_aspect('auto')


  warmingLev = 2.0

  relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all = loadWlVsScenChange(warmingLev=warmingLev)
  ax0 = plt.subplot(gs[3,0])
  pcl, mp = plotRelChngDiff(ax0, rc_r8, mp, 'g: rel. chng. rcp85 $' + str(warmingLev) +'^\circ$', vmax=40)
  ax1 = plt.subplot(gs[3,1])
  pcl, mp = plotRelChngDiff(ax1, rc_r4, mp, 'h: rel. chng. rcp45 $' + str(warmingLev) +'^\circ$', vmax=40)
  ax2 = plt.subplot(gs[3,2])
  pcl, mp = plotRelChngDiff(ax2, relChngDiff, mp, 'i: difference rcp85-rcp45 at $' + str(warmingLev) +'^\circ$', vmax=40)
  cax = plt.subplot(gs[3,3])
  cb = plt.colorbar(pcl, ax=ax2, cax=cax)
  cb.set_label('$\Delta$ 100-y discharge (%)')
  ax0.set_aspect('auto')
  ax1.set_aspect('auto')
  ax2.set_aspect('auto')
  cax.set_aspect('auto')

  ax0 = plt.subplot(gs[4,0])
  pValue, _, std = estimateChngSignificanceAndRobustness.computeRlChngPValueAtWarmingLev(scen='rcp85', warmingLev=warmingLev)
  std = std/np.abs(rc_r8)
 #pcl, mp = plotPvalue(ax0, pValue, None, mp, 'd: p-value, $\Delta rcp85$')
  pcl, mp = plotSigma(ax0, std, None, mp, 'j: $\sigma$, % of rel. chng. of rcp85', sigmamax=2)
  ax1 = plt.subplot(gs[4,1])
  pValue, _, std = estimateChngSignificanceAndRobustness.computeRlChngPValueAtWarmingLev(scen='rcp45', warmingLev=warmingLev)
  std = std/np.abs(rc_r4)
 #pcl, mp = plotPvalue(ax1, pValue, None, mp, 'e: p-value, $\Delta rcp45$')
  pcl, mp = plotSigma(ax1, std, None, mp, 'k: $\sigma$, % of rel. chng. of rcp45', sigmamax=2)
  ax2 = plt.subplot(gs[4,2])  
 #pValue, _, _ = estimateChngSignificanceAndRobustness.computeRlChngPValueAtWarmingLevBtwScen(warmingLev=warmingLev)
 #pcl, mp = plotPvalue(ax2, pValue, relChngDiff, mp, 'f: p-value, $\Delta rcp85 - \Delta rcp45$')
  std = np.std(rc_r8all-rc_r4all, 0)
  std = std/rc_r8
  pcl, mp = plotSigma(ax2, std, relChngDiff, mp, 'l: $\sigma$, difference rcp85-rcp45', sigmamax=2)
  cax = plt.subplot(gs[4,3])
  cb = plt.colorbar(pcl, ax=ax2, cax=cax)
 #cb.set_label('p-value')
  cb.set_label('$\sigma$ (fraction of relative change)')
  ax0.set_aspect('auto')
  ax1.set_aspect('auto')
  ax2.set_aspect('auto')
  cax.set_aspect('auto')


  plt.tight_layout()

  f.savefig(outPng, dpi=300)


if __name__ == '__main__':
  plotScenVsScen(1.5)
  plt.show()
