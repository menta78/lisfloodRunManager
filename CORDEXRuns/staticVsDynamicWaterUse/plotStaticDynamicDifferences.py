import os, pickle

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import gridspec
from mpl_toolkits import basemap as bm
import netCDF4

import loadWlVsScenChange as ldEnsmbl
import getWarmingLevels as gwl


def getLonLat():
  lonLatFile = 'lonlat.nc'
  ds = netCDF4.Dataset(lonLatFile)
  lon = ds.variables['lon'][:]
  lat = ds.variables['lat'][:]
  return lon, lat


def plotRelChngDiff(ax, relChngDiff, mp, txt, cmap='bwr_r', vmax=20, vmin=None):
  if mp == None:
   #llcrnrlon = -11.5
   #llcrnrlat = 23
   #urcrnrlon = 44
   #urcrnrlat = 74

    llcrnrlon = -25
    llcrnrlat = 25
    urcrnrlon = 44
    urcrnrlat = 71.5

   #mp = bm.Basemap(llcrnrlon=llcrnrlon, llcrnrlat=llcrnrlat, urcrnrlon=urcrnrlon, 
   #         urcrnrlat=urcrnrlat, resolution='l')
    mp = bm.Basemap(llcrnrlon=llcrnrlon, llcrnrlat=llcrnrlat, urcrnrlon=urcrnrlon,
             urcrnrlat=urcrnrlat, resolution='l', projection='lcc', lon_0=-15, lat_1=-15, lat_2=10)

  lon, lat = getLonLat()
  lon, lat = lon.transpose(), lat.transpose()

  plt.axes(ax)
  mp.drawcoastlines(linewidth=.25)
  mp.fillcontinents(color=[.95, .95, .95], lake_color=[.95, .95, .95], zorder=0)
 #mp.drawparallels(np.arange(-180, 180, 10), labels=[1,1])
 #mp.drawmeridians(np.arange(-90, 90, 10), labels=[1,1])
 # pcl = mp.pcolor(lon, lat, relChngDiff*100, cmap=cmap)
  x, y = mp(lon, lat)
  sc = plt.scatter(x, y, s=1, c=relChngDiff*100, linewidth=0, cmap=cmap)
  vmin = -vmax if vmin is None else vmin
  plt.clim(vmin, vmax)
  print('mean absolute change: ' + str(np.nanmean(np.abs(relChngDiff)*100)) + '%')

  txtpos = mp(-20, 69)
  plt.annotate(txt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=13)

  return sc, mp


def plotFigureDiff(relChngWUCnstR85, relChngWUChngR85, relChngWUCnstR45, relChngWUChngR45, title, mp=None):
  fig = plt.figure(figsize=(10, 5))
  gs = gridspec.GridSpec(1, 3, width_ratios=[1,1,.1])
  
  ax = plt.subplot(gs[0])
 #relChng = (relChngWUChngR85-relChngWUCnstR85)/relChngWUCnstR85
  relChng = relChngWUChngR85-relChngWUCnstR85
  sc, mp = plotRelChngDiff(ax, relChng, mp, 'a: RCP8.5', vmax=7)
  
  ax = plt.subplot(gs[1])
 #relChng = (relChngWUChngR45-relChngWUCnstR45)/relChngWUCnstR45
  relChng = relChngWUChngR45-relChngWUCnstR45
  sc, mp = plotRelChngDiff(ax, relChng, mp, 'b: RCP4.5', vmax=7)
  
  cax = plt.subplot(gs[2])
  cb = plt.colorbar(sc, ax=ax, cax=cax)
  cax.set_ylabel(title)
  
  plt.tight_layout()

  return fig, mp




def plotEnsembleStaticVsDynamicDiffMin():
  import pdb; pdb.set_trace()
  cacheFlPth = 'staticVsDynamicDiffMin.pkl'
  figFlNamePattern = 'staticVsDynamicDifMin_{wl}.png'
  if os.path.isfile(cacheFlPth):
    fl = open(cacheFlPth)
    relChngDiffChng15, rlR8Chng15, rlR4Chng15, rlR8AllChng15, rlR4AllChng15,\
    relChngDiffCnst15, rlR8Cnst15, rlR4Cnst15, rlR8AllCnst15, rlR4AllCnst15,\
    relChngDiffChng20, rlR8Chng20, rlR4Chng20, rlR8AllChng20, rlR4AllChng20,\
    relChngDiffCnst20, rlR8Cnst20, rlR4Cnst20, rlR8AllCnst20, rlR4AllCnst20\
          = pickle.load(fl)
    fl.close()
  else:
    relChngDiffChng15, rlR8Chng15, rlR4Chng15, rlR8AllChng15, rlR4AllChng15 = ldEnsmbl.loadWlVsScenChange(warmingLev=1.5, retPer=15,
               threshold=1., rlVarName='rl_min', flpattern='projection_dis_{scen}_{mdl}_wuChang_statistics.nc')
    relChngDiffCnst15, rlR8Cnst15, rlR4Cnst15, rlR8AllCnst15, rlR4AllCnst15 = ldEnsmbl.loadWlVsScenChange(warmingLev=1.5, retPer=15,
               threshold=1., rlVarName='rl_min', flpattern='projection_dis_{scen}_{mdl}_wuConst_statistics.nc')
    relChngDiffChng20, rlR8Chng20, rlR4Chng20, rlR8AllChng20, rlR4AllChng20 = ldEnsmbl.loadWlVsScenChange(warmingLev=2.0, retPer=15,
               threshold=1., rlVarName='rl_min', flpattern='projection_dis_{scen}_{mdl}_wuChang_statistics.nc')
    relChngDiffCnst20, rlR8Cnst20, rlR4Cnst20, rlR8AllCnst20, rlR4AllCnst20 = ldEnsmbl.loadWlVsScenChange(warmingLev=2.0, retPer=15,
               threshold=1., rlVarName='rl_min', flpattern='projection_dis_{scen}_{mdl}_wuConst_statistics.nc')
    cacheLst = [
        relChngDiffChng15, rlR8Chng15, rlR4Chng15, rlR8AllChng15, rlR4AllChng15,
        relChngDiffCnst15, rlR8Cnst15, rlR4Cnst15, rlR8AllCnst15, rlR4AllCnst15,
        relChngDiffChng20, rlR8Chng20, rlR4Chng20, rlR8AllChng20, rlR4AllChng20,
        relChngDiffCnst20, rlR8Cnst20, rlR4Cnst20, rlR8AllCnst20, rlR4AllCnst20]
    fl = open(cacheFlPth, 'w')
    pickle.dump(cacheLst, fl)
    fl.close()

  mp = None
  fig15, mp = plotFigureDiff(rlR8Cnst15, rlR8Chng15, rlR4Cnst15, rlR4Chng15, 'Dynamic vs static w.u., $1.5^\circ$. % pts', mp=mp)
  fig20, mp = plotFigureDiff(rlR8Cnst20, rlR8Chng20, rlR4Cnst20, rlR4Chng20, 'Dynamic vs static w.u., $2.0^\circ$. % pts', mp=mp)

  fig15.savefig(figFlNamePattern.format(wl='15'), dpi=300)
  fig20.savefig(figFlNamePattern.format(wl='20'), dpi=300)

  plt.show()

  
if __name__ == '__main__':
  plotEnsembleStaticVsDynamicDiffMin()

