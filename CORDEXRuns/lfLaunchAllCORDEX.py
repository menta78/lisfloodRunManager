import os, sys
import netCDF4
libpath = os.path.join( os.path.dirname(os.path.abspath(__file__)), '../' )
sys.path.append(libpath)
from datetime import datetime
from datetutil.relativedelta import relativedelta



def launchAll():
  meteoDataDirectory = '/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/lisflood/input/LAEAETRS89_BIAS_CORDEX'

  models = """
IPSL-INERIS-WRF331F
SMHI-RCA4_BC_CNRM-CERFACS-CNRM-CM5
SMHI-RCA4_BC_ICHEC-EC-EARTH
SMHI-RCA4_BC_IPSL-IPSL-CM5A-MR
SMHI-RCA4_BC_MOHC-HadGEM2-ES
SMHI-RCA4_BC_MPI-M-MPI-ESM-LR
CLMcom-CCLM4-8-17_BC_CNRM-CERFACS-CNRM-CM5
CLMcom-CCLM4-8-17_BC_ICHEC-EC-EARTH		(copying to eos)
CLMcom-CCLM4-8-17_BC_MPI-M-MPI-ESM-LR		(copying to eos)
DMI-HIRHAM5-ICHEC-EC-EARTH_BC			(copying to cid)
KNMI-RACMO22E-ICHEC-EC-EARTH_BC			(copying to cid)
"""
  models = [m.strip(' \n\t\r') for m in models.strip(' \n\t\r').split('\n') if m.strip(' \n\t\r')]
 # READ THE CALENDARS DIRECTLY FROM THE FILES

  scenarios = ['historical', 'rcp85', 'rcp45']  
  calendarDayStartByScen = {
    'historical': datetime(1981, 1, 1)
    'rcp85': datetime(2011, 1, 1)
    'rcp45': datetime(2011, 1, 1)
    }
  calendarDayEndByScen = {
    'historical': datetime(2010, 12, 31)
    'rcp85': datetime(2099, 12, 31)
    'rcp45': datetime(2011, 12, 31)
    }

  waterUse = [True, False]
  waterUseDataPathRoot = '/eos/jeodpp/data/projects/CRITECH/ADAPTATION/lisflood/input/waterdemandCordex/cordex/'
  waterUseDataPath = {
    ('historical', True): os.path.join(waterUseDataPathRoot, 'hist/waterdemand2010/'),
    ('rcp85', True): os.path.join(waterUseDataPathRoot, 'rcp/dynamic/'),
    ('rcp85', False): os.path.join(waterUseDataPathRoot, 'rcp/static/waterdemand2010/'),
    ('rcp45', True): os.path.join(waterUseDataPathRoot, 'rcp/dynamic/'),
    ('rcp45', False): os.path.join(waterUseDataPathRoot, 'rcp/static/waterdemand2010/'),
    }
  landUseDataPathRoot = '/eos/jeodpp/data/projects/CRITECH/ADAPTATION/lisflood/lisfloodRun/LisfloodEurope/maps_netcdf/landuse/'
  landUseDataPath = {
    ('historical', True): os.path.join(landUseDataPathRoot, 'hist/landuse2010/'),
    ('rcp85', True): os.path.join(landUseDataPathRoot, 'rcp/'),
    ('rcp85', False): os.path.join(landUseDataPathRoot, 'hist/landuse2010/'),
    ('rcp45', True): os.path.join(landUseDataPathRoot, 'rcp/'),
    ('rcp45', False): os.path.join(landUseDataPathRoot, 'hist/landuse2010/'),
    }

  for currUseWater in waterUse:
    for scen in scenarios:
      for mdl in models:
        if scen == 'historical' and (not waterUse):
          print('  skipping historical/no water use')
        calendarDayStart = calendarDayStartByScen[scen]
        calendarDayEnd = calendarDayEndByScen[scen]
        meteoDataPath = os.path.join(meteoDataDirectory, mdl, scen)
        curWaterDataPath = waterUseDataPath[(scen, currUseWater)]
        curLandUseDataPath = landUseDataPath[(scen, currUseWater)]
        pths = {
          'meteoDir': meteoDataPath,
          'waterUseDir': curWaterDataPath,
          'landUseDir': landUseDataPath
          }
        launchSingleModel(scen, mdl, calendarDayStart, calendarDayEnd, currUseWater, pths)



def launchSingleModel(scen, mdl, calendarDayStart, calendarDayEnd, waterUse, paths):
  testNcFile = os.path.join(meteoDataPath, 'pr.nc')
  ds = netCDF4.Dataset(testNCFile)
  try:
    calendar = ds.variables['time'].calendar
  except:
    calendar = 'proleptic_gregorian'  
  ds.close() 

  calUnitStr = 'days since ' + calendarDayStart.strftime('%Y-%m-%d')
  try:
    stepEnd = netCDF4.date2num(calendarDayEnd, calUnitStr, calendar)
  except:
    stepEnd = netCDF4.date2num(calendarDayEnd-relativedelta(days=1), calUnitStr, calendar)
  stepEnd = int(stepEnd) + 1

  print('')
  print('  preparing to launch model: {scen} - {mdl} - waterUse=={currUseWater} - calendar=={cal}'.format(
          scen=scen, mdl=mdl, currUseWater=str(currUseWater)), cal=calendar)
  print('  stepStart == ' + calendarDayStart.strftime('%Y-%m-%d'))
  print('  stepEnd == ' + str(stepEnd))
  print('  map paths:')
  for m in paths.keys():
    print('    ' + m + ': ' + paths[m])
  


if __name__ == '__main__':
  launchAll()


