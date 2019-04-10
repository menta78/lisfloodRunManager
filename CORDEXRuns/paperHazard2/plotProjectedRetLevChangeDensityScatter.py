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
from loadOutletRetLevFromNc import loadAllRetLevFromNc



def plotSingleModel(ax, relChngR8, relChngR4, modelName, plotRegression=False, showLegend=False, densityBins=70, lim=None, **kwargs):
  cnd = np.logical_and(
           np.logical_and(
              np.logical_and(~np.isnan(relChngR8), ~np.isnan(relChngR4)),
              np.logical_and(relChngR8 != np.inf, relChngR4 != np.inf)
           ),
           np.logical_and(relChngR8 != -np.inf, relChngR4 != -np.inf)
        )
  rc8 = relChngR8[cnd]*100
  rc4 = relChngR4[cnd]*100
 #xy = np.vstack([rc8, rc4])
 #z = gaussian_kde(xy)(xy)
 #ax.scatter(rc4, rc8, 1, c=z)
  if lim is None:
    limPercentiles = [3, 97]
    xlm = [np.percentile(rc4, limPercentiles[0]), np.percentile(rc4, limPercentiles[1])]
    ylm = [np.percentile(rc8, limPercentiles[0]), np.percentile(rc8, limPercentiles[1])]
    lim = [min(xlm[0], ylm[0]), max(xlm[1], ylm[1])]
  dp = ax.hist2d(rc4, rc8, bins=densityBins, range=[lim, lim], cmap='Purples')
  plt.xlim(lim)
  plt.ylim(lim)
  plt.grid('on')

  ax.plot(lim, lim, 'k', label='1-1 fit')
  if plotRegression:
    pc = np.polyfit(rc4, rc8, 1)
    fitLn0 = pc[0]*lim[0] + pc[1]
    fitLn1 = pc[0]*lim[1] + pc[1]
    ax.plot(lim, [fitLn0, fitLn1], 'r')

 #ax.yaxis.tick_right()
  tickFontSize = kwargs['tickFontSize'] if 'tickFontSize' in kwargs else 7
  ax.tick_params(axis='x', direction='in', pad=2, labelsize=tickFontSize)
  ax.tick_params(axis='y', direction='in', pad=0, labelsize=tickFontSize, rotation=90)

  labelFontSize = kwargs['labelFontSize'] if 'labelFontSize' in kwargs else 9
  xLabelPad = kwargs['xLabelPad'] if 'xLabelPad' in kwargs else -20
  yLabelPad = kwargs['yLabelPad'] if 'yLabelPad' in kwargs else -8
 #ax.xaxis.set_label_position('top')
  plt.xlabel('rcp45 ($\Delta$ %)', labelpad=xLabelPad, fontsize=labelFontSize)
 #ax.yaxis.set_label_position('right')
  plt.ylabel('rcp85 ($\Delta$ %)', labelpad=yLabelPad, fontsize=labelFontSize, rotation=-90)

  mdltxt = modelName
  mdltxt = mdltxt.replace('_BC_', '\n', 1)
  mdltxt = mdltxt.replace('_BC', '', 1)
  txtx = (max(lim) - min(lim))/2. + min(lim)
  txty = (max(lim) - min(lim))/1.2 + min(lim)
  bold = kwargs['bold'] if 'bold' in kwargs else False
  weight = 'bold' if bold else 'normal'
  titleFontSize = kwargs['titleFontSize'] if 'titleFontSize' in kwargs else 8
  ax.text(txtx, txty, mdltxt, fontsize=titleFontSize, ha='center', va='center', weight=weight)

  xlim = plt.xlim()
  ylim = plt.ylim()

  prcn = np.linspace(.5,99.5)
  nnchng = relChngR8[np.logical_not(np.isnan(relChngR8))]*100
  prcntl8 = np.percentile(nnchng, prcn)
  nnchng = relChngR4[np.logical_not(np.isnan(relChngR4))]*100
  prcntl4 = np.percentile(nnchng, prcn)
  prcntPlt = plt.plot(prcntl4, prcntl8, 'red', linewidth=2, label='p-p line')
  

  nnchng = relChngR8[np.logical_not(np.isnan(relChngR8))]*100
  r8median = np.percentile(nnchng, 50)
  r8p01 = np.percentile(nnchng, 1)
  r8p99 = np.percentile(nnchng, 99)
  r8p05 = np.percentile(nnchng, 5)
  r8p95 = np.percentile(nnchng, 95)
