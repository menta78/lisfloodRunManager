import re, os
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import gridspec
from mpl_toolkits import basemap as bm
from scipy.interpolate import interp1d
import netCDF4
import pickle

import estimateChngSignificanceAndRobustness
import loadWlVsScenChange as ldEnsmbl
import getWarmingLevels as gwl



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
  pltvls[futRp <= 4] = 1
  pltvls[np.logical_and(futRp > 4, futRp <= 6)] = 2
  pltvls[np.logical_and(futRp > 6, futRp <= 8)] = 3
  pltvls[np.logical_and(futRp > 8, futRp <= 10)] = 4
  pltvls[np.logical_and(futRp > 10, futRp <= 12)] = 5
  pltvls[np.logical_and(futRp > 12, futRp <= 20)] = 6
  pltvls[np.logical_and(futRp > 20, futRp <= 40)] = 7
  pltvls[futRp > 40] = 8
  x, y = mp(lon, lat)
  sc = plt.scatter(x, y, s=1, c=pltvls, vmin=1, vmax=8, linewidth=0, cmap='PiYG')
  txtpos = mp(-22, 68)
  plt.annotate(txt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=19)
  return sc, mp


def doLoadData(warmingLev=2, retPer=10):
  numberOfModels = -1
  bsln_, rl_r8_, rl_r4_, retper_ = ldEnsmbl.loadMdlsAtWl(warmingLev=warmingLev, rlVarName='rl_min', numberOfModels=numberOfModels)
  bsln = np.nanmean(bsln_, 0)
  rl_r8 = np.nanmean(rl_r8_, 0)
  rl_r4 = np.nanmean(rl_r4_, 0)

  iretper = np.where(retper_ == retPer)[0][0]

# retlvRcpR8 = rl_r8[iretper, :, :]
# retlvRcpR4 = rl_r4[iretper, :, :]
# cnd = ~np.isnan(retlvRcpR8)
# retlvRcpR8Ln = retlvRcpR8[cnd]
# retlvRcpR4Ln = retlvRcpR4[cnd]
# cndmtx = np.tile(cnd, [len(retper_), 1, 1])
# retlvBslnLn = bsln[cndmtx].reshape(len(retper_), len(retlvRcpR8Ln))
# retpermtx = np.transpose(np.tile(retper_, [retvlBslnLn.shape[0], 1]), (1,0))

# futRpR8 = np.zeros(retvlBslnLn.shape)*np.nan
# futRpR4 = np.zeros(retvlBslnLn.shape)*np.nan
# npt = retvlBslnLn.shape[0]
# for ipt in range(npt):
#   futRpR8[ipt] = interp1d(retlvBslnLn[:,ipt], retper_, bounds_error=False, fill_value='extrapolate')(retlvRcpR8Ln[ipt])
#   futRpR4[ipt] = interp1d(retlvBslnLn[:,ipt], retper_, bounds_error=False, fill_value='extrapolate')(retlvRcpR4Ln[ipt])

  retlvBsln = bsln[iretper, :, :]
  cnd = ~np.isnan(retlvBsln)
  retlvBslnLn = retlvBsln[cnd]
  cndmtx = np.tile(cnd, [len(retper_), 1, 1])
  retlvRcpR8Ln = rl_r8[cndmtx].reshape(len(retper_), len(retlvBslnLn))
  retlvRcpR4Ln = rl_r4[cndmtx].reshape(len(retper_), len(retlvBslnLn))
  retpermtx = np.transpose(np.tile(retper_, [retlvBslnLn.shape[0], 1]), (1,0))

  futRpR8 = np.zeros(retlvBslnLn.shape)*np.nan
  futRpR4 = np.zeros(retlvBslnLn.shape)*np.nan
  npt = retlvBslnLn.shape[0]
  for ipt in range(npt):
    futRpR8[ipt] = interp1d(retlvRcpR8Ln[:,ipt], retper_, bounds_error=False, fill_value='extrapolate')(retlvBslnLn[ipt])
    futRpR4[ipt] = interp1d(retlvRcpR4Ln[:,ipt], retper_, bounds_error=False, fill_value='extrapolate')(retlvBslnLn[ipt])

  dslonlat = netCDF4.Dataset('lonlat.nc')
  lon = dslonlat['lon'][:].transpose()
  lat = dslonlat['lat'][:].transpose()
  dslonlat.close()

  dsuparea = netCDF4.Dataset('upArea.nc')
  upArea = dsuparea.variables['upArea'][:].transpose()
  dsuparea.close()

  uparealn = upArea[cnd]
  lonln = lon[cnd]
  latln = lat[cnd]

  futRpR8[uparealn < 1e9] = np.nan
  futRpR4[uparealn < 1e9] = np.nan
  return lonln, latln, futRpR8, futRpR4

  
