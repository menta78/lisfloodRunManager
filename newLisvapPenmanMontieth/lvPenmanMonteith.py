import os
import xarray
import lvPhysics



def run(settings):
  s = settings


  print('preparing the input variables')
  relativeHumidityDs = xarray.open_dataset(os.path.join(s.inputDir, s.relativeHumidityNcFile))
  relativeHumidity = relativeHumidityDs.variables[s.relativeHumidityNcVar]

  solarRadiationWmsNcDs = xarray.open_dataset(os.path.join(s.inputDir, s.solarRadiationWm2NcFile))
  solarRadiationWms = solarRadiationWmsNcDs.variables[s.solarRadiationWm2NcVar]

  sfcWindNcDs = xarray.open_dataset(os.path.join(s.inputDir, s.sfcWindNcFile))
  sfcWind = sfcWindNcDs.variables[s.sfcWindNcVar]

  tmaxNcDs = xarray.open_dataset(os.path.join(s.inputDir, s.tmaxNcFile))
  tmax = tmaxNcDs.variables[s.tmaxNcVar]

  tminNcDs = xarray.open_dataset(os.path.join(s.inputDir, s.tminNcFile))
  tmin = tminNcDs.variables[s.tminNcVar]

  sfcPressureNcDs = xarray.open_dataset(os.path.join(s.inputDir, s.sfcPressureNcFile))
  sfcPressure = sfcPressureNcDs.variables[s.sfcPressureNcVar]


  print('estimating the average temperature')
  ta = (tmax + tmin)/2.

  
  print('estimating the absorbed solar radiation')
  rgd = solarRadiationWms*86400 # converting to J/m^2/Day


