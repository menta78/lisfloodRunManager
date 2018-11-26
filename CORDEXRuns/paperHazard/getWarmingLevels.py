
  
def getWarmingLevels(scenario, warmingLev):
  wly = {}
  if scenario == 'rcp85':
    if warmingLev == 1.5:
      wly = {
        'CLMcom-CCLM4-8-17_BC_CNRM-CERFACS-CNRM-CM5': 2029,
        'CLMcom-CCLM4-8-17_BC_ICHEC-EC-EARTH': 2026,
        'CLMcom-CCLM4-8-17_BC_MPI-M-MPI-ESM-LR': 2028,
        'DMI-HIRHAM5-ICHEC-EC-EARTH_BC': 2028,
        'IPSL-INERIS-WRF331F_BC': 2021,
        'KNMI-RACMO22E-ICHEC-EC-EARTH_BC': 2026,
        'SMHI-RCA4_BC_CNRM-CERFACS-CNRM-CM5': 2029,
        'SMHI-RCA4_BC_ICHEC-EC-EARTH': 2026,
        'SMHI-RCA4_BC_IPSL-IPSL-CM5A-MR': 2021,
        'SMHI-RCA4_BC_MOHC-HadGEM2-ES': 2018,
        'SMHI-RCA4_BC_MPI-M-MPI-ESM-LR': 2028
      }
    elif warmingLev == 2.:
      wly = {
        'CLMcom-CCLM4-8-17_BC_CNRM-CERFACS-CNRM-CM5': 2044,
        'CLMcom-CCLM4-8-17_BC_ICHEC-EC-EARTH': 2041,
        'CLMcom-CCLM4-8-17_BC_MPI-M-MPI-ESM-LR': 2044,
        'DMI-HIRHAM5-ICHEC-EC-EARTH_BC': 2043,
        'IPSL-INERIS-WRF331F_BC': 2035,
        'KNMI-RACMO22E-ICHEC-EC-EARTH_BC': 2042,
        'SMHI-RCA4_BC_CNRM-CERFACS-CNRM-CM5': 2044,
        'SMHI-RCA4_BC_ICHEC-EC-EARTH': 2041,
        'SMHI-RCA4_BC_IPSL-IPSL-CM5A-MR': 2035,
        'SMHI-RCA4_BC_MOHC-HadGEM2-ES': 2030,
        'SMHI-RCA4_BC_MPI-M-MPI-ESM-LR': 2044
      }
    else:
      raise Exception('warming level not supported: ' + str(warmingLev)) 
  elif scenario == 'rcp45':
    if warmingLev == 1.5:
      wly = {
        'CLMcom-CCLM4-8-17_BC_CNRM-CERFACS-CNRM-CM5': 2035,
        'CLMcom-CCLM4-8-17_BC_ICHEC-EC-EARTH': 2033,
        'CLMcom-CCLM4-8-17_BC_MPI-M-MPI-ESM-LR': 2034,
        'DMI-HIRHAM5-ICHEC-EC-EARTH_BC': 2032,
        'IPSL-INERIS-WRF331F_BC': 2023,
        'KNMI-RACMO22E-ICHEC-EC-EARTH_BC': 2032,
        'SMHI-RCA4_BC_CNRM-CERFACS-CNRM-CM5': 2035,
        'SMHI-RCA4_BC_ICHEC-EC-EARTH': 2033,
        'SMHI-RCA4_BC_IPSL-IPSL-CM5A-MR': 2023,
        'SMHI-RCA4_BC_MOHC-HadGEM2-ES': 2021,
        'SMHI-RCA4_BC_MPI-M-MPI-ESM-LR': 2034
      }
    elif warmingLev == 2.:
      wly = {
        'CLMcom-CCLM4-8-17_BC_CNRM-CERFACS-CNRM-CM5': 2057,
        'CLMcom-CCLM4-8-17_BC_ICHEC-EC-EARTH': 2056,
        'CLMcom-CCLM4-8-17_BC_MPI-M-MPI-ESM-LR': 2064,
        'DMI-HIRHAM5-ICHEC-EC-EARTH_BC': 2054,
        'IPSL-INERIS-WRF331F_BC': 2042,
        'KNMI-RACMO22E-ICHEC-EC-EARTH_BC': 2056,
        'SMHI-RCA4_BC_CNRM-CERFACS-CNRM-CM5': 2057,
        'SMHI-RCA4_BC_ICHEC-EC-EARTH': 2056,
        'SMHI-RCA4_BC_IPSL-IPSL-CM5A-MR': 2042,
        'SMHI-RCA4_BC_MOHC-HadGEM2-ES': 2037,
        'SMHI-RCA4_BC_MPI-M-MPI-ESM-LR': 2064
      }
  else:
    raise Exception('scenario not supported: ' + scenario)
  return wly

