import numpy as np
from matplotlib import pyplot as plt
from matplotlib import gridspec
from mpl_toolkits import basemap as bm

import netCDF4

def plotRetPerMap(ax, lon, lat, retPer, mp, txt, cmap='autumn_r', showColorbar=True):
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

  x, y = mp(lon, lat)

  plt.axes(ax)
  mp.drawcoastlines(linewidth=.25)
  mp.fillcontinents(color=[.95, .95, .95], lake_color=[.95, .95, .95], zorder=0)
  retPerLev = np.zeros(retPer.shape)
  retPerLev[retPer <= 5] = 1
  retPerLev[np.logical_and(retPer > 5, retPer <= 10)] = 2
  retPerLev[np.logical_and(retPer > 10, retPer <= 20)] = 3
  retPerLev[np.logical_and(retPer > 20, retPer <= 50)] = 4
  retPerLev[retPer > 50] = 5
  vmin = 0
  vmax = 5
  pcl = plt.scatter(x.flatten(), y.flatten(), 1, c=retPerLev.flatten(), cmap=cmap, alpha=1, linewidth=0)
  vmin = -vmax if vmin is None else vmin
  plt.clim(vmin, vmax)

  txtpos = mp(-24, 32)
 #txtpos = mp(-22, 69)
  plt.annotate(txt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=13)

  if showColorbar:
    cb = plt.colorbar(ticks=[0,1,2,3,4,5])
    cb.ax.set_yticklabels(['', '5', '10', '20', '50', ''], fontsize=12)
    cb.set_label('return period (years)', fontsize=13)

  return pcl, mp



def plotRetPerMapsFromFile(filePath, flstr):
  print('loading the data ...')
  ds = netCDF4.Dataset(filePath)
  yys = ds.variables['year'][:]
  le_ = ds.variables['le'][:]
  rp_ = ds.variables['rp'][:]
  lon_ = ds.variables['lon'][:]
  lat_ = ds.variables['lat'][:]
  ds.close()

  dsup = netCDF4.Dataset('upArea.nc')
  upArea = dsup.variables['upArea'][:]
  dsup.close()

  lemn = np.nanmean(le_, 0)
  cnd = np.logical_and(lemn >= 3, upArea >= 1000000000)
  cnd3d = np.tile(cnd, [len(yys), 1, 1])
  le = le_[cnd3d].reshape(len(yys), np.sum(cnd))
  rp = rp_[cnd3d].reshape(len(yys), np.sum(cnd))
  lon = lon_[cnd]
  lat = lat_[cnd]
  mp = None
  for yy, iyy in zip(yys, range(len(yys))):
    print('plotting ' + str(yy))
    rpi = rp[iyy, :]
    fig = plt.figure(figsize=(6,5))
    ax = fig.gca()
    p, mp = plotRetPerMap(ax, lon, lat, rpi, mp, str(int(yy)))
    fig.tight_layout()
    fig.savefig('minDischargeRetPer_' + flstr + '_' + str(yy) + '.png', dpi=200)
    
    


  
if __name__ == '__main__':
  import pdb; pdb.set_trace()
 #fpath = '/ClimateRun4/multi-hazard/eva/historical_dis_monMeanMin_NCEP_year_statistics.nc'
 #flstr = '1monthRnMean'

 #fpath = '/ClimateRun4/multi-hazard/eva/historical_dis_mon7dMeanMin_NCEP_year_statistics.nc'
 #flstr = '7dRnMean'

  fpath = '/ClimateRun4/multi-hazard/eva/historical_dis_mon14dMeanMin_NCEP_year_statistics.nc'
  flstr = '14dRnMean'

  plotRetPerMapsFromFile(fpath, flstr)

