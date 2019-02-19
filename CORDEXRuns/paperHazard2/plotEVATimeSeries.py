import numpy as np
import netCDF4
from matplotlib import pyplot as plt


def plotTimeSeries(ncfilepath, ix, iy, txt, outpng, rp1=10, rp2=50, rp3=100, legendloc='upper left'):
  ds = netCDF4.Dataset(ncfilepath)

  ix_, iy_ = ix, 950-iy

  yall = ds.variables['year_all']
  ymax = ds.variables['year_max'][:, ix_, iy_]

  retPer = ds.variables['return_period'][:]
  y = ds.variables['year'][:]
  rl1 = ds.variables['rl'][retPer==rp1, :, ix_, iy_].squeeze()
  rl2 = ds.variables['rl'][retPer==rp2, :, ix_, iy_].squeeze()
  rl3 = ds.variables['rl'][retPer==rp3, :, ix_, iy_].squeeze()

  f = plt.figure()
  plt.plot(yall, ymax, 'o', label='y. max')
  plt.plot(y, rl1, label='10-y r.l.')
  plt.plot(y, rl2, label='50-y r.l.')
  plt.plot(y, rl3, label='100-y r.l.')
  plt.grid('on')
  plt.legend(loc=legendloc)
  plt.xlabel('year')
  plt.ylabel('Q ($m^3s^{-1}$)')
  plt.title(txt)
  f.savefig(outpng, dpi=300)
  


def plotLoire():
  ncfilepath = '/DATA/multi-hazard/discharge/projection_dis_rcp85_IPSL-INERIS-WRF331F_BC_wuChang_statistics.nc'
 #ncfilepath = '/DATA/multi-hazard/discharge/projection_dis_rcp45_DMI-HIRHAM5-ICHEC-EC-EARTH_BC_wuChang_statistics.nc'
  ix = 204
  iy = 401
  plotTimeSeries(ncfilepath, ix, iy, 'Loire', 'evaLoire.png')
  plt.show()

def plotDanube():
  ncfilepath = '/DATA/multi-hazard/discharge/projection_dis_rcp85_IPSL-INERIS-WRF331F_BC_wuChang_statistics.nc'
 #ncfilepath = '/DATA/multi-hazard/discharge/projection_dis_rcp45_DMI-HIRHAM5-ICHEC-EC-EARTH_BC_wuChang_statistics.nc'
  ix = 492
  iy = 406
  plotTimeSeries(ncfilepath, ix, iy, 'Danube', 'evaDanube.png', legendloc='lower right')
  plt.show()

def plotRhine():
  ncfilepath = '/DATA/multi-hazard/discharge/projection_dis_rcp85_IPSL-INERIS-WRF331F_BC_wuChang_statistics.nc'
 #ncfilepath = '/DATA/multi-hazard/discharge/projection_dis_rcp45_DMI-HIRHAM5-ICHEC-EC-EARTH_BC_wuChang_statistics.nc'
  ix = 311
  iy = 490
  plotTimeSeries(ncfilepath, ix, iy, 'Rhine', 'evaRhine.png')
  plt.show()


