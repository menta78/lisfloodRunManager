import os
import numpy as np
from matplotlib import pyplot as plt
import xarray
import scipy.interpolate as si


mdldir = os.path.dirname(os.path.abspath(__file__))
defaultOutletNcFlPath = os.path.join(mdldir, 'outlets.nc')


def plotMap(outletNcFlPath=defaultOutletNcFlPath):
  ds = xarray.open_dataset(outletNcFlPath)
  x = ds.variables['x'][:]
  dx = np.abs(x[1] - x[0])
  y = ds.variables['y'][:]
  dy = np.abs(y[1] - y[0])
  outlets = ds.variables['outlets'][:]

  xmtx, ymtx = np.meshgrid(x, y)
  pc = plt.pcolor(xmtx, ymtx, outlets)

  def fmt(xloc, yloc):
    ix = np.where(np.abs(x - xloc) < dx)
    iy = np.where(np.abs(y - yloc) < dy)
    z = np.nanmax(outlets[iy, ix])
    ss = 'x={x:.5f}  y={y:.5f}  z={z:.5f}'.format(x=xloc, y=yloc, z=z)
    return ss

  def plotClick(event):
    ss = fmt(event.xdata, event.ydata)
    print(ss)

  pc.axes.format_coord = fmt
  plt.gcf().canvas.mpl_connect('button_press_event', plotClick)
  plt.show()


