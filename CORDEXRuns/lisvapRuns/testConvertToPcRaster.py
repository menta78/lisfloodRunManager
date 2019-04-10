import numpy as np
import os

ncflpth = '/H01_Fresh_Water_Archive/Europe/Cordex/forcing_data/cordex5km/LAEAETRS89_BIAS_EURO-CORDEX/CLMcom-CCLM4-8-17_BC/ICHEC-EC-EARTH/historical/other/Tmax_BCed_1981-2010_1981-2010.nc'

ds = xarray.open_dataset(ncflpth)
tmx = ds.variables['tasmaxAdjust']

tmx100 = np.array(np.squeeze(tmx[100, :, :]))
tmx100str = tmx100.astype(str)
tmx100str[tmx100str == 'nan'] = '1e31'
np.savetxt('test.txt', tmx100str, fmt='%s', delimiter='   ')
os.system('asc2map --clone target.map test.txt test.map')

