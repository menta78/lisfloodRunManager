# -*- coding: utf-8 -*-
import os
import numpy as np
import netCDF4
import matplotlib
from matplotlib import pyplot as plt
from matplotlib import gridspec
from mpl_toolkits import basemap as bm

from getWarmingLevels import getWarmingLevels

lonlatNcMapFile = 'lonlat.nc'



def plotSingleModel(ax, ncfile, modelName, baselineYear=1995, projYear=2085, retPer=100, mp=None, **kwargs):

  dslonlat = netCDF4.Dataset(lonlatNcMapFile)
  lon = dslonlat.variables['lon'][:].transpose()
  lat = dslonlat.variables['lat'][:].transpose()
  dslonlat.close()

  ds = netCDF4.Dataset(ncfile)

  rtprs = ds.variables['return_period'][:]
  rpIndx = np.where(rtprs == retPer)[0]

  yrs = ds.variables['year'][:]
  bslnIndx = np.where(yrs == baselineYear)[0]
  projIndx = np.where(yrs == projYear)[0]
  
  bsln = ds.variables['rl'][rpIndx, bslnIndx, :, :].squeeze()
  proj = ds.variables['rl'][rpIndx, projIndx, :, :].squeeze()

  ds.close()

  projVar = (proj - bsln)/bsln*100
  if not ax is None:
    pcl, mp = plotSingleModelVar(ax, modelName, lon, lat, projVar, mp=mp, **kwargs)
  else:
    pcl, mp = None, None
  return lon, lat, bsln, proj, pcl, mp
  

def testPlotSingleModel():
  ncfile = '/ClimateRun4/multi-hazard/eva/projection_dis_rcp45_SMHI-RCA4_BC_ICHEC-EC-EARTH_wuChang_statistics.nc'
  modelName = 'SMHI-RCA4_BC_ICHEC-EC-EARTH'
  plotSingleModel(ncfile, modelName)



def plotSingleModelVar(ax, modelName, lon, lat, projVar, mp=None, bold=False, titleFontSize=6):
  if mp == None:
    llcrnrlon = -11.5
    llcrnrlat = 23
    urcrnrlon = 44
    urcrnrlat = 74
    mp = bm.Basemap(llcrnrlon=llcrnrlon, llcrnrlat=llcrnrlat, urcrnrlon=urcrnrlon, 
             urcrnrlat=urcrnrlat, resolution='l')
  plt.axes(ax)
  mp.drawcoastlines(linewidth=.25)
 #mp.fillcontinents(color=[.8, .8, .8], lake_color=[.7, .95, .7])
  pcl = mp.pcolor(lon, lat, projVar, cmap='bwr_r')
  plt.clim(-70, 70)
  txtpos = mp(17, 25)
  weight = 'bold' if bold else 'normal'
  plt.annotate(modelName, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', 
               horizontalalignment='center', fontsize=titleFontSize, weight=weight)
  return pcl, mp



def plotAllModels(scenario, rootDir='/ClimateRun4/multi-hazard/eva/'):
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

  outputPngFile = '100yrlChange_' + scenario + '.png'

  nrow = 4
  ncol = 3
  fig = plt.figure(figsize=(8, 9))
  gs = gridspec.GridSpec(nrow, ncol + 1, width_ratios=[1,1,1,.1])
  lon, lat = [], []
  bslnlist, projlist = [], []
  mp = None
  for mdl, imdl in zip(models, range(1, len(models) + 1)):
    irow = imdl // ncol
    icol = imdl % ncol
    print('plotting model ' + mdl + ' at ' + str(irow) + ', ' + str(icol))
    ax = plt.subplot(gs[irow, icol])
    
    ncFlNm = '_'.join(['projection_dis', scenario, mdl, 'wuChang', 'statistics.nc'])
    ncFlPth = os.path.join(rootDir, ncFlNm)
    mdlname = mdl.replace('BC_', '').replace('_BC', '')
    lon, lat, bsln, proj, pcl, mp = plotSingleModel(ax, ncFlPth, mdlname, mp=mp)
    bslnlist.append(bsln)
    projlist.append(proj)

  ax = plt.subplot(gs[0, 0])
  bsln = np.nanmean(np.array(bslnlist), 0)
  proj = np.nanmean(np.array(projlist), 0)
  projVar = (proj - bsln)/bsln*100
  plotSingleModelVar(ax, 'Ensemble ' + scenario, lon, lat, projVar, mp, bold=True)

  ax = plt.subplot(gs[:, 3])
 #ax.get_xaxis().set_visible(False)
 #ax.get_yaxis().set_visible(False)
  cb = plt.colorbar(pcl, cax=ax)
  cb.set_label(label='100-year event change (%)', fontsize=12)
  plt.tight_layout()

  fig.savefig(outputPngFile, dpi=300)




