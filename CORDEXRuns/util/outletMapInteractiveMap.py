import numpy as np
from matplotlib import pyplot as plt
import xarray
import scipy.interpolate as si


defaultOutletNcFlPath = '/eos/jeodpp/data/projects/CRITECH/ADAPTATION/lisflood/lisfloodRun/LisfloodEurope/maps_netcdf/outlets.nc'


def plotMap(outledNcFlPath=defaultOutletNcFlPath):
  ds = xarray.open_dataset(flpth)
  x = ds.variables['x'][:]
  y = ds.variables['y'][:]
  outlets = ds.variables['outlets'][:]

  xmtx, ymtx = np.meshgrid(x, y)
  plt.pcolor(xmtx, ymtx, outlets)

  def fmt(xloc, yloc):
    z = np.take(si.interp2d(x, y, outlets)(xloc, yloc), 0)
    return 'x={x:.5f}  y={y:.5f}  z={z:.5f}'.format(x=x, y=y, z=z)

  plt.gca().format_coord = fmt
  plt.show()


