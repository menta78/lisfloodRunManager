import netCDF4
import numpy as np
import os
from datetime import datetime
import loadTssFile
import loadOutletDischargeFromNc
from matplotlib import pyplot as plt
import plotBaselineMeasuresScatter


def printMsrMdlsMaxima():
  msrsTssFl = '/STORAGE/src1/git/lisfloodRunManager/verifyOutput/testdata/disWin_measuresGauges.tss'
  msrsStartDate = datetime(1990, 01, 01)
  tmsMsrs, statIdsMsrs, disMsrs = loadTssFile.loadTssFile(msrsTssFl, startDate=msrsStartDate)
  
  modelTssDir = '/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/ClimateRuns/LisfloodEuroCordex/historical/CLMcom-CCLM4-8-17_BC_CNRM-CERFACS-CNRM-CM5/wuConst'
  modelStartDate = datetime(1981, 1, 1, 0, 0)
  tmsMdl, statIdsMdl, disMdl = loadTssFile.loadTssFromDir(modelTssDir, startDate=modelStartDate)
  
  h01ncfile = '/H01_Fresh_Water/Europe/BernyRuns/RunsCCLUWDproj/CLMcom-CCLM4-8-17_BC/CNRM-CERFACS-CNRM-CM5/hist/Europe_all/dis.nc'
  ds = netCDF4.Dataset(h01ncfile)
  disMdlH01 = ds.variables['dis'][:]

  print('max measured discharge')
  print(np.max(disMsrs[:]))
  print('max discharge jeodpp model')
  print(np.max(disMdl[:]))
  print('max discharge h01 model')
  print(np.nanmax(disMdlH01[:]))



def plotScatterH01ModelsMax(avgYearsByYear=False):
  outputfig = 'allMdlScatterYrMxH0.png'
  ncOutletPth = '/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/lisflood/lisfloodRun/LisfloodEurope/maps_netcdf/outlets.nc'
  
  h0NcRootDir = '/H01_Fresh_Water/Europe/BernyRuns/RunsCCLUWDproj/'
  h0TssRootDir = './h01tss/'
  try:
    os.mkdir(h0TssRootDir)
  except:
    pass

  mdls = """
IPSL-INERIS-WRF331F_BC
SMHI-RCA4_BC/CNRM-CERFACS-CNRM-CM5
SMHI-RCA4_BC/ICHEC-EC-EARTH
SMHI-RCA4_BC/IPSL-IPSL-CM5A-MR
SMHI-RCA4_BC/MOHC-HadGEM2-ES
SMHI-RCA4_BC/MPI-M-MPI-ESM-LR
CLMcom-CCLM4-8-17_BC/CNRM-CERFACS-CNRM-CM5
CLMcom-CCLM4-8-17_BC/ICHEC-EC-EARTH
CLMcom-CCLM4-8-17_BC/MPI-M-MPI-ESM-LR
DMI-HIRHAM5-ICHEC-EC-EARTH_BC
KNMI-RACMO22E-ICHEC-EC-EARTH_BC
"""
  models = mdls.split()

  f, axmtx = plt.subplots(3, 4, figsize=(12, 9))
  plt.tight_layout()

  getStat = plotBaselineMeasuresScatter.getYMax if avgYearsByYear else plotBaselineMeasuresScatter.getYMaxMean

  axHind = axmtx[0, 0]
  hindTssFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/efasTss/disWin.tss'
  hindStartDate = datetime(1990, 1, 1, 0, 0)
  plotBaselineMeasuresScatter.plotModelScatterLog(axHind, 'Hindcast', hindTssFile, modelStartDate=hindStartDate, 
       getStat=getStat)

  axmtxflt = np.array(axmtx).flatten()[1:]
  axinvisible = []
  for mdl, axmdl in zip(models, axmtxflt):
    modelName = mdl.replace('/', '_')
    print('  elaborating model ' + modelName)
    tssFlPth = os.path.join(h0TssRootDir, 'disWin_' + modelName + '.tss')
    if not os.path.isfile(tssFlPth):
      print('    tss file not found, creating it (this can take a while): ' + tssFlPth)
      ncFlPth = os.path.join(h0NcRootDir, mdl, 'hist/Europe_all/dis.nc')
      if not os.path.isfile(ncFlPth):
        print('      Cannot find output nc either. Skipping model')
        axinvisible.append(axmdl)
        continue
      loadOutletDischargeFromNc.nc2tss(ncOutletPth, ncFlPth, tssFlPth)
    plotBaselineMeasuresScatter.plotModelScatterLog(axmdl, modelName, tssFlPth,
       getStat=getStat)
    plt.tight_layout()
    pass
  for ax in axinvisible:
    ax.set_visible(False)

  plt.suptitle('Annual Maxima (H0)', y=.995, fontsize=13)
  f.savefig(outputfig, dpi=300)

  



