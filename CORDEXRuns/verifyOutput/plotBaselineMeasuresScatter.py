import numpy as np
import os
from datetime import datetime
from matplotlib import pyplot as plt
import loadTssFile

defMsrsTssFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/testdata/disWin_measuresGauges.tss'


def getYMax(tms, dis, startDate, endDate):
  cnd = np.logical_and(tms >= startDate, tms <= endDate)
  tms = tms[cnd]
  dis = dis[cnd, :]
  estYrs = np.array([t.year for t in tms])
  yrs = np.unique(estYrs)
  ny = len(yrs)
  disMax = np.ones([ny, dis.shape[1]])*np.nan

  for iy in range(ny):
    y = yrs[iy]
    cndy = estYrs == y
    disy = dis[cndy, :]
    disMaxy = np.max(disy, 0)
    disMax[iy, :] = disMaxy
  return yrs, disMax


def getYMin(tms, dis, startDate, endDate):
  cnd = np.logical_and(tms >= startDate, tms <= endDate)
  tms = tms[cnd]
  dis = dis[cnd, :]
  estYrs = np.array([t.year for t in tms])
  yrs = np.unique(estYrs)
  ny = len(yrs)
  disMin = np.ones([ny, dis.shape[1]])*np.nan

  for iy in range(ny):
    y = yrs[iy]
    cndy = estYrs == y
    disy = dis[cndy, :]
    disMiny = np.min(disy, 0)
    disMin[iy, :] = disMiny
  return yrs, disMin


def getYMean(tms, dis, startDate, endDate):
  cnd = np.logical_and(tms >= startDate, tms <= endDate)
  tms = tms[cnd]
  dis = dis[cnd, :]
  estYrs = np.array([t.year for t in tms])
  yrs = np.unique(estYrs)
  ny = len(yrs)
  disMean = np.ones([ny, dis.shape[1]])*np.nan

  for iy in range(ny):
    y = yrs[iy]
    cndy = estYrs == y
    disy = dis[cndy, :]
    disMeany = np.mean(disy, 0)
    disMean[iy, :] = disMeany
  return yrs, disMean


def plotModelScatter(ax, modelName, modelTssPath, modelStartDate=datetime(1981,01,01), 
       msrsTssFl=defMsrsTssFile, msrsStartDate=datetime(1990, 01, 01), getStat=getYMax):
  if os.path.isfile(modelTssPath):
    tmsMdl, statIdsMdl, disMdl = loadTssFile.loadTssFile(modelTssPath, startDate=modelStartDate)
  else:
    tmsMdl, statIdsMdl, disMdl = loadTssFile.loadTssFromDir(modelTssPath, startDate=modelStartDate)
  tmsMsrs, statIdsMsrs, disMsrs = loadTssFile.loadTssFile(msrsTssFl, startDate=msrsStartDate)
  assert (statIdsMdl == statIdsMsrs).all()
  
  startDate = max(min(tmsMdl), min(tmsMsrs))
  endDate = min(max(tmsMdl), max(tmsMsrs))

  yrs, mdlStat = getStat(tmsMdl, disMdl, startDate, endDate)
  yrs, msrStat = getStat(tmsMsrs, disMsrs, startDate, endDate)

  mdlStat = np.sort(mdlStat, 0)
  msrStat = np.sort(msrStat, 0)

  mdlStatFlt = mdlStat.flatten()
  msrStatFlt = msrStat.flatten()
  cnd0 = msrStatFlt > .1
  mdlStatFlt = mdlStatFlt[cnd0]
  msrStatFlt = msrStatFlt[cnd0]
  
  ax.scatter(msrStatFlt, mdlStatFlt, 10)
  ax.set_aspect('equal')
  ax.grid('on')
  
  xlim = ax.get_xlim()
  ylim = ax.get_ylim()

  lm = [min(min(xlim), min(ylim)), max(max(xlim), max(ylim))]
  ax.set_xlim(lm)
  ax.set_ylim(lm)
  ax.plot(lm, lm, 'k')

  pc = np.polyfit(msrStatFlt, mdlStatFlt, 1)
  fitLn0 = pc[0]*lm[0] + pc[1]
  fitLn1 = pc[0]*lm[1] + pc[1]
  ax.plot(lm, [fitLn0, fitLn1], 'r')

 #emptyTicks = ['']*len(ax.get_xticklabels())
 #ax.set_xticklabels(emptyTicks)
 #emptyTicks = ['']*len(ax.get_yticklabels())
 #ax.set_yticklabels(emptyTicks)
  ax.set_xticks([])
  ax.set_yticks([])

  mdltxt = modelName
  mdltxt = mdltxt.replace('_BC_', '\n', 1)
  mdltxt = mdltxt.replace('_BC', '', 1)
  txtx = (max(lm) - min(lm))/2.
  txty = (max(lm) - min(lm))/1.2
  ax.text(txtx, txty, mdltxt, fontsize=9, ha='center', va='center')
  txty = (max(lm) - min(lm))/30.
  ax.text(txtx, txty, 'observ.', fontsize=12, ha='center', va='center')
  txtx = txty
  txty = (max(lm) - min(lm))/2.
  ax.text(txtx, txty, 'model', fontsize=12, ha='center', va='center', rotation=-90)
  pass




