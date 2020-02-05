# -*- coding: utf-8 -*-
import os
import numpy as np
import netCDF4
import matplotlib
from matplotlib import pyplot as plt
from matplotlib import gridspec
from mpl_toolkits import basemap as bm
from scipy.stats import gaussian_kde

from getWarmingLevels import getWarmingLevels
from loadOutletRetLevFromNc import loadAllRetLevFromNc, loadYearlyMeanFromNc

#wuStr = 'wuChang'
wuStr = 'wuConst'
nTestModels = -1

modelStr = """
IPSL-INERIS-WRF331F_BC
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


def getRelChngs(ncEvaFlPth, retPer, projYear, bslnYear=1995, ncvar='rl', vlsMask=None, minThreshold=1):
  if ncvar == 'year_mean':
    year, timeSeries = loadYearlyMeanFromNc(ncEvaFlPth)
    bslnYrIndx = np.where(year == bslnYear)[0][0]
    projYrIndx = np.where(year == projYear)[0][0]
    wnSz = 15
    minIndx = np.max([bslnYrIndx - wnSz, 0])
    maxIndx = np.min([bslnYrIndx + wnSz, len(year)])
    bsln = np.nanmean(timeSeries[minIndx:maxIndx, :, :], 0)
    minIndx = np.max([projYrIndx - wnSz, 0])
    maxIndx = np.min([projYrIndx + wnSz, len(year)])
    proj = np.nanmean(timeSeries[minIndx:maxIndx, :, :], 0)
  else:
    year, timeSeries = loadAllRetLevFromNc(ncEvaFlPth, retPer, ncvar=ncvar)
    bslnYrIndx = np.where(year == bslnYear)
    projYrIndx = np.where(year == projYear)
    bsln = np.squeeze(timeSeries[bslnYrIndx, :, :])
    proj = np.squeeze(timeSeries[projYrIndx, :, :])
  relChngMtx = (proj - bsln)/bsln
  vlsMask = np.logical_and(~np.isnan(bsln), bsln >= minThreshold) if vlsMask is None else vlsMask
  relChng = relChngMtx[vlsMask]
  return relChng, vlsMask




def plotEnsembles_max(rootDir='/ClimateRun4/multi-hazard/eva/', retPer=100, ax=None):
  import pdb; pdb.set_trace()
  warmingLev = 2.0
  rcp8, rcp4 = 'rcp85', 'rcp45'

  models = modelStr.split()
 #models = [models[0], models[1]]

  if nTestModels != -1:
    models = models[:nTestModels]

  outputPngFile = 'chngByModelScen' + str(retPer) + '.png'

  if ax is None:
    fig = plt.figure(figsize=(10, 8))
    ax = fig.gca()
    ownsFig = True
  else:
    ownsFig = False
  lgndShown = False
  vlsMask = None

  wlYearR8 = getWarmingLevels(rcp8, warmingLev)
  wlYearR4 = getWarmingLevels(rcp4, warmingLev)

  mnChng = []
  yrs = []

  for mdl, imdl in zip(models, range(1, len(models) + 1)):
    print('getting model ' + mdl)
    
    ncFlNm = '_'.join(['projection_dis', rcp8, mdl, wuStr, 'statistics.nc'])
    ncFlPth = os.path.join(rootDir, ncFlNm)
    wrmYear = wlYearR8[mdl]
    wrmYear = int(round(wrmYear/5.)*5.)
    relChngR8, vlsMask = getRelChngs(ncFlPth, retPer, wrmYear, vlsMask=vlsMask)

    ncFlNm = '_'.join(['projection_dis', rcp4, mdl, wuStr, 'statistics.nc'])
    ncFlPth = os.path.join(rootDir, ncFlNm)
    wrmYear = wlYearR4[mdl]
    wrmYear = int(round(wrmYear/5.)*5.)
    relChngR4, vlsMask = getRelChngs(ncFlPth, retPer, wrmYear, vlsMask=vlsMask)

   #_chng = (np.nanmean(np.abs(relChngR8)), np.nanmean(np.abs(relChngR4)))
    _chng = (np.nanmedian(np.abs(relChngR8)), np.nanmedian(np.abs(relChngR4)))
    mnChng.append(_chng)
    _yrs = (wlYearR8[mdl], wlYearR4[mdl])
    yrs.append(_yrs)

  mnChng = np.array(mnChng)*100
  yrs = np.array(yrs)
  prop_cycle = plt.rcParams['axes.prop_cycle']
  colors = prop_cycle.by_key()['color']
  colors.insert(0, 'k')
  plts = [(plt.plot(yrs[imdl, 0], mnChng[imdl, 0], 'o', color=colors[imdl], markerfacecolor=colors[imdl], label=models[imdl]), plt.plot(yrs[imdl, 1], mnChng[imdl, 1], 'D', color=colors[imdl], markerfacecolor=colors[imdl]), plt.plot(yrs[imdl, :], mnChng[imdl, :], color=colors[imdl])) for imdl in range(len(models))]
  plt.grid('on')
  lgnd1 = plt.legend(loc=1)
  plt.gca().add_artist(lgnd1)
  lgnd2 = plt.legend([plts[0][0][0], plts[0][1][0]], ['RCP8.5', 'RCP4.5'], loc=4)

  plt.tight_layout()
  if ownsFig:
    fig.savefig(outputPngFile)
  



if __name__ == '__main__':
  plotEnsembles_max(rootDir='/ClimateRun4/multi-hazard/eva/')
  plt.show()

