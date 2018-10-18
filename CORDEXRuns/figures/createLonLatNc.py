import netCDF4
import numpy as np

ds0 = netCDF4.Dataset('/ClimateRun4/multi-hazard/eva/dis_rcp45_SMHI-RCA4_BC_ICHEC-EC-EARTH_wuChang_statistics.nc')
xncin = ds0.variables['x']
yncin = ds0.variables['y']

ds = netCDF4.Dataset('lonlat.nc', 'w')

ds.createDimension('x', len(xncin))
ds.createDimension('y', len(yncin))

xnc = ds.createVariable('x', 'f8', ('x',))
xnc[:] = xncin[:]

ync = ds.createVariable('y', 'f8', ('y',))
ync[:] = yncin[:]

lon = np.loadtxt('lon.asc')
lat = np.loadtxt('lat.asc')

lonnc = ds.createVariable('lon', 'f8', ('y', 'x',))
lonnc[:] = lon

latnc = ds.createVariable('lat', 'f8', ('y', 'x',))
latnc[:] = lat

ds.close()
ds0.close()


#verify
ds = netCDF4.Dataset('lonlat.nc')
x = ds.variables['x'][:]
y = ds.variables['y'][:]
lon = ds.variables['lon'][:]
lat = ds.variables['lat'][:]
xmtx, ymtx = np.meshgrid(x, y)

plt.pcolor(xmtx, ymtx, lon)
plt.colorbar()

plt.figure()
plt.pcolor(xmtx, ymtx, lat)
plt.colorbar()

ds.close()


plt.show()

