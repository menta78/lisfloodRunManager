import numpy as np
from matplotlib import pyplot as plt
from matplotlib import gridspec
from mpl_toolkits import basemap as bm

import estimateChngSignificanceAndRobustness
from loadWlVsScenChange import loadWlVsScenChange


def plotRelChngDiff(ax, relChngDiff, mp, txt):
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
  pcl = mp.pcolor(lon, lat, relChngDiff*100, cmap='bwr_r')
  plt.clim(-20, 20)

  txtpos = mp(-7, 25)
  plt.annotate(txt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data')

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
  pcl = mp.pcolor(lon, lat, pvl_, cmap='hot', vmin=0, vmax=.5)

  txtpos = mp(-7, 25)
  plt.annotate(txt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data')

  return pcl, mp


def plotFigureWlVsScenChange():
  outPng = 'wlRelChngScenVsScen.png'

  f = plt.figure(figsize=(8.5, 8))
  gs = gridspec.GridSpec(2, 3, width_ratios=[1,1,.5/8.5])

  mp = None

  ax0 = plt.subplot(gs[0,0])
  relChngDiff = loadWlVsScenChange(warmingLev=1.5)
  pcl, mp = plotRelChngDiff(ax0, relChngDiff, mp, 'a: $\Delta rcp85 - \Delta rcp45$, w.l. $1.5^\circ$')

  ax = plt.subplot(gs[0,1])
  relChngDiff = loadWlVsScenChange(warmingLev=2)
  pcl, mp = plotRelChngDiff(ax, relChngDiff, mp, 'b: $\Delta rcp85 - \Delta rcp45$, w.l. $2.0^\circ$')

  cax = plt.subplot(gs[0,2])
  cb = plt.colorbar(pcl, ax=ax, cax=cax)
  cb.set_label('$\Delta rcp85 - \Delta rcp45$ (%)')
  ax0.set_aspect('auto')
  ax.set_aspect('auto')
  cax.set_aspect('auto')

  ax0 = plt.subplot(gs[1,0])  
  pValue = estimateChngSignificanceAndRobustness.computeRlChngPValueAtWarmingLevBtwScen(warmingLev=1.5)
  pcl, mp = plotPvalue(ax0, pValue, relChngDiff, mp, 'c: p-value, w.l. $1.5^\circ$')

  ax = plt.subplot(gs[1,1])  
  pValue = estimateChngSignificanceAndRobustness.computeRlChngPValueAtWarmingLevBtwScen(warmingLev=2)
  pcl, mp = plotPvalue(ax, pValue, relChngDiff, mp, 'd: p-value. w.l. $2.0^\circ$')

  cax = plt.subplot(gs[1,2])
  cb = plt.colorbar(pcl, ax=ax, cax=cax)
  cb.set_label('p-value')
  ax0.set_aspect('auto')
  ax.set_aspect('auto')
  cax.set_aspect('auto')

  plt.tight_layout()

  f.savefig(outPng, dpi=300)
  
  

