import os, glob
import xarray as xr
import numpy as np

from matplotlib import pyplot as plt
import cartopy.crs as ccrs
from matplotlib import gridspec


ncfldir = '/Applications/mentaDropbox/Dropbox/notSynced/xClaudiaHahn'
refrp = 100

def getFileRelativeChange(ncfl, year):
  ds = xr.open_dataset(ncfl)
  rp = ds.variables['baseline_rp']
  rl = ds.variables['return_level']
  yr = ds.variables['year']
  rlchng = rl[yr==year, rp==refrp]/rl[yr==1996, rp==refrp][0,:]
  rslt = rlchng.values[:].squeeze()
  ds.close()
  return rslt


def getEnsembleRelativeChange(scen, year):
  fls = glob.glob(os.path.join(ncfldir, 'returnPeriodShift_dis_' + scen + '_*'))
  rlchngs = []
  for ncfl in fls:
    print('loading file ' + ncfl)
    rlchng = getFileRelativeChange(ncfl, year)
    rlchngs.append(rlchng)
  rlchngs = np.array(rlchngs)
  return rlchngs


def getInterqRngOverRelChng(scen, year):
  rlchngs = getEnsembleRelativeChange(scen, year)
  prcntls = np.nanpercentile(rlchngs, [50, 25, 75], axis=0)
  mdn = np.abs(prcntls[0])
  iqRng = np.abs(prcntls[2]-prcntls[1])
  ratio = iqRng/mdn
  return ratio


def plotRatio(scen, year, ax=None):
  if ax is None:
    ax = plt.axes(projection=ccrs.PlateCarree())
  ax.coastlines()
  refFile = os.path.join(ncfldir, 'returnPeriodShift_dis_rcp45_SMHI-RCA4_BC_MPI-M-MPI-ESM-LR_wuConst_statistics.nc')
  ds = xr.open_dataset(refFile)
  lon = ds.variables['lon'].values[:]
  lat = ds.variables['lat'].values[:]
  ds.close()

  ratio = getInterqRngOverRelChng(scen, year)

  mskEast = np.logical_and(lat <= 66.47, lon >= 34.88)
  mskTrk0 = np.logical_and( np.logical_and(36. <= lat, lat <= 39.13), lon >= 26.17)
  mskTrk1 = np.logical_and( np.logical_and(39.13 <= lat, lat <= 42.57), lon >= 31)
 #mskNAfrica = np.logical_and( np.logical_and(-1 <= lon, lon <= 11.55), lat <= 36.66)
  mskNAfrica = np.logical_and( np.logical_and(-1 <= lon, lon <= 11.55), lat <= 37.4)
  ratio[mskEast] = np.nan
  ratio[mskTrk0] = np.nan
  ratio[mskTrk1] = np.nan
  ratio[mskNAfrica] = np.nan
  ratio[lat <= 35.9] = np.nan

  rtnn = np.logical_not(np.isnan(ratio))
  rtplt = ratio[rtnn]
  rtplt[rtplt > 1] = 1
  
  sct = plt.scatter(lon[rtnn], lat[rtnn], .07, c=rtplt, cmap='binary')
  return sct


def createPlot():
  outPng = 'climateUncertainty.png'

  f = plt.figure(figsize=(19,9))
  gs = gridspec.GridSpec(2, 4, width_ratios=[1,1,1,.05])

  txtx, txty = -21, 68

  axRcp45_2025 = plt.subplot(gs[0,0], projection=ccrs.PlateCarree())
  plotRatio('rcp45', 2025, axRcp45_2025)
  plt.text(txtx, txty, 'RCP4.5, 2025', fontsize=14)

  axRcp45_2055 = plt.subplot(gs[0,1], projection=ccrs.PlateCarree())
  plotRatio('rcp45', 2055, axRcp45_2055)
  plt.text(txtx, txty, 'RCP4.5, 2055', fontsize=14)

  axRcp45_2085 = plt.subplot(gs[0,2], projection=ccrs.PlateCarree())
  plotRatio('rcp45', 2085, axRcp45_2085)
  plt.text(txtx, txty, 'RCP4.5, 2085', fontsize=14)

  axRcp85_2025 = plt.subplot(gs[1,0], projection=ccrs.PlateCarree())
  plotRatio('rcp85', 2025, axRcp85_2025)
  plt.text(txtx, txty, 'RCP8.5, 2025', fontsize=14)

  axRcp85_2055 = plt.subplot(gs[1,1], projection=ccrs.PlateCarree())
  plotRatio('rcp85', 2055, axRcp85_2055)
  plt.text(txtx, txty, 'RCP8.5, 2055', fontsize=14)

  axRcp85_2085 = plt.subplot(gs[1,2], projection=ccrs.PlateCarree())
  sct = plotRatio('rcp85', 2085, axRcp85_2085)
  plt.text(txtx, txty, 'RCP8.5, 2085', fontsize=14)

  axcb = plt.subplot(gs[:,3])
  cb = plt.colorbar(sct, ax=axRcp85_2085, cax=axcb)
  cb.set_label('IQR / Median', fontsize=15)

  axRcp45_2025.set_aspect('auto')
  axRcp45_2055.set_aspect('auto')
  axRcp45_2085.set_aspect('auto')
  axRcp85_2025.set_aspect('auto')
  axRcp85_2055.set_aspect('auto')
  axRcp85_2085.set_aspect('auto')
  axcb.set_aspect('auto')

  plt.tight_layout()

  f.savefig(outPng, dpi=300)

  


