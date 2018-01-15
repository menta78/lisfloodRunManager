import os
import netCDF4


def launchAll():
  meteoDataDirectory = '/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/lisflood/input/LAEAETRS89_BIAS_CORDEX'

  models = """
IPSL-INERIS-WRF331F
SMHI-RCA4_BC_CNRM-CERFACS-CNRM-CM5
SMHI-RCA4_BC_ICHEC-EC-EARTH
SMHI-RCA4_BC_IPSL-IPSL-CM5A-MR
SMHI-RCA4_BC_MOHC-HadGEM2-ES			(to be copied)
SMHI-RCA4_BC_MPI-M-MPI-ESM-LR			(to be copied)
CLMcom-CCLM4-8-17_BC_CNRM-CERFACS-CNRM-CM5	(to be copied)
CLMcom-CCLM4-8-17_BC_ICHEC-EC-EARTH		(to be copied)
CLMcom-CCLM4-8-17_BC_MPI-M-MPI-ESM-LR		(to be copied)
DMI-HIRHAM5-ICHEC-EC-EARTH_BC			(to be copied)
KNMI-RACMO22E-ICHEC-EC-EARTH_BC			(to be copied)
"""
  models = models.strip(' \n\t\r').split('\n')
 # READ THE CALENDARS DIRECTLY FROM THE FILES

  scenarios = ['historical', 'rcp85', 'rcp45']  

  waterUse = [True, False]
  waterUseDataPath = [
    'TO_BE_COPIED_TO_EOS',
    'TO_BE_COPIED_TO_EOS'
    ]

  for currUseWater, currWaterDataPath in zip(waterUse, currWaterDataPath):
    for scen in scenarios:
      for mdl in models:
        launchSingleModel(scen, mdl, currUseWater, currWaterDataPath)



def launchSingleModel(scen, mdl, waterUse, waterUseDataPath):
  meteoDataPath = os.path.join(meteoDataDirectory, mdl, scen)

  testNcFile = os.path.join(meteoDataPath, 'pr.nc')
  ds = netCDF4.Dataset(testNCFile)
  try:
    calendar = ds.variables['time'].calendar
  except:
    calendar = 'proleptic_gregorian'  
  ds.close() 
  print('')
  print('  preparing to launch model: {scen} - {mdl} - waterUse=={currUseWater} - calendar=={cal}'.format(
          scen=scen, mdl=mdl, currUseWater=str(currUseWater)), cal=calendar)
  


if __name__ == '__main__':
  launchAll()