def plotMinDisFreqChange(): 
  cacheFl = 'plotMinDisFreqChange.cache'
  if os.path.isfile(cacheFl):
    lon, lat, futRpR8_15, futRpR4_15, futRpR8_20, futRpR4_20 = pickle.load(open(cacheFl, 'rb'))
  else:
    lon, lat, futRpR8_15, futRpR4_15 = doLoadData(warmingLev=1.5)
    lon, lat, futRpR8_20, futRpR4_20 = doLoadData(warmingLev=2.0)
    pickle.dump((lon, lat, futRpR8_15, futRpR4_15, futRpR8_20, futRpR4_20), open(cacheFl, 'wb'))
  


  f = plt.figure(figsize=(16,8))

  gs = gridspec.GridSpec(1, 3, width_ratios=[1,1,.05])

  ax1 = plt.subplot(gs[0])
  txt = '$1.5^\circ C$'
  mp = None
  sc, mp = doPlotMinDisFreq(ax1, futRpR8_15, lon, lat, txt, mp)

  ax2 = plt.subplot(gs[1])
  txt = '$2.0^\circ C$'
  sc, mp = doPlotMinDisFreq(ax2, futRpR8_20, lon, lat, txt, mp)

  cax = plt.subplot(gs[2])
  cb = plt.colorbar(sc, ax=ax2, cax=cax, ticks=np.arange(1,9))
  cb.ax.set_yticklabels(['<4', '4-6', '6-8', '8-10', '10-12', '12-20', '20-40', '>40'], fontsize=15)
  cb.set_label('years', fontsize=16)


  ax1.set_aspect('auto')
  ax2.set_aspect('auto')
  cax.set_aspect('auto')
  plt.tight_layout()

  f.savefig('retperDelta_rcp85_.png', dpi=200)



  f = plt.figure(figsize=(16,8))

  gs = gridspec.GridSpec(1, 3, width_ratios=[1,1,.05])

  ax1 = plt.subplot(gs[0])
  txt = '$1.5^\circ C$'
  mp = None
  sc, mp = doPlotMinDisFreq(ax1, futRpR4_15, lon, lat, txt, mp)

  ax2 = plt.subplot(gs[1])
  txt = '$2.0^\circ C$'
  sc, mp = doPlotMinDisFreq(ax2, futRpR4_20, lon, lat, txt, mp)

  cax = plt.subplot(gs[2])
  cb = plt.colorbar(sc, ax=ax2, cax=cax, ticks=np.arange(1,9))
  cb.ax.set_yticklabels(['<4', '4-6', '6-8', '8-10', '10-12', '12-20', '20-40', '>40'], fontsize=15)
  cb.set_label('years', fontsize=16)


  ax1.set_aspect('auto')
  ax2.set_aspect('auto')
  cax.set_aspect('auto')
  plt.tight_layout()

  f.savefig('retperDelta_rcp45_.png', dpi=200)


  
  
if __name__ == '__main__':
  plotMinDisFreqChange()
  plt.show()