# mdnplt, = plt.plot(xlim, [r8median, r8median], 'firebrick', linewidth=.8, label='Median')
# p05plt, = plt.plot(xlim, [r8p05, r8p05], 'forestgreen', linewidth=.8, label='$5^{th}$ prcnt.')
# p95plt, = plt.plot(xlim, [r8p95, r8p95], 'fuchsia', linewidth=.8, label='$95^{th}$ prcnt.')
  print('rcp85, 1st perc: ' + str(r8p01))
  print('rcp85, 5th perc: ' + str(r8p05))
  print('rcp85, median: ' + str(r8median))
  print('rcp85, 95th perc: ' + str(r8p95))
  print('rcp85, 99th perc: ' + str(r8p99))

  nnchng = relChngR4[np.logical_not(np.isnan(relChngR4))]*100
  r4median = np.percentile(nnchng, 50)
  r4p01 = np.percentile(nnchng, 1)
  r4p99 = np.percentile(nnchng, 99)
  r4p05 = np.percentile(nnchng, 5)
  r4p95 = np.percentile(nnchng, 95)
# plt.plot([r4median, r4median], ylim, 'firebrick', linewidth=.8)
# plt.plot([r4p05, r4p05], ylim, 'forestgreen', linewidth=.8)
# plt.plot([r4p95, r4p95], ylim, 'fuchsia', linewidth=.8)
  print('rcp45, 1st perc: ' + str(r4p01))
  print('rcp45, 5th perc: ' + str(r4p05))
  print('rcp45, median: ' + str(r4median))
  print('rcp45, 95th perc: ' + str(r4p95))
  print('rcp45, 99th perc: ' + str(r4p99))

  if showLegend:
    ax.legend(loc='lower right', fontsize=12)

  return dp
  


def getRelChngs(ncEvaFlPth, retPer, projYear, bslnYear=1995, ncvar='rl', vlsMask=None, minThreshold=1):
  year, timeSeries = loadAllRetLevFromNc(ncEvaFlPth, retPer, ncvar=ncvar)
  bslnYrIndx = np.where(year == bslnYear)
  bsln = np.squeeze(timeSeries[bslnYrIndx, :, :])
  projYrIndx = np.where(year == projYear)
  proj = np.squeeze(timeSeries[projYrIndx, :, :])
  relChngMtx = (proj - bsln)/bsln
  vlsMask = np.logical_and(~np.isnan(bsln), bsln >= minThreshold) if vlsMask is None else vlsMask
  relChng = relChngMtx[vlsMask]
  return relChng, vlsMask


