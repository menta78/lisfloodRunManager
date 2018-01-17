import os, sys
import netCDF4
libpath = os.path.join( os.path.dirname(os.path.abspath(__file__)), '..' )
sys.path.append(libpath)
from datetime import datetime
from dateutil.relativedelta import relativedelta



def launchAll():
  meteoDataDirectory = '/eos/jeodpp/data/projects/CRITECH/ADAPTATION/lisflood/input/LAEAETRS89_BIAS_CORDEX'

  models = """
IPSL-INERIS-WRF331F
SMHI-RCA4_BC_CNRM-CERFACS-CNRM-CM5
SMHI-RCA4_BC_ICHEC-EC-EARTH
SMHI-RCA4_BC_IPSL-IPSL-CM5A-MR
SMHI-RCA4_BC_MOHC-HadGEM2-ES
SMHI-RCA4_BC_MPI-M-MPI-ESM-LR
CLMcom-CCLM4-8-17_BC_CNRM-CERFACS-CNRM-CM5
CLMcom-CCLM4-8-17_BC_ICHEC-EC-EARTH
CLMcom-CCLM4-8-17_BC_MPI-M-MPI-ESM-LR
DMI-HIRHAM5-ICHEC-EC-EARTH_BC
KNMI-RACMO22E-ICHEC-EC-EARTH_BC
"""
  models = [m.strip(' \n\t\r') for m in models.strip(' \n\t\r').split('\n') if m.strip(' \n\t\r')]
 # READ THE CALENDARS DIRECTLY FROM THE FILES

  scenarios = ['historical', 'rcp85', 'rcp45']  
  calendarDayStartByScen = {
    'historical': datetime(1981, 1, 1),
    'rcp85': datetime(2011, 1, 1),
    'rcp45': datetime(2011, 1, 1)
    }
  calendarDayEndByScen = {
    'historical': datetime(2010, 12, 31),
    'rcp85': datetime(2099, 12, 31),
    'rcp45': datetime(2011, 12, 31)
    }

  waterUse = [True, False]
  waterUseDataPathRoot = '/eos/jeodpp/data/projects/CRITECH/ADAPTATION/lisflood/input/waterdemandCordex/cordex'
  waterUseDataPath = {
    ('historical', True): os.path.join(waterUseDataPathRoot, 'hist/waterdemand2010'),
    ('rcp85', True): os.path.join(waterUseDataPathRoot, 'rcp/dynamic'),
    ('rcp85', False): os.path.join(waterUseDataPathRoot, 'rcp/static/waterdemand2010'),
    ('rcp45', True): os.path.join(waterUseDataPathRoot, 'rcp/dynamic'),
    ('rcp45', False): os.path.join(waterUseDataPathRoot, 'rcp/static/waterdemand2010'),
    }
  landUseDataPathRoot = '/eos/jeodpp/data/projects/CRITECH/ADAPTATION/lisflood/lisfloodRun/LisfloodEurope/maps_netcdf/landuse/cordex'
  landUseDataPath = {
    ('historical', True): os.path.join(landUseDataPathRoot, 'hist/landuse2010'),
    ('rcp85', True): os.path.join(landUseDataPathRoot, 'rcp'),
    ('rcp85', False): os.path.join(landUseDataPathRoot, 'hist/landuse2010'),
    ('rcp45', True): os.path.join(landUseDataPathRoot, 'rcp'),
    ('rcp45', False): os.path.join(landUseDataPathRoot, 'hist/landuse2010'),
    }
  staticFracMaps = '/eos/jeodpp/data/projects/CRITECH/ADAPTATION/lisflood/lisfloodRun/LisfloodEurope/maps_netcdf/landuse20112099'
  directRunoffFractionMaps = {
    ('historical', True): staticFracMaps,
    ('rcp85', False): staticFracMaps,
    ('rcp85', True, 'proleptic_gregorian'): os.path.join(staticFracMaps, 'fracsealed/frsealed_2011_2099'),
    ('rcp85', True, '360_day'): os.path.join(staticFracMaps, 'fracsealed_360Day/frsealed_2011_2099'),
    ('rcp85', True, '365_day'): os.path.join(staticFracMaps, 'fracsealed_365Day/frsealed_2011_2099'),
    ('rcp45', False): staticFracMaps,
    ('rcp45', True, 'proleptic_gregorian'): os.path.join(staticFracMaps, 'fracsealed/frsealed_2011_2099'),
    ('rcp45', True, '360_day'): os.path.join(staticFracMaps, 'fracsealed_360Day/frsealed_2011_2099'),
    ('rcp45', True, '365_day'): os.path.join(staticFracMaps, 'fracsealed_365Day/frsealed_2011_2099'),
    }
  forestFractionMaps = {
    ('historical', True): staticFracMaps,
    ('rcp85', False): staticFracMaps,
    ('rcp85', True, 'proleptic_gregorian'): os.path.join(staticFracMaps, 'fracforest/frforet_2011_2099'),
    ('rcp85', True, '360_day'): os.path.join(staticFracMaps, 'fracforest_360Day/frforet_2011_2099'),
    ('rcp85', True, '365_day'): os.path.join(staticFracMaps, 'fracforest_365Day/frforet_2011_2099'),
    ('rcp45', False): staticFracMaps,
    ('rcp45', True, 'proleptic_gregorian'): os.path.join(staticFracMaps, 'fracforest/frforet_2011_2099'),
    ('rcp45', True, '360_day'): os.path.join(staticFracMaps, 'fracforest_360Day/frforet_2011_2099'),
    ('rcp45', True, '365_day'): os.path.join(staticFracMaps, 'fracforest_365Day/frforet_2011_2099'),
    }
  waterFractionMaps = {
    ('historical', True): staticFracMaps,
    ('rcp85', False): staticFracMaps,
    ('rcp85', True): os.path.join(staticFracMaps, 'fracwater/frwater_2011_2099'),
    ('rcp45', False): staticFracMaps,
    ('rcp45', True): os.path.join(staticFracMaps, 'fracwater/frwater_2011_2099'),
    }
  otherFractionMaps = {
    ('historical', True): staticFracMaps,
    ('rcp85', False): staticFracMaps,
    ('rcp85', True, 'proleptic_gregorian'): os.path.join(staticFracMaps, 'fracother/frother_2011_2099'),
    ('rcp85', True, '360_day'): os.path.join(staticFracMaps, 'fracother_360Day/frother_2011_2099'),
    ('rcp85', True, '365_day'): os.path.join(staticFracMaps, 'fracother_365Day/frother_2011_2099'),
    ('rcp45', False): staticFracMaps,
    ('rcp45', True, 'proleptic_gregorian'): os.path.join(staticFracMaps, 'fracother/frother_2011_2099'),
    ('rcp45', True, '360_day'): os.path.join(staticFracMaps, 'fracother_360Day/frother_2011_2099'),
    ('rcp45', True, '365_day'): os.path.join(staticFracMaps, 'fracother_365Day/frother_2011_2099'),
    }
  irrigationFractionMaps = {
    ('historical', True): staticFracMaps,
    ('rcp85', False): staticFracMaps,
    ('rcp85', True): os.path.join(staticFracMaps, 'fracirrigated/frirrig_2011_2099'),
    ('rcp45', False): staticFracMaps,
    ('rcp45', True): os.path.join(staticFracMaps, 'fracirrigated/frirrig_2011_2099'),
    }
  riceFractionMaps = {
    ('historical', True): staticFracMaps,
    ('rcp85', False): staticFracMaps,
    ('rcp85', True): os.path.join(staticFracMaps, 'fracrice/fracrice_2011_2099'),
    ('rcp45', False): staticFracMaps,
    ('rcp45', True): os.path.join(staticFracMaps, 'fracrice/fracrice_2011_2099'),
    }

  prefixWaterUseDomestic = {
    'proleptic_gregorian': 'dom',
    '360_day': 'dom_360Day',
    '365_day': 'dom_365Day'
    }
  prefixWaterUseLivestock = {
    'proleptic_gregorian': 'liv',
    '360_day': 'liv_360Day',
    '365_day': 'liv_365Day'
    }
  prefixWaterUseEnergy = {
    'proleptic_gregorian': 'ene',
    '360_day': 'ene_360Day',
    '365_day': 'ene_365Day'
    }
  prefixWaterUseIndustry = {
    'proleptic_gregorian': 'ind',
    '360_day': 'ind_360Day',
    '365_day': 'ind_365Day'
    }
  

  def getCalendar(meteoDataPath):
    testNcFile = os.path.join(meteoDataPath, 'pr.nc')
    ds = netCDF4.Dataset(testNcFile)
    try:
      calendar = ds.variables['time'].calendar
    except:
      calendar = 'proleptic_gregorian'  
    ds.close() 
    return calendar
 

  def getMapPath(dctnr, scen, useWater, calendar):
    key1 = (scen, useWater, calendar)
    key2 = (scen, useWater)
    return dctnr.get(key1, dctnr.get(key2, ''))


  for scen in scenarios:
    for currUseWater in waterUse:
      for mdl in models:
        if scen == 'historical' and (not currUseWater):
          print('')
          continue
        calendarDayStart = calendarDayStartByScen[scen]
        calendarDayEnd = calendarDayEndByScen[scen]
        meteoDataPath = os.path.join(meteoDataDirectory, mdl, scen)
        calendar = getCalendar(meteoDataPath)
        curWaterDataPath = waterUseDataPath[(scen, currUseWater)]
        curLandUseDataPath = landUseDataPath[(scen, currUseWater)]
        cDirectRunoffFractionMaps = getMapPath(directRunoffFractionMaps, scen, currUseWater, calendar)
        cForestFractionMaps = getMapPath(forestFractionMaps, scen, currUseWater, calendar)
        cWaterFractionMaps = getMapPath(waterFractionMaps, scen, currUseWater, calendar)
        cOtherFractionMaps = getMapPath(otherFractionMaps, scen, currUseWater, calendar)
        cIrrigationFractionMaps = getMapPath(irrigationFractionMaps, scen, currUseWater, calendar)
        cRiceFractionMaps = getMapPath(riceFractionMaps, scen, currUseWater, calendar)
        cPoulationMap = os.path.join(curWaterDataPath, 'pop')
        cPrefixWaterUseDomestic = prefixWaterUseDomestic[calendar]
        cPrefixWaterUseLivestock = prefixWaterUseLivestock[calendar]
        cPrefixWaterUseEnergy = prefixWaterUseEnergy[calendar]
        cPrefixWaterUseIndustry = prefixWaterUseIndustry[calendar]
        miscVars = {
          'meteoDir': meteoDataPath,
          'waterUseDir': curWaterDataPath,
          'landUseDir': curLandUseDataPath,
          'directRunoffFractionMaps': cDirectRunoffFractionMaps,
          'forestFractionMaps': cForestFractionMaps,
          'waterFractionMaps': cWaterFractionMaps,
          'otherFractionMaps': cOtherFractionMaps,
          'irrigationFractionMaps': cIrrigationFractionMaps,
          'riceFractionMaps': cRiceFractionMaps,
          'populationMaps': cPoulationMap,
          'prefixWaterUseDomestic': cPrefixWaterUseDomestic,
          'prefixWaterUseLivestock': cPrefixWaterUseLivestock,
          'prefixWaterUseEnergy': cPrefixWaterUseEnergy,
          'prefixWaterUseIndustry': cPrefixWaterUseIndustry
          }
        launchSingleModel(scen, mdl, calendarDayStart, calendarDayEnd, calendar, currUseWater, miscVars)



def launchSingleModel(scen, mdl, calendarDayStart, calendarDayEnd, calendar, waterUse, miscVars):
  calUnitStr = 'days since ' + calendarDayStart.strftime('%Y-%m-%d')
  try:
    stepEnd = netCDF4.date2num(calendarDayEnd, calUnitStr, calendar)
  except:
    stepEnd = netCDF4.date2num(calendarDayEnd-relativedelta(days=1), calUnitStr, calendar)
  stepEnd = int(stepEnd) + 1

  print('')
  print('  preparing to launch model: {scen} - {mdl} - waterUse=={waterUse} - calendar=={cal}'.format(
          scen=scen, mdl=mdl, waterUse=str(waterUse), cal=calendar))
  print('  stepStart == ' + calendarDayStart.strftime('%Y-%m-%d'))
  print('  stepEnd == ' + str(stepEnd))
  print('  map miscVars:')
  ks = miscVars.keys()
  ks.sort()
  for m in ks:
    print('    ' + m + ': ' + miscVars[m])
  


if __name__ == '__main__':
  launchAll()


