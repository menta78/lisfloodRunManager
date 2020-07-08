import re, os
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import gridspec
from alphaBetaLab import abFixBasemap
from mpl_toolkits import basemap as bm
from scipy.interpolate import interp1d
import netCDF4
import pickle


ncdir = '/ClimateRun4/HELIX/global/dis/output/tsEVA/returnPeriodShift/'
ncdir = '../returnPeriodShift/'
outputNcFlPath = './helixDisEnsemble.nc'


def doLoadData(warmingLev=2, retPer=100):

  mdlvls = []
  mdlRetLev = []

  fls = [f for f in os.listdir(ncdir) if re.match('returnPeriodShift_(.*).nc', f)]
  fls.sort()
  for f, ifl in zip(fls, range(len(fls))):
    fpth = os.path.join(ncdir, f)
    print('  loading ' + fpth)
    ds = netCDF4.Dataset(fpth)

    if ifl == 0:
      lon = ds.variables['lon'][:]
      lat = ds.variables['lat'][:]

    wlev = ds.variables['warming_lev'][:]
    iwlev = wlev == warmingLev
    retpers = ds.variables['baseline_rp'][:]
    irp = retpers == retPer
    rpShift = ds.variables['baseline_rp_shift'][iwlev, irp, :, :].squeeze()
    mdlvls.append(rpShift)
    retLev = ds.variables['return_level'][iwlev, irp, :, :].squeeze()
    mdlRetLev.append(retLev)
    
  mdlvls = np.array(mdlvls)
  mdn = np.nanmedian(mdlvls, 0)
 #mdn = np.nanmean(np.array(mdlvls), 0)
  mdlRetLev = np.array(mdlRetLev)

  return lon, lat, mdn, mdlvls, mdlRetLev


def doLoadBaseline(retPer=100):

  mdlvls = []

  fls = [f for f in os.listdir(ncdir) if re.match('returnPeriodShift_(.*).nc', f)]
  fls.sort()
  for f, ifl in zip(fls, range(len(fls))):
    fpth = os.path.join(ncdir, f)
    print('  loading ' + fpth)
    ds = netCDF4.Dataset(fpth)

    if ifl == 0:
      lon = ds.variables['lon'][:]
      lat = ds.variables['lat'][:]

    wlev = ds.variables['warming_lev'][:]
    retpers = ds.variables['baseline_rp'][:]
    irp = retpers == retPer
    if 'baseline_return_level' in ds.variables:
      retlev = ds.variables['baseline_return_level'][irp, :, :].squeeze()
    else:
      retlev = np.zeros([len(lon), len(lat)])*np.nan
   #iwlev = wlev == 1.5
   #retlev = ds.variables['return_level'][iwlev, irp, :, :].squeeze()
    mdlvls.append(retlev)
    
  mdlvls = np.array(mdlvls)
  mdn = np.nanmedian(np.array(mdlvls), 0)
 #mdn = np.nanmean(np.array(mdlvls), 0)

  return lon, lat, mdn, mdlvls
    



def saveEnsembleFile():

  lon, lat, retLev, retLevByMdl = doLoadBaseline()
  lon, lat, futRp_15, _, rlByMdl_15 = doLoadData(warmingLev=1.5)
  lon, lat, futRp_20, _, rlByMdl_20 = doLoadData(warmingLev=2.0)
  lon, lat, futRp_30, _, rlByMdl_30 = doLoadData(warmingLev=3.0)

  retLevChng_15_mdl = (rlByMdl_15 - retLevByMdl)/retLevByMdl
  retLevChng_20_mdl = (rlByMdl_20 - retLevByMdl)/retLevByMdl
  retLevChng_30_mdl = (rlByMdl_30 - retLevByMdl)/retLevByMdl

  retLevChng_15 = np.nanmedian(retLevChng_15_mdl, 0)
  retLevChng_20 = np.nanmedian(retLevChng_20_mdl, 0)
  retLevChng_30 = np.nanmedian(retLevChng_30_mdl, 0)

  dsout = netCDF4.Dataset(outputNcFlPath, 'w')
  dsout.createDimension('lon', len(lon))
  dsout.createDimension('lat', len(lat))
  
  lonnc = dsout.createVariable('lon', 'f8', ('lon'))
  lonnc.description = 'longitude mtx'
  lonnc[:] = lon

  latnc = dsout.createVariable('lat', 'f8', ('lat'))
  latnc.description = 'latitude mtx'
  latnc[:] = lat

  bslnRetLevNc = dsout.createVariable('baseline_return_level', 'f4', ('lon', 'lat'))
  bslnRetLevNc.description = 'return levels at baseline'
  bslnRetLevNc[:] = retLev

  rlChng15 = dsout.createVariable('return_level_perc_chng_15', 'f4', ('lon', 'lat'))
  rlChng15[:] = retLevChng_15*100

  rlChng20 = dsout.createVariable('return_level_perc_chng_20', 'f4', ('lon', 'lat'))
  rlChng20[:] = retLevChng_20*100

  rlChng30 = dsout.createVariable('return_level_perc_chng_30', 'f4', ('lon', 'lat'))
  rlChng30[:] = retLevChng_30*100

  rpshift15 = dsout.createVariable('baseline_rp_shift_15', 'f4', ('lon', 'lat'))
  rpshift15[:] = futRp_15

  rpshift20 = dsout.createVariable('baseline_rp_shift_20', 'f4', ('lon', 'lat'))
  rpshift20[:] = futRp_20

  rpshift30 = dsout.createVariable('baseline_rp_shift_30', 'f4', ('lon', 'lat'))
  rpshift30[:] = futRp_30

  dsout.close()

  
  
  
if __name__ == '__main__':
  import pdb; pdb.set_trace()

 #ncdir = '/ClimateRun4/multi-hazard/eva/prFrequencyShift_std/'
 #outputNcFlPath = './precipitationEnsemble.nc'
 #plotFreqChange15_20_30deg()
 #saveEnsembleFile()

 #ncdir = '/DATA/mentalo/Dropbox/notSynced/xEamonn'
 #ncdir = '/ClimateRun4/multi-hazard/eva/eamonn/'
 #outputNcFlPath = '/DATA/mentalo/Dropbox/notSynced/xEamonn/disEnsemble.nc'
  saveEnsembleFile()