def plotAllModelsWarmingLevel(warmingLev, rootDir='/ClimateRun4/multi-hazard/eva/'):
  rcp8, rcp4 = 'rcp85', 'rcp45'
  retPer = 100

  models = """
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
  models = models.split()

  wlYearR8 = getWarmingLevels(rcp8, warmingLev)
  wlYearR4 = getWarmingLevels(rcp4, warmingLev)

  outputPngFile = 'scatter_100yrlChange_wl' + str(warmingLev) + '.png'

  nrow = 4
  ncol = 3
  fig = plt.figure(figsize=(8, 9.5))
  gs = gridspec.GridSpec(nrow, ncol)
  lon, lat = [], []
  relChng8lst, relChng4lst = [], []
  mp = None
  vlsMask = None
  for mdl, imdl in zip(models, range(1, len(models) + 1)):
    irow = imdl // ncol
    icol = imdl % ncol
    print('plotting model ' + mdl + ' at ' + str(irow) + ', ' + str(icol))
    ax = plt.subplot(gs[irow, icol])
    
    ncFlNm = '_'.join(['projection_dis', rcp8, mdl, 'wuChang', 'statistics.nc'])
    ncFlPth = os.path.join(rootDir, ncFlNm)
    wrmYear = wlYearR8[mdl]
    wrmYear = int(round(wrmYear/5.)*5.)
    relChngR8, vlsMask = getRelChngs(ncFlPth, retPer, wrmYear, vlsMask)

    ncFlNm = '_'.join(['projection_dis', rcp4, mdl, 'wuChang', 'statistics.nc'])
    ncFlPth = os.path.join(rootDir, ncFlNm)
    wrmYear = wlYearR4[mdl]
    wrmYear = int(round(wrmYear/5.)*5.)
    relChngR4, vlsMask = getRelChngs(ncFlPth, retPer, wrmYear, vlsMask)

    plotSingleModel(ax, relChngR8, relChngR4, mdl)
    relChng8lst.append(relChngR8)
    relChng4lst.append(relChngR4)

  ax = plt.subplot(gs[0, 0])
  relChng8 = np.nanmean(np.array(relChng8lst), 0)
  relChng4 = np.nanmean(np.array(relChng4lst), 0)
  plotSingleModel(ax, relChng8, relChng4, str(retPer) + '-year ret. lev.\nensemble rcp85 vs rcp45,\nwrm. lev. ' + str(warmingLev) + '$^\circ$', bold=True, plotRegression=True)
  plt.tight_layout()

  fig.savefig(outputPngFile, dpi=300)


def plotEnsembles_max(rootDir='/ClimateRun4/multi-hazard/eva/', retPer=100, gs=None):
  warmingLevs = [1.5, 2.0]
  rcp8, rcp4 = 'rcp85', 'rcp45'

  models = """
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
  models = models.split()
 #models = [models[0], models[1]]

  outputPngFile = 'scatter_100yrlChange_wls_ensemble_retPer' + str(retPer) + '.png'

  if gs is None:
    fig = plt.figure(figsize=(11, 5))
    gs = gridspec.GridSpec(1, 3, width_ratios=[1,1,.04])
    ownsFig = True
  else:
    ownsFig = False
  lon, lat = [], []
  axs = []
  lgndShown = False
  vlsMask = None
  for warmingLev, iwl in zip(warmingLevs, range(len(warmingLevs))):

    wlYearR8 = getWarmingLevels(rcp8, warmingLev)
    wlYearR4 = getWarmingLevels(rcp4, warmingLev)
    relChng8lst, relChng4lst = [], []

    for mdl, imdl in zip(models, range(1, len(models) + 1)):
      print('getting model ' + mdl)
      
      ncFlNm = '_'.join(['projection_dis', rcp8, mdl, 'wuChang', 'statistics.nc'])
      ncFlPth = os.path.join(rootDir, ncFlNm)
      wrmYear = wlYearR8[mdl]
      wrmYear = int(round(wrmYear/5.)*5.)
      relChngR8, vlsMask = getRelChngs(ncFlPth, retPer, wrmYear, vlsMask=vlsMask)
  
      ncFlNm = '_'.join(['projection_dis', rcp4, mdl, 'wuChang', 'statistics.nc'])
      ncFlPth = os.path.join(rootDir, ncFlNm)
      wrmYear = wlYearR4[mdl]
      wrmYear = int(round(wrmYear/5.)*5.)
      relChngR4, vlsMask = getRelChngs(ncFlPth, retPer, wrmYear, vlsMask=vlsMask)
  
      relChng8lst.append(relChngR8)
      relChng4lst.append(relChngR4)

    ax = plt.subplot(gs[iwl])
    relChng8 = np.nanmean(np.array(relChng8lst), 0)
    relChng4 = np.nanmean(np.array(relChng4lst), 0)
    showLegend = not lgndShown
    dp = plotSingleModel(ax, relChng8, relChng4, 
             str(retPer) + '-year ret. lev.\nextreme high discharge\nwrm. lev. ' + str(warmingLev) + '$^\circ$', 
             bold=True, plotRegression=False, tickFontSize=13, labelFontSize=15, titleFontSize=14,
             xLabelPad=-30, yLabelPad=-15, showLegend=showLegend)
    lgndShown = True
    axs.append(ax)

  cax = plt.subplot(gs[2])
  cb = plt.colorbar(dp[-1], ax=ax, cax=cax)
  cax.tick_params(labelsize=13, rotation=90)
  cb.set_label('density (pixel count)', fontsize=13)
  [ax.set_aspect('auto') for ax in axs]
  cax.set_aspect('auto')

  plt.tight_layout()

  if ownsFig:
    fig.savefig(outputPngFile, dpi=300)