def plotEnsembles(rootDir='/ClimateRun4/multi-hazard/eva/'):
  scenarios = ['rcp85', 'rcp45']
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

  outputPngFile = '100yrlChange_ensembles.png'

  nrow = 4
  ncol = 3
  fig = plt.figure(figsize=(10, 4))
  gs = gridspec.GridSpec(1, 3, width_ratios=[1,1,.1])
  lon, lat = [], []
  bslnlist, projlist = [], []
  mp = None
  for scenario, iscen in zip(scenarios, range(len(scenarios))):
    for mdl, imdl in zip(models, range(1, len(models) + 1)):
      print('getting model ' + mdl)
      
      ncFlNm = '_'.join(['projection_dis', scenario, mdl, 'wuChang', 'statistics.nc'])
      ncFlPth = os.path.join(rootDir, ncFlNm)
      mdlname = mdl.replace('BC_', '').replace('_BC', '')
      lon, lat, bsln, proj, pcl, mp = plotSingleModel(None, ncFlPth, mdlname, mp=mp)
      bslnlist.append(bsln)
      projlist.append(proj)

    ax = plt.subplot(gs[iscen])
    bsln = np.nanmean(np.array(bslnlist), 0)
    proj = np.nanmean(np.array(projlist), 0)
    projVar = (proj - bsln)/bsln*100
    plotSingleModelVar(ax, 'Ensemble ' + scenario, lon, lat, projVar, mp, bold=True, titleFontSize=10)

  ax = plt.subplot(gs[2])
 #ax.get_xaxis().set_visible(False)
 #ax.get_yaxis().set_visible(False)
  cb = plt.colorbar(pcl, cax=ax)
  cb.set_label(label='100-year event change (%)', fontsize=12)
  plt.tight_layout()

  fig.savefig(outputPngFile, dpi=300)

  


def plotAllModelsWarmingLevel(scenario, warmingLev, rootDir='/ClimateRun4/multi-hazard/eva/'):
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

  wlYear = getWarmingLevels(scenario, warmingLev)

  outputPngFile = '100yrlChange_' + scenario + '_wl' + str(warmingLev) + '.png'

  nrow = 4
  ncol = 3
  fig = plt.figure(figsize=(8, 9))
  gs = gridspec.GridSpec(nrow, ncol + 1, width_ratios=[1,1,1,.1])
  lon, lat = [], []
  bslnlist, projlist = [], []
  mp = None
  for mdl, imdl in zip(models, range(1, len(models) + 1)):
    irow = imdl // ncol
    icol = imdl % ncol
    print('plotting model ' + mdl + ' at ' + str(irow) + ', ' + str(icol))
    ax = plt.subplot(gs[irow, icol])
    
    wrmYear = wlYear[mdl]
    wrmYear = int(round(wrmYear/5.)*5.)

    ncFlNm = '_'.join(['projection_dis', scenario, mdl, 'wuChang', 'statistics.nc'])
    ncFlPth = os.path.join(rootDir, ncFlNm)
    mdlname = mdl.replace('BC_', '').replace('_BC', '')
    lon, lat, bsln, proj, pcl, mp = plotSingleModel(ax, ncFlPth, mdlname, mp=mp, projYear=wrmYear)
    bslnlist.append(bsln)
    projlist.append(proj)

  ax = plt.subplot(gs[0, 0])
  bsln = np.nanmean(np.array(bslnlist), 0)
  proj = np.nanmean(np.array(projlist), 0)
  projVar = (proj - bsln)/bsln*100
  plotSingleModelVar(ax, 'Ensemble ' + scenario + ', warming lev. ' + str(warmingLev) + '$^\circ$', lon, lat, projVar, mp, bold=True)

  ax = plt.subplot(gs[:, 3])
 #ax.get_xaxis().set_visible(False)
 #ax.get_yaxis().set_visible(False)
  cb = plt.colorbar(pcl, cax=ax)
  cb.set_label(label='100-year event change (%)', fontsize=12)
  plt.tight_layout()

  fig.savefig(outputPngFile, dpi=300)


