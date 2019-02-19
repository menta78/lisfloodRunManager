import netCDF4
from matplotlib import pyplot as plt

outpng = 'domain.png'

ncEvaMapPth = '/ClimateRun4/multi-hazard/eva/projection_dis_rcp45_CLMcom-CCLM4-8-17_BC_ICHEC-EC-EARTH_wuChang_statistics.nc'

disDs = netCDF4.Dataset(ncEvaMapPth)
rl = disDs.variables['rl'][0, 0, :, :].transpose()
cnd = ~np.isnan(rl)

lonlatDs = netCDF4.Dataset('lonlat.nc')
lon_ = lonlatDs.variables['lon'][:]
lat_ = lonlatDs.variables['lat'][:]

lon = lon_[cnd]
lat = lat_[cnd]

f = plt.figure()
plt.scatter(lon, lat, s=.1, c='k', cmap='Greys'); plt.grid('on')
f.savefig(outpng, dpi=300)