def plotAllMaxScatters():
  outputfig = 'allMdlScatterYrMx.png'
  models = """
IPSL-INERIS-WRF331F
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

  rootDir = '/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/ClimateRuns/LisfloodEuroCordex/historical/'

  f, axmtx = plt.subplots(3, 4, figsize=(12, 9))
  plt.tight_layout()

  axHind = axmtx[0, 0]
  hindTssFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/efasTss/disWin.tss'
  hindStartDate = datetime(1990, 1, 1, 0, 0)
  plotModelScatter(axHind, 'Hindcast', hindTssFile, modelStartDate=hindStartDate)

  axmtxflt = np.array(axmtx).flatten()[1:]
  for mdl, axmdl in zip(models, axmtxflt):
    mdlDir = os.path.join(rootDir, mdl, 'notWaterUse')
    plotModelScatter(axmdl, mdl, mdlDir)
    plt.tight_layout()
    pass

  plt.suptitle('Annual Maxima', y=.995, fontsize=13)
  f.savefig(outputfig, dpi=300)




def plotAllMinScatters():
  outputfig = 'allMdlScatterYrMin.png'
  models = """
IPSL-INERIS-WRF331F
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

  rootDir = '/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/ClimateRuns/LisfloodEuroCordex/historical/'

  f, axmtx = plt.subplots(3, 4, figsize=(12, 9))
  plt.tight_layout()

  axHind = axmtx[0, 0]
  hindTssFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/efasTss/disWin.tss'
  hindStartDate = datetime(1990, 1, 1, 0, 0)
  plotModelScatter(axHind, 'Hindcast', hindTssFile, modelStartDate=hindStartDate, getStat=getYMin)

  axmtxflt = np.array(axmtx).flatten()[1:]
  for mdl, axmdl in zip(models, axmtxflt):
    mdlDir = os.path.join(rootDir, mdl, 'notWaterUse')
    plotModelScatter(axmdl, mdl, mdlDir, getStat=getYMin)
    plt.tight_layout()
    pass

  plt.suptitle('Annual Minima', y=.995, fontsize=13)
  f.savefig(outputfig, dpi=300)




def plotAllMeanScatters():
  outputfig = 'allMdlScatterYrMean.png'
  models = """
IPSL-INERIS-WRF331F
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

  rootDir = '/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/ClimateRuns/LisfloodEuroCordex/historical/'

  f, axmtx = plt.subplots(3, 4, figsize=(12, 9))
  plt.tight_layout()

  axHind = axmtx[0, 0]
  hindTssFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/efasTss/disWin.tss'
  hindStartDate = datetime(1990, 1, 1, 0, 0)
  plotModelScatter(axHind, 'Hindcast', hindTssFile, modelStartDate=hindStartDate, getStat=getYMean)

  axmtxflt = np.array(axmtx).flatten()[1:]
  for mdl, axmdl in zip(models, axmtxflt):
    mdlDir = os.path.join(rootDir, mdl, 'notWaterUse')
    plotModelScatter(axmdl, mdl, mdlDir, getStat=getYMean)
    plt.tight_layout()
    pass

  plt.suptitle('Annual Means', y=.995, fontsize=13)
  f.savefig(outputfig, dpi=300)


    
    
  
def plotModelScatterEfas():
  outputfig = 'mdlScatterHindcast.png'
  modelTssFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/efasTss/disWin.tss'
  modelStartDate = datetime(1990, 1, 1, 0, 0)
  f = plt.figure(figsize=(3, 3))
  ax = f.gca()
  plotModelScatter(ax, 'Hindcast', modelTssFile, modelStartDate=modelStartDate)
  f.savefig(outputfig, dpi=300)
  


