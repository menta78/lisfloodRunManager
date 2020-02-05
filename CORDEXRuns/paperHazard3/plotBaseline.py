from loadOutletRetLevFromNc import getAfricaAndTurkeyMask

#from alphaBetaLab import abFixBasemap
import numpy as np
from scipy import stats
from scipy.interpolate import griddata
from matplotlib import pyplot as plt
from matplotlib import gridspec
import matplotlib
from mpl_toolkits import basemap as bm
import matplotlib as mpl
from mpl_toolkits.axes_grid1 import make_axes_locatable, axes_size
from matplotlib import gridspec

import netCDF4


modelName = 'CLMcom-CCLM4-8-17_BC_MPI-M-MPI-ESM-LR'
bslnYear = 1995

def plotVls(ax, vls, mp, txt, cmap='jet', vmax=None):
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

  def getLonLat():
    lonLatFile = 'lonlat.nc'
    ds = netCDF4.Dataset(lonLatFile)
    lon = ds.variables['lon'][:]
    lat = ds.variables['lat'][:]
    return lon, lat
  lon, lat = getLonLat()
  lon, lat = lon.transpose(), lat.transpose()
  x, y = mp(lon, lat)

  plt.axes(ax)
  mp.drawcoastlines(linewidth=.25)
  mp.fillcontinents(color=[.95, .95, .95], lake_color=[.95, .95, .95], zorder=0)
 #mp.drawparallels(np.arange(-180, 180, 10), labels=[1,1])
 #mp.drawmeridians(np.arange(-90, 90, 10), labels=[1,1])
 #pcl = mp.pcolor(lon, lat, vls*100, cmap=cmap)
 #pcl = mp.scatter(lon.flatten(), lat.flatten(), .07, c=vls.flatten()*100, cmap=cmap, alpha=1)

  tamask, _, _ = getAfricaAndTurkeyMask()
  tamask = tamask.transpose()
  vls[~tamask] = np.nan

  cnd = ~np.isnan(vls)
 #xFt = x[cnd]
 #yFt = y[cnd]
  lonFt = lon[cnd]
  latFt = lat[cnd]
  vlsFt = vls[cnd]
  xFt, yFt = mp(lonFt, latFt)
  pcl = plt.scatter(xFt, yFt, .07, c=vlsFt, cmap=cmap, alpha=1, norm=matplotlib.colors.LogNorm())
  divider = make_axes_locatable(ax)
  height = axes_size.AxesX(ax, aspect=1./20)
  pad = axes_size.Fraction(.5, height)
  cax = divider.append_axes("bottom", size=height, pad=pad)
  cb = plt.colorbar(orientation='horizontal', cax=cax)
  if not vmax is None:
    plt.clim(1, vmax)
 #htch = plt.contourf(xgrd, ygrd, signMap, 3, hatches=['', '\\\\\\\\\\'], alpha=0)

 #txtpos = mp(-24, 32)
  txtpos = mp(-22, 69)
  plt.axes(ax)
  plt.annotate(txt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=13)

  return pcl, cb, mp


def plotHighExtremes(ax, mp):
  retPer = 100
  flpath = '/ClimateRun4/multi-hazard/eva/projection_dis_rcp85_' + modelName + '_wuConst_statistics.nc'
  ds = netCDF4.Dataset(flpath)
  rp = ds.variables['return_period'][:]
  yr = ds.variables['year'][:]
  rl = ds.variables['rl'][rp == retPer, yr == bslnYear, :, :].squeeze()
  ds.close()
  dsuparea = netCDF4.Dataset('upArea.nc')
  upArea = dsuparea.variables['upArea'][:].transpose()
  dsuparea.close()
  rl[upArea < 1e9] = np.nan
  pcl, cb, mp = plotVls(ax, rl, mp, 'a: baseline, $Q_{H100}$', vmax=15000)
  cb.set_label('$Q_{H100}$ ($m^3 s^{-1}$)')


def plotLowExtremes(ax, mp):
  retPer = 15
  flpath = '/ClimateRun4/multi-hazard/eva/projection_dis_rcp85_' + modelName + '_wuConst_statistics.nc'
  ds = netCDF4.Dataset(flpath)
  rp = ds.variables['return_period'][:]
  yr = ds.variables['year'][:]
  rl = ds.variables['rl_min'][rp == retPer, yr == bslnYear, :, :].squeeze()
  ds.close()
  dsuparea = netCDF4.Dataset('upArea.nc')
  upArea = dsuparea.variables['upArea'][:].transpose()
  dsuparea.close()
  rl[upArea < 1e9] = np.nan
  pcl, cb, mp = plotVls(ax, rl, mp, 'c: baseline, $Q_{L15}$', vmax=5000)
  cb.set_label('$Q_{L15}$ ($m^3 s^{-1}$)')


def plotMeans(ax, mp):
  flpath = '/ClimateRun4/multi-hazard/eva/projection_dis_rcp85_' + modelName + '_wuConst_statistics.nc'
  ds = netCDF4.Dataset(flpath)
  rp = ds.variables['return_period'][:]
  yr = ds.variables['year_all'][:]
  iyr = np.where(yr == bslnYear)[0][0]
  rl_ = ds.variables['year_mean'][iyr-14:iyr+14, :, :].squeeze()
  ds.close()
  rl = np.nanmean(rl_, 0)
  dsuparea = netCDF4.Dataset('upArea.nc')
  upArea = dsuparea.variables['upArea'][:].transpose()
  dsuparea.close()
  rl[upArea < 1e9] = np.nan
  pcl, cb, mp = plotVls(ax, rl, mp, 'b: baseline, $Q_{M}$', vmax=10000)
  cb.set_label('$Q_M$ ($m^3 s^{-1}$)')
  return mp


def plotBaseline():
  outPng = 'baseline.png'

  f = plt.figure(figsize=(12, 6)) 
  gs = gridspec.GridSpec(1, 3)

  mp = None

  ax0 = plt.subplot(gs[0, 0])
  mp = plotHighExtremes(ax0, mp)

  ax1 = plt.subplot(gs[0, 1])
  mp = plotMeans(ax1, mp)

  ax2 = plt.subplot(gs[0, 2])
  mp = plotLowExtremes(ax2, mp)
  
  plt.tight_layout()

  f.savefig(outPng, dpi=600)
  


if __name__ == '__main__':
  import pdb; pdb.set_trace()
  plotBaseline()
  plt.show()