def plotEnsembles_min(rootDir='/ClimateRun4/multi-hazard/eva/', retPer=100, gs=None, showLegend=True):
  warmingLevs = [1.5, 2.0]
  rcp8, rcp4 = 'rcp85', 'rcp45'

  models = """
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
  models = models.split()
 #models = [models[0], models[1]]

  outputPngFile = 'scatter_100yrlChange_min_wls_ensemble_retPer' + str(retPer) + '.png'

  if gs is None:
    fig = plt.figure(figsize=(11, 5))
    gs = gridspec.GridSpec(1, 3, width_ratios=[1,1,.04])
    ownsFig = True
  else:
    ownsFig = False
  lon, lat = [], []
  axs = []
  lgndShown = not showLegend
  lims = {1.5: [-20, 50], 2.0: [-40, 80]}
  lims = {1.5: [-24, 60], 2.0: [-39, 80]}
  densityBins = {1.5: 130, 2.0: 130}
  for warmingLev, iwl in zip(warmingLevs, range(len(warmingLevs))):

    wlYearR8 = getWarmingLevels(rcp8, warmingLev)
    wlYearR4 = getWarmingLevels(rcp4, warmingLev)
    relChng8lst, relChng4lst = [], []

    vlsMask = None
    for mdl, imdl in zip(models, range(1, len(models) + 1)):
      print('getting model ' + mdl)
      
      ncFlNm = '_'.join(['projection_dis', rcp8, mdl, 'wuChang', 'statistics.nc'])
      ncFlPth = os.path.join(rootDir, ncFlNm)
      wrmYear = wlYearR8[mdl]
      wrmYear = int(round(wrmYear/5.)*5.)
      relChngR8, vlsMask = getRelChngs(ncFlPth, retPer, wrmYear, ncvar='rl_min', vlsMask=vlsMask)
  
      ncFlNm = '_'.join(['projection_dis', rcp4, mdl, 'wuChang', 'statistics.nc'])
      ncFlPth = os.path.join(rootDir, ncFlNm)
      wrmYear = wlYearR4[mdl]
      wrmYear = int(round(wrmYear/5.)*5.)
      relChngR4, vlsMask = getRelChngs(ncFlPth, retPer, wrmYear, ncvar='rl_min', vlsMask=vlsMask)
  
      relChng8lst.append(relChngR8)
      relChng4lst.append(relChngR4)

    ax = plt.subplot(gs[iwl])
    relChng8 = np.nanmean(np.array(relChng8lst), 0)
    relChng4 = np.nanmean(np.array(relChng4lst), 0)
    showLegend = not lgndShown
    dp = plotSingleModel(ax, relChng8, relChng4, 
             str(retPer) + '-year ret. lev.\nextreme low discharge\nwrm. lev. ' + str(warmingLev) + '$^\circ$', 
             bold=True, plotRegression=False, tickFontSize=13, labelFontSize=15, titleFontSize=14,
             xLabelPad=-30, yLabelPad=-15, showLegend=showLegend, lim=lims[warmingLev])
    plt.xlim(lims[warmingLev])
    plt.ylim(lims[warmingLev])
    lgndShown = True
    axs.append(ax)

  cax = plt.subplot(gs[2])
  cb = plt.colorbar(dp[-1], ax=ax, cax=cax)
  cax.tick_params(labelsize=13, rotation=90)
  cb.set_label('density (pixel count)', fontsize=13)
  [ax.set_aspect('auto') for ax in axs]
  cax.set_aspect('auto')

  plt.tight_layout()

  if ownsFig:
    fig.savefig(outputPngFile, dpi=300)


def plotEnsembles(rootDir='/ClimateRun4/multi-hazard/eva/'):
  outputPngFile = 'scatter_100yrlChange_max_min_dis_ensemble.png'

  fig = plt.figure(figsize=(11, 10))
  gs = gridspec.GridSpec(2, 3, width_ratios=[1,1,.04])
  gsMx = [gs[0,0], gs[0,1], gs[0,2]]
  plotEnsembles_max(rootDir=rootDir, gs=gsMx)
  gsMn = [gs[1,0], gs[1,1], gs[1,2]]
  plotEnsembles_min(rootDir=rootDir, gs=gsMn, showLegend=False)

  plt.tight_layout()
  fig.savefig(outputPngFile, dpi=300)


if __name__ == '__main__':
 #plotEnsembles()
 #plotEnsembles(rootDir='/ClimateRun/menta/eva_50y_timeWindow/')
 #plotEnsembles_min(rootDir='/ClimateRun4/multi-hazard/eva/')
 #plotEnsembles_max(rootDir='/ClimateRun4/multi-hazard/eva/')
  plotEnsembles()
  plt.show()

