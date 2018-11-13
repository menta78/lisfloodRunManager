# -*- coding: utf-8 -*-
import os, pickle
import numpy as np
import netCDF4
import matplotlib
from matplotlib import pyplot as plt
from matplotlib import gridspec
from mpl_toolkits import basemap as bm
from datetime import datetime

from getWarmingLevels import getWarmingLevels
from loadTssFile import loadTssFromDir

from plotBaselineMeasuresScatter import getYMinMean



def plotSingleModel(ax, relChngR8, relChngR4, modelName, plotRegression=False, **kwargs):
  rc8 = relChngR8[np.logical_not(np.isnan(relChngR8))]*100
  rc4 = relChngR4[np.logical_not(np.isnan(relChngR4))]*100
  ax.scatter(rc4, rc8, 1)
  xlm = plt.xlim()
  ylm = plt.ylim()
  lim = [min(xlm[0], ylm[0]), max(xlm[1], ylm[1])]
  plt.xlim(lim)
  plt.ylim(lim)
  plt.grid('on')

  if plotRegression:
    ax.plot(lim, lim, 'k')
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
  


def plotSingleModelLog(ax, relChngR8, relChngR4, modelName, **kwargs):
  rc8 = relChngR8[np.logical_not(np.isnan(relChngR8))]*100
  rc4 = relChngR4[np.logical_not(np.isnan(relChngR4))]*100
  ax.scatter(rc4, rc8, 1)
  ax.set_aspect('equal')
  ax.set_xscale('log')
  ax.set_yscale('log')
  xlim = [1, max(rc8)*4]
  ylim = [1, max(rc8)*4]

  ax.set_xlim(xlim)
  ax.set_ylim(ylim)
  ax.plot(xlim, xlim, 'k')
  plt.grid('on')

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
  txtx = .5
  txty = 1./1.1
  bold = kwargs['bold'] if 'bold' in kwargs else False
  weight = 'bold' if bold else 'normal'
  titleFontSize = kwargs['titleFontSize'] if 'titleFontSize' in kwargs else 8
  ax.text(txtx, txty, mdltxt, fontsize=titleFontSize, ha='center', va='center', weight=weight, 
           transform=ax.transAxes)



def getRelChngs(cacheId, fldirHist, fldirRcp, projYear, windowYearHalfSize=14, bslnYear=1995,
      getStat=getYMinMean):

  cacheFl = os.path.join('cache', cacheId + '_hist.pkl')
  if (cacheId != '') and os.path.isfile(cacheFl):
    fl = open(cacheFl)
    tms, disHist = pickle.load(fl)
    fl.close()
  else:
    tms, _, disHist = loadTssFromDir(fldirHist)
    if cacheId != '':
      fl = open(cacheFl, 'w')
      pickle.dump([tms, disHist], fl)
      fl.close()
  strtDt = datetime(bslnYear-windowYearHalfSize, 1, 1)
  endDt = datetime(bslnYear+windowYearHalfSize+1, 1, 1)
  _, disHist = getStat(tms, disHist, strtDt, endDt)

  cacheFl = os.path.join('cache', cacheId + '_rcp.pkl')
  if os.path.isfile(cacheFl):
    fl = open(cacheFl)
    tms, disRcp = pickle.load(fl)
    fl.close()
  else:
    tms, _, disRcp = loadTssFromDir(fldirRcp)
    if cacheId != '':
      fl = open(cacheFl, 'w')
      pickle.dump([tms, disRcp], fl)
      fl.close()
  strtDt = datetime(projYear-windowYearHalfSize, 1, 1)
  endDt = datetime(projYear+windowYearHalfSize+1, 1, 1)
  _, disRcp = getStat(tms, disRcp, strtDt, endDt)
 
  return (disRcp - disHist)/disHist




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
  for mdl, imdl in zip(models, range(1, len(models) + 1)):
    irow = imdl // ncol
    icol = imdl % ncol
    print('plotting model ' + mdl + ' at ' + str(irow) + ', ' + str(icol))
    ax = plt.subplot(gs[irow, icol])
    
    ncFlNm = '_'.join(['projection_dis', rcp8, mdl, 'wuChang', 'statistics.nc'])
    ncFlPth = os.path.join(rootDir, ncFlNm)
    wrmYear = wlYearR8[mdl]
    wrmYear = int(round(wrmYear/5.)*5.)
    relChngR8 = getRelChngs(ncFlPth, retPer, wrmYear)

    ncFlNm = '_'.join(['projection_dis', rcp4, mdl, 'wuChang', 'statistics.nc'])
    ncFlPth = os.path.join(rootDir, ncFlNm)
    wrmYear = wlYearR4[mdl]
    wrmYear = int(round(wrmYear/5.)*5.)
    relChngR4 = getRelChngs(ncFlPth, retPer, wrmYear)

    plotSingleModel(ax, relChngR8, relChngR4, mdl)
    relChng8lst.append(relChngR8)
    relChng4lst.append(relChngR4)

  ax = plt.subplot(gs[0, 0])
  relChng8 = np.nanmean(np.array(relChng8lst), 0)
  relChng4 = np.nanmean(np.array(relChng4lst), 0)
  plotSingleModel(ax, relChng8, relChng4, 'Ensemble rcp85 vs rcp45,\nwrm. lev. ' + str(warmingLev) + '$^\circ$', bold=True, plotRegression=True)
  plt.tight_layout()

  fig.savefig(outputPngFile, dpi=300)


