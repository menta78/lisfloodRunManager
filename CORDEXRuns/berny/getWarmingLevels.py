import numpy as np
import scipy.stats as st

  

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
    elif warmingLev == 3.:
      wly = {
        'CLMcom-CCLM4-8-17_BC_CNRM-CERFACS-CNRM-CM5': 2067,
        'CLMcom-CCLM4-8-17_BC_ICHEC-EC-EARTH': 2066,
        'CLMcom-CCLM4-8-17_BC_MPI-M-MPI-ESM-LR': 2067,
        'DMI-HIRHAM5-ICHEC-EC-EARTH_BC': 2065,
        'IPSL-INERIS-WRF331F_BC': 2054,
        'KNMI-RACMO22E-ICHEC-EC-EARTH_BC': 2065,
        'SMHI-RCA4_BC_CNRM-CERFACS-CNRM-CM5': 2067,
        'SMHI-RCA4_BC_ICHEC-EC-EARTH': 2066,
        'SMHI-RCA4_BC_IPSL-IPSL-CM5A-MR': 2054,
        'SMHI-RCA4_BC_MOHC-HadGEM2-ES': 2051,
        'SMHI-RCA4_BC_MPI-M-MPI-ESM-LR': 2067
      }
    elif warmingLev == 4.:
      wly = {
        'CLMcom-CCLM4-8-17_BC_CNRM-CERFACS-CNRM-CM5': 2089,
        'CLMcom-CCLM4-8-17_BC_ICHEC-EC-EARTH': 2090,
        'CLMcom-CCLM4-8-17_BC_MPI-M-MPI-ESM-LR': 2089,
        'DMI-HIRHAM5-ICHEC-EC-EARTH_BC': 2086,
        'IPSL-INERIS-WRF331F_BC': 2073,
        'KNMI-RACMO22E-ICHEC-EC-EARTH_BC': 2087,
        'SMHI-RCA4_BC_CNRM-CERFACS-CNRM-CM5': 2089,
        'SMHI-RCA4_BC_ICHEC-EC-EARTH': 2090,
        'SMHI-RCA4_BC_IPSL-IPSL-CM5A-MR': 2073,
        'SMHI-RCA4_BC_MOHC-HadGEM2-ES': 2071,
        'SMHI-RCA4_BC_MPI-M-MPI-ESM-LR': 2089
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
    elif warmingLev == 3.:
      wly = None
    elif warmingLev == 4.:
      wly = None
  else:
    raise Exception('scenario not supported: ' + scenario)
  return wly



def getWarmingLevelMixDistributionByScen(scenario, warmingLev, startYear=2000, endYear=2150, distHalfWidth=15):
  yrs = np.arange(startYear, endYear)
  
  ndst = distHalfWidth

  wls = getWarmingLevels(scenario, warmingLev)
  mdls = wls.keys()
  dists = []
  for mdl in mdls:
    yr = wls[mdl]
    iyr = np.where(yrs == yr)[0][0]
    iminy = np.max([iyr-ndst, 0])
    imaxy = np.min([iyr+ndst, len(yrs)-1])
    
    dist = np.zeros(yrs.shape)
    dist[iminy:iyr] = np.array([i+1 for i in range(ndst)])
    dist[iyr:imaxy+1] = np.array([ndst+1-i for i in range(ndst+1)])

    dists.append(dist)

  dists = np.array(dists)
  mixDist = np.sum(dists, 0)
  mixDist = mixDist/np.sum(mixDist)

  pdf = st.rv_discrete(values=(yrs, mixDist))

  return pdf



def getWarmingLevelMixDistributions(warmingLev, startYear=2000, endYear=2150):
  pdfR8 = getWarmingLevelMixDistributionByScen('rcp85', warmingLev, startYear=startYear, endYear=endYear)  
  pdfR4 = getWarmingLevelMixDistributionByScen('rcp45', warmingLev, startYear=startYear, endYear=endYear)  
  yrs = pdfR8.xk
  mixDist = (pdfR8.pk + pdfR4.pk)/2.
  pdf = st.rv_discrete(values=(yrs, mixDist))
  return pdf, pdfR8, pdfR4




