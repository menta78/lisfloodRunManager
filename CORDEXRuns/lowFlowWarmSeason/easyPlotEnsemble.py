import netCDF4
import numpy as np
from matplotlib import pyplot as plt

def plotMap(flpth, warmLevStr):

  ds = netCDF4.Dataset(flpth)
  
  vrbl = ds.variables['baseline_rp_shift_' + warmLevStr][:]
  signfc = ds.variables['significant_' + warmLevStr][:]
  lon = ds.variables['lon'][:]
  lat = ds.variables['lat'][:]
  cnd = ~np.isnan(vrbl)
  
  vrbl_ = vrbl[cnd]
  vrbl_[vrbl_ >= 100] = 100
  signfc_ = signfc[cnd]
  lon_ = lon[cnd]
  lat_ = lat[cnd]
  
  plt.figure()
  cndSign = signfc_ > 0
  plt.scatter(lon_[cndSign], lat_[cndSign], s=.1, c=vrbl_[cndSign], cmap='RdYlGn')
  plt.colorbar()
  cndSign = signfc_ == 0
  plt.scatter(lon_[cndSign], lat_[cndSign], s=.1, c='gray')
   

  