def plotScatterH01ModelsMin(avgYearsByYear=False):
  outputfig = 'allMdlScatterYrMinH0.png'
  ncOutletPth = '/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/lisflood/lisfloodRun/LisfloodEurope/maps_netcdf/outlets.nc'
  
  h0NcRootDir = '/H01_Fresh_Water/Europe/BernyRuns/RunsCCLUWDproj/'
  h0TssRootDir = './h01tss/'
  try:
    os.mkdir(h0TssRootDir)
  except:
    pass

  mdls = """
IPSL-INERIS-WRF331F_BC
SMHI-RCA4_BC/CNRM-CERFACS-CNRM-CM5
SMHI-RCA4_BC/ICHEC-EC-EARTH
SMHI-RCA4_BC/IPSL-IPSL-CM5A-MR
SMHI-RCA4_BC/MOHC-HadGEM2-ES
SMHI-RCA4_BC/MPI-M-MPI-ESM-LR
CLMcom-CCLM4-8-17_BC/CNRM-CERFACS-CNRM-CM5
CLMcom-CCLM4-8-17_BC/ICHEC-EC-EARTH
CLMcom-CCLM4-8-17_BC/MPI-M-MPI-ESM-LR
DMI-HIRHAM5-ICHEC-EC-EARTH_BC
KNMI-RACMO22E-ICHEC-EC-EARTH_BC
"""
  models = mdls.split()

  f, axmtx = plt.subplots(3, 4, figsize=(12, 9))
  plt.tight_layout()

  getStat = plotBaselineMeasuresScatter.getYMin if avgYearsByYear else plotBaselineMeasuresScatter.getYMinMean

  axHind = axmtx[0, 0]
  hindTssFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/efasTss/disWin.tss'
  hindStartDate = datetime(1990, 1, 1, 0, 0)
  plotBaselineMeasuresScatter.plotModelScatterLog(axHind, 'Hindcast', hindTssFile, modelStartDate=hindStartDate, 
       getStat=getStat)

  axmtxflt = np.array(axmtx).flatten()[1:]
  axinvisible = []
  for mdl, axmdl in zip(models, axmtxflt):
    modelName = mdl.replace('/', '_')
    print('  elaborating model ' + modelName)
    tssFlPth = os.path.join(h0TssRootDir, 'disWin_' + modelName + '.tss')
    if not os.path.isfile(tssFlPth):
      print('    tss file not found, creating it (this can take a while): ' + tssFlPth)
      ncFlPth = os.path.join(h0NcRootDir, mdl, 'hist/Europe_all/dis.nc')
      if not os.path.isfile(ncFlPth):
        print('      Cannot find output nc either. Skipping model')
        axinvisible.append(axmdl)
        continue
      loadOutletDischargeFromNc.nc2tss(ncOutletPth, ncFlPth, tssFlPth)
    plotBaselineMeasuresScatter.plotModelScatterLog(axmdl, modelName, tssFlPth,
       getStat=getStat)
    plt.tight_layout()
    pass
  for ax in axinvisible:
    ax.set_visible(False)

  plt.suptitle('Annual Minima (H0)', y=.995, fontsize=13)
  f.savefig(outputfig, dpi=300)



def plotScatterH01ModelsMean(avgYearsByYear=False):
  outputfig = 'allMdlScatterYrMeanH0.png'
  ncOutletPth = '/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/lisflood/lisfloodRun/LisfloodEurope/maps_netcdf/outlets.nc'
  
  h0NcRootDir = '/H01_Fresh_Water/Europe/BernyRuns/RunsCCLUWDproj/'
  h0TssRootDir = './h01tss/'
  try:
    os.mkdir(h0TssRootDir)
  except:
    pass

  mdls = """
IPSL-INERIS-WRF331F_BC
SMHI-RCA4_BC/CNRM-CERFACS-CNRM-CM5
SMHI-RCA4_BC/ICHEC-EC-EARTH
SMHI-RCA4_BC/IPSL-IPSL-CM5A-MR
SMHI-RCA4_BC/MOHC-HadGEM2-ES
SMHI-RCA4_BC/MPI-M-MPI-ESM-LR
CLMcom-CCLM4-8-17_BC/CNRM-CERFACS-CNRM-CM5
CLMcom-CCLM4-8-17_BC/ICHEC-EC-EARTH
CLMcom-CCLM4-8-17_BC/MPI-M-MPI-ESM-LR
DMI-HIRHAM5-ICHEC-EC-EARTH_BC
KNMI-RACMO22E-ICHEC-EC-EARTH_BC
"""
  models = mdls.split()

  f, axmtx = plt.subplots(3, 4, figsize=(12, 9))
  plt.tight_layout()

  getStat = plotBaselineMeasuresScatter.getYMean if avgYearsByYear else plotBaselineMeasuresScatter.getTotMean

  axHind = axmtx[0, 0]
  hindTssFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/efasTss/disWin.tss'
  hindStartDate = datetime(1990, 1, 1, 0, 0)
  plotBaselineMeasuresScatter.plotModelScatterLog(axHind, 'Hindcast', hindTssFile, modelStartDate=hindStartDate, 
       getStat=getStat)

  axmtxflt = np.array(axmtx).flatten()[1:]
  axinvisible = []
  for mdl, axmdl in zip(models, axmtxflt):
    modelName = mdl.replace('/', '_')
    print('  elaborating model ' + modelName)
    tssFlPth = os.path.join(h0TssRootDir, 'disWin_' + modelName + '.tss')
    if not os.path.isfile(tssFlPth):
      print('    tss file not found, creating it (this can take a while): ' + tssFlPth)
      ncFlPth = os.path.join(h0NcRootDir, mdl, 'hist/Europe_all/dis.nc')
      if not os.path.isfile(ncFlPth):
        print('      Cannot find output nc either. Skipping model')
        axinvisible.append(axmdl)
        continue
      loadOutletDischargeFromNc.nc2tss(ncOutletPth, ncFlPth, tssFlPth)
    plotBaselineMeasuresScatter.plotModelScatterLog(axmdl, modelName, tssFlPth,
       getStat=getStat)
    plt.tight_layout()
    pass
  for ax in axinvisible:
    ax.set_visible(False)

  plt.suptitle('Annual Means (H0)', y=.995, fontsize=13)
  f.savefig(outputfig, dpi=300)