def plotEnsembles(rootDir='/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/ClimateRuns/LisfloodEuroCordex/', wuChangStr='wuChang'):
  warmingLevs = [1.5, 2.0]
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

  outputPngFile = 'scatter_minDis_' + wuChangStr + '_wls_ensemble.png'

  fig = plt.figure(figsize=(10, 5))
  gs = gridspec.GridSpec(1, 3, width_ratios=[1,1,.1])
  lon, lat = [], []
  relChng8lst, relChng4lst = [], []
  for warmingLev, iwl in zip(warmingLevs, range(len(warmingLevs))):

    wlYearR8 = getWarmingLevels(rcp8, warmingLev)
    wlYearR4 = getWarmingLevels(rcp4, warmingLev)

    for mdl, imdl in zip(models, range(1, len(models) + 1)):
      print('getting model ' + mdl)
      
      fldirHist = os.path.join(rootDir, 'historical', mdl, 'wuConst')
      fldirR8 = os.path.join(rootDir, rcp8, mdl, wuChangStr)
      wrmYear = wlYearR8[mdl]
      cacheId = '_'.join([mdl, rcp8, 'wuChang'])
      relChngR8 = getRelChngs(cacheId, fldirHist, fldirR8, wrmYear)
  
      fldirR4 = os.path.join(rootDir, rcp4, mdl, wuChangStr)
      wrmYear = wlYearR4[mdl]
      cacheId = '_'.join([mdl, rcp4, 'wuChang'])
      relChngR4 = getRelChngs(cacheId, fldirHist, fldirR4, wrmYear)
  
      relChng8lst.append(relChngR8)
      relChng4lst.append(relChngR4)

    ax = plt.subplot(gs[iwl])
    relChng8 = np.nanmean(np.array(relChng8lst), 0)
    relChng4 = np.nanmean(np.array(relChng4lst), 0)
    plotSingleModel(ax, relChng8, relChng4, 
             'Ensemble rcp85 vs rcp45, min. dis.\nwrm. lev. ' + str(warmingLev) + '$^\circ$', 
             bold=True, plotRegression=True, tickFontSize=10, labelFontSize=12, titleFontSize=13,
             xLabelPad=-25, yLabelPad=-10)

  plt.tight_layout()

  fig.savefig(outputPngFile, dpi=300)


def plotEnsemblesLog(rootDir='/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/ClimateRuns/LisfloodEuroCordex/', wuChangStr='wuChang'):
  warmingLevs = [1.5, 2.0]
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

  outputPngFile = 'scatter_minDis_' + wuChangStr + '_wls_ensemble.png'

  fig = plt.figure(figsize=(10, 5))
  gs = gridspec.GridSpec(1, 3, width_ratios=[1,1,.1])
  lon, lat = [], []
  relChng8lst, relChng4lst = [], []
  for warmingLev, iwl in zip(warmingLevs, range(len(warmingLevs))):

    wlYearR8 = getWarmingLevels(rcp8, warmingLev)
    wlYearR4 = getWarmingLevels(rcp4, warmingLev)

    for mdl, imdl in zip(models, range(1, len(models) + 1)):
      print('getting model ' + mdl)
      
      fldirHist = os.path.join(rootDir, 'historical', mdl, 'wuConst')
      fldirR8 = os.path.join(rootDir, rcp8, mdl, wuChangStr)
      wrmYear = wlYearR8[mdl]
      cacheId = '_'.join([mdl, rcp8, 'wuChang'])
      relChngR8 = getRelChngs(cacheId, fldirHist, fldirR8, wrmYear)
  
      fldirR4 = os.path.join(rootDir, rcp4, mdl, wuChangStr)
      wrmYear = wlYearR4[mdl]
      cacheId = '_'.join([mdl, rcp4, 'wuChang'])
      relChngR4 = getRelChngs(cacheId, fldirHist, fldirR4, wrmYear)
  
      relChng8lst.append(relChngR8)
      relChng4lst.append(relChngR4)

    ax = plt.subplot(gs[iwl])
    relChng8 = np.nanmean(np.array(relChng8lst), 0)
    relChng4 = np.nanmean(np.array(relChng4lst), 0)
    plotSingleModelLog(ax, relChng8, relChng4, 
             'Ensemble rcp85 vs rcp45,\n minimum discharge\nwrm. lev. ' + str(warmingLev) + '$^\circ$', 
             bold=True, plotRegression=True, tickFontSize=10, labelFontSize=12, titleFontSize=13,
             xLabelPad=-25, yLabelPad=-10)

  plt.tight_layout()

  fig.savefig(outputPngFile, dpi=300)




