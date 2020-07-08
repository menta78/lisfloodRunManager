import numpy as np
from scipy.interpolate import RegularGridInterpolator

import pandas
import netCDF4

inputfile = 'WPI2019_HW.xls'

inputNcFile = 'helixDisEnsemble.nc'
retLevChng15Var = 'return_level_perc_chng_15'
retLevChng20Var = 'return_level_perc_chng_20'
retLevChng30Var = 'return_level_perc_chng_30'
baselineRpShift15Var = 'baseline_rp_shift_15'
baselineRpShift20Var = 'baseline_rp_shift_20'
baselineRpShift30Var = 'baseline_rp_shift_30'



outputfile = 'WPI2019_HW_RNF.xls'
retLevChng15TabVar = 'RUNOFF_PERC_CHANGE_15'
retLevChng20TabVar = 'RUNOFF_PERC_CHANGE_20'
retLevChng30TabVar = 'RUNOFF_PERC_CHANGE_30'
frqRatio15TabVar = 'RUNOFF_FREQ_INCREASE_RATIO_15'
frqRatio20TabVar = 'RUNOFF_FREQ_INCREASE_RATIO_20'
frqRatio30TabVar = 'RUNOFF_FREQ_INCREASE_RATIO_30'




ds = netCDF4.Dataset(inputNcFile)
lon = ds.variables['lon'][:]
lat = ds.variables['lat'][:][::-1]
cnd = retLevChng15 > 10
retLevChng15 = ds.variables[retLevChng15Var][:].transpose()[::-1,:]
retLevChng20 = ds.variables[retLevChng20Var][:].transpose()[::-1,:]
retLevChng30 = ds.variables[retLevChng30Var][:].transpose()[::-1,:]
rpShft15 = ds.variables[baselineRpShift15Var][:].transpose()[::-1,:]
rpShft20 = ds.variables[baselineRpShift20Var][:].transpose()[::-1,:]
rpShft30 = ds.variables[baselineRpShift30Var][:].transpose()[::-1,:]
ds.close()
#cndNan = retLevChng15 < 10
#retLevChng15[cndNan] = np.nan


retLevChng15Intp = RegularGridInterpolator([lat, lon], retLevChng15, method='nearest', bounds_error=False, fill_value=None)
retLevChng20Intp = RegularGridInterpolator([lat, lon], retLevChng20, method='nearest', bounds_error=False, fill_value=None)
retLevChng30Intp = RegularGridInterpolator([lat, lon], retLevChng30, method='nearest', bounds_error=False, fill_value=None)
rpShft15Intp = RegularGridInterpolator([lat, lon], rpShft15, method='nearest', bounds_error=False, fill_value=None)
rpShft20Intp = RegularGridInterpolator([lat, lon], rpShft20, method='nearest', bounds_error=False, fill_value=None)
rpShft30Intp = RegularGridInterpolator([lat, lon], rpShft30, method='nearest', bounds_error=False, fill_value=None)


wpiTab = pandas.read_excel(inputfile)
pts = wpiTab[['LATITUDE', 'LONGITUDE']]

retLevChng15Pts = retLevChng15Intp(pts)
retLevChng20Pts = retLevChng20Intp(pts)
retLevChng30Pts = retLevChng30Intp(pts)
rpShft15Pts = rpShft15Intp(pts)
rpShft20Pts = rpShft20Intp(pts)
rpShft30Pts = rpShft30Intp(pts)
frqRatio15 = 100/rpShft15Pts 
frqRatio20 = 100/rpShft20Pts
frqRatio30 = 100/rpShft30Pts

wpiTab[retLevChng15TabVar] = retLevChng15Pts
wpiTab[retLevChng20TabVar] = retLevChng20Pts
wpiTab[retLevChng30TabVar] = retLevChng30Pts
wpiTab[frqRatio15TabVar] = frqRatio15
wpiTab[frqRatio20TabVar] = frqRatio20
wpiTab[frqRatio30TabVar] = frqRatio30



wpiTab.to_excel(outputfile)

