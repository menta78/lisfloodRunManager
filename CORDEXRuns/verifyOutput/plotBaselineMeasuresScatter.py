import numpy as np
import os
from datetime import datetime
from matplotlib import pyplot as plt
import loadTssFile

#defMsrsTssFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/testdata/disWin_measuresGauges.tss'
defMsrsTssFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/validationData/Qts_Europe_measurements.csv'


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
    disMaxy = np.nanmax(disy, 0)
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
    disMiny = np.nanmin(disy, 0)
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
    disMeany = np.nanmean(disy, 0)
    disMean[iy, :] = disMeany
  return yrs, disMean


def getYMaxMean(tms, dis, startDate, endDate):
  yrs, disMax = getYMax(tms, dis, startDate, endDate)
  disMaxMean = np.nanmean(disMax, 0)
  return np.array([min(yrs)]), disMaxMean


def getYMinMean(tms, dis, startDate, endDate):
  yrs, disMin = getYMin(tms, dis, startDate, endDate)
  disMinMean = np.nanmean(disMin, 0)
  return np.array([min(yrs)]), disMinMean


def getTotMean(tms, dis, startDate, endDate):
  cnd = np.logical_and(tms >= startDate, tms <= endDate)
  tms = tms[cnd]
  dis = dis[cnd, :]
  disTotMean = np.nanmean(dis, 0)
  return np.array([min(tms).year]), disTotMean



def plotModelScatter(ax, modelName, modelTssPath, modelStartDate=datetime(1981,01,01), 
       msrsTssFl=defMsrsTssFile, msrsStartDate=datetime(1990, 01, 01), getStat=getYMax, scatterSize=10, timeHorizon=None):
  if os.path.isfile(modelTssPath):
    tmsMdl, statIdsMdl, disMdl = loadTssFile.loadTssFile(modelTssPath, startDate=modelStartDate)
  else:
    tmsMdl, statIdsMdl, disMdl = loadTssFile.loadTssFromDir(modelTssPath, startDate=modelStartDate)
  tmsMsrs, statIdsMsrs, disMsrs = loadTssFile.loadMeasurePseudoTss(msrsTssFl, selectStatIds=statIdsMdl)
  assert (statIdsMdl == statIdsMsrs).all()
  
  if timeHorizon is None:
    startDate = max(min(tmsMdl), min(tmsMsrs))
    endDate = min(max(tmsMdl), max(tmsMsrs))
  else:
    startDate = min(timeHorizon)
    endDate = max(timeHorizon)

  yrs, mdlStat = getStat(tmsMdl, disMdl, startDate, endDate)
  yrs, msrStat = getStat(tmsMsrs, disMsrs, startDate, endDate)

  if len(msrStat.shape) > 1:
    mdlStat = np.sort(mdlStat, 0)
    msrStat = np.sort(msrStat, 0)

  mdlStatFlt = mdlStat.flatten()
  msrStatFlt = msrStat.flatten()
  cnd = np.logical_not( 
       np.logical_or(np.isnan(msrStatFlt), np.isnan(mdlStatFlt))
       )
  mdlStatFlt = mdlStatFlt[cnd]
  msrStatFlt = msrStatFlt[cnd]
  cnd = np.logical_and(mdlStatFlt >= .1*msrStatFlt, msrStatFlt >= .1*mdlStatFlt)
  mdlStatFlt = mdlStatFlt[cnd]
  msrStatFlt = msrStatFlt[cnd]
  
  print('n of plotted dots: ' + str(len(msrStatFlt)))
  print('n of dots <   1: ' + str(len(msrStatFlt[msrStatFlt < 1])))
  print('n of dots <  10: ' + str(len(msrStatFlt[msrStatFlt < 10])))
  print('n of dots < 100: ' + str(len(msrStatFlt[msrStatFlt < 100])))
  ax.scatter(msrStatFlt, mdlStatFlt, scatterSize)
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



def plotModelScatterLog(ax, modelName, modelTssPath, modelStartDate=datetime(1981,01,01), 
       msrsTssFl=defMsrsTssFile, msrsStartDate=datetime(1990, 01, 01), getStat=getYMax, scatterSize=10):
  if os.path.isfile(modelTssPath):
    tmsMdl, statIdsMdl, disMdl = loadTssFile.loadTssFile(modelTssPath, startDate=modelStartDate)
  else:
    tmsMdl, statIdsMdl, disMdl = loadTssFile.loadTssFromDir(modelTssPath, startDate=modelStartDate)
  tmsMsrs, statIdsMsrs, disMsrs = loadTssFile.loadMeasurePseudoTss(msrsTssFl, selectStatIds=statIdsMdl)
  assert (statIdsMdl == statIdsMsrs).all()
  
  startDate = max(min(tmsMdl), min(tmsMsrs))
  endDate = min(max(tmsMdl), max(tmsMsrs))

  yrs, mdlStat = getStat(tmsMdl, disMdl, startDate, endDate)
  yrs, msrStat = getStat(tmsMsrs, disMsrs, startDate, endDate)

  if len(msrStat.shape) > 1:
    mdlStat = np.sort(mdlStat, 0)
    msrStat = np.sort(msrStat, 0)

  mdlStatFlt = mdlStat.flatten()
  msrStatFlt = msrStat.flatten()
  cnd = np.logical_not( 
       np.logical_or(np.isnan(msrStatFlt), np.isnan(mdlStatFlt))
       )
  mdlStatFlt = mdlStatFlt[cnd]
  msrStatFlt = msrStatFlt[cnd]
  cnd = np.logical_and(mdlStatFlt >= .1*msrStatFlt, msrStatFlt >= .1*mdlStatFlt)
  mdlStatFlt = mdlStatFlt[cnd]
  msrStatFlt = msrStatFlt[cnd]
  
  print('n of plotted dots: ' + str(len(msrStatFlt)))
  print('n of dots <   1: ' + str(len(msrStatFlt[msrStatFlt < 1])))
  print('n of dots <  10: ' + str(len(msrStatFlt[msrStatFlt < 10])))
  print('n of dots < 100: ' + str(len(msrStatFlt[msrStatFlt < 100])))
  ax.scatter(msrStatFlt, mdlStatFlt, scatterSize)
  ax.set_aspect('equal')
  ax.grid('on')
  ax.set_xscale('log')
  ax.set_yscale('log')
  ax.tick_params(axis='x', direction='in', pad=-15)
  ax.tick_params(axis='y', direction='in', pad=-20)
  
 #ax.figure.canvas.draw()
 #xlim = ax.get_xlim()
 #ylim = ax.get_ylim()
  xlim = [1, max(msrStatFlt)*2]
  ylim = [1, max(mdlStatFlt)*2]

  lm = [min(min(xlim), min(ylim)), max(max(xlim), max(ylim))]
  ax.set_xlim(lm)
  ax.set_ylim(lm)
  ax.plot(lm, lm, 'k')

 #emptyTicks = ['']*len(ax.get_xticklabels())
 #ax.set_xticklabels(emptyTicks)
 #emptyTicks = ['']*len(ax.get_yticklabels())
 #ax.set_yticklabels(emptyTicks)
 #ax.set_xticks([])
 #ax.set_yticks([])

  mdltxt = modelName
  mdltxt = mdltxt.replace('_BC_', '\n', 1)
  mdltxt = mdltxt.replace('_BC', '', 1)
  txtx = .5
  txty = 1./1.2
  ax.text(txtx, txty, mdltxt, fontsize=9, ha='center', va='center', transform=ax.transAxes)
  txty = 1/7.5
  ax.text(txtx, txty, 'observ.', fontsize=12, ha='center', va='center', transform=ax.transAxes)
  txtx = txty
  txty = .5
  ax.text(txtx, txty, 'model', fontsize=12, ha='center', va='center', rotation=-90, transform=ax.transAxes)

  tks = [l for l in ax.get_xticks()]
  tkslbl = ['' if tk < 10 else '$10^{' + str(int(round(np.log10(tk)))) + '}$' for tk in tks]
  ax.set_xticklabels(tkslbl)

  tks = [l for l in ax.get_yticks()]
  tkslbl = ['' if tk < 10 else '$10^{' + str(int(round(np.log10(tk)))) + '}$' for tk in tks]
  ax.set_yticklabels(tkslbl)

  pass





def plotAllMaxScatters(avgYearsByYear=False):
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

  getStat = getYMax if avgYearsByYear else getYMaxMean

  axHind = axmtx[0, 0]
  hindTssFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/efasTss/disWin.tss'
  hindStartDate = datetime(1990, 1, 1, 0, 0)
  plotModelScatterLog(axHind, 'Hindcast', hindTssFile, modelStartDate=hindStartDate, getStat=getStat)

  axmtxflt = np.array(axmtx).flatten()[1:]
  for mdl, axmdl in zip(models, axmtxflt):
    mdlDir = os.path.join(rootDir, mdl, 'wuConst')
    plotModelScatterLog(axmdl, mdl, mdlDir, getStat=getStat)
    plt.tight_layout()
    pass

  plt.suptitle('Annual Maxima', y=.995, fontsize=13)
  f.savefig(outputfig, dpi=300)




def plotAllMinScatters(avgYearsByYear=False):
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

  getStat = getYMin if avgYearsByYear else getYMinMean

  axHind = axmtx[0, 0]
  hindTssFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/efasTss/disWin.tss'
  hindStartDate = datetime(1990, 1, 1, 0, 0)
  plotModelScatterLog(axHind, 'Hindcast', hindTssFile, modelStartDate=hindStartDate, getStat=getStat)

  axmtxflt = np.array(axmtx).flatten()[1:]
  for mdl, axmdl in zip(models, axmtxflt):
    mdlDir = os.path.join(rootDir, mdl, 'wuConst')
    plotModelScatterLog(axmdl, mdl, mdlDir, getStat=getStat)
    plt.tight_layout()
    pass

  plt.suptitle('Annual Minima', y=.995, fontsize=13)
  f.savefig(outputfig, dpi=300)




def plotAllMeanScatters(avgYearsByYear=False):
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

  getStat = getYMean if avgYearsByYear else getTotMean

  axHind = axmtx[0, 0]
  hindTssFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/efasTss/disWin.tss'
  hindStartDate = datetime(1990, 1, 1, 0, 0)
  plotModelScatterLog(axHind, 'Hindcast', hindTssFile, modelStartDate=hindStartDate, getStat=getStat)

  axmtxflt = np.array(axmtx).flatten()[1:]
  for mdl, axmdl in zip(models, axmtxflt):
    mdlDir = os.path.join(rootDir, mdl, 'wuConst')
    plotModelScatterLog(axmdl, mdl, mdlDir, getStat=getStat)
    plt.tight_layout()
    pass

  plt.suptitle('Annual Means', y=.995, fontsize=13)
  f.savefig(outputfig, dpi=300)


    
    
  
def plotModelScatterEfasMax():
  outputfig = 'mdlScatterHindcastMax.png'
  modelTssFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/efasTss/disWin.tss'
  modelStartDate = datetime(1990, 1, 1, 0, 0)
  f = plt.figure(figsize=(3, 3))
  ax = f.gca()
  plotModelScatterLog(ax, 'Hindcast', modelTssFile, modelStartDate=modelStartDate, scatterSize=10, getStat=getYMaxMean)
  f.savefig(outputfig, dpi=300)
  
  
def plotModelScatterEfasMean():
  outputfig = 'mdlScatterHindcastMean.png'
  modelTssFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/efasTss/disWin.tss'
  modelStartDate = datetime(1990, 1, 1, 0, 0)
  f = plt.figure(figsize=(3, 3))
  ax = f.gca()
  plotModelScatterLog(ax, 'Hindcast', modelTssFile, modelStartDate=modelStartDate, scatterSize=10, getStat=getTotMean)
  f.savefig(outputfig, dpi=300)
  
  
def plotModelScatterEfasMin():
  outputfig = 'mdlScatterHindcastMin.png'
  modelTssFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/efasTss/disWin.tss'
  modelStartDate = datetime(1990, 1, 1, 0, 0)
  f = plt.figure(figsize=(3, 3))
  ax = f.gca()
  plotModelScatterLog(ax, 'Hindcast', modelTssFile, modelStartDate=modelStartDate, scatterSize=10, getStat=getYMinMean)
  f.savefig(outputfig, dpi=300)

def plotModelScatter_testValerioSttsIPSLinput():
  outputfig = 'testValerioSttsIPSLinput_max.png'
  modelTssFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/validationData/disWin_test_valerioStts_IPSLinput.tss'
  modelStartDate = datetime(1990, 1, 1, 0, 0)
  f = plt.figure(figsize=(3, 3))
  ax = f.gca()
  plotModelScatter(ax, 'test hindcast stts\nIPSL input, max', modelTssFile, modelStartDate=modelStartDate, scatterSize=10, getStat=getYMaxMean)
  f.savefig(outputfig, dpi=300)
  plt.cla()

  outputfig = 'testValerioSttsIPSLinput_mean.png'
  modelTssFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/validationData/disWin_test_valerioStts_IPSLinput.tss'
  modelStartDate = datetime(1990, 1, 1, 0, 0)
  f = plt.figure(figsize=(3, 3))
  ax = f.gca()
  plotModelScatter(ax, 'test hindcast stts\nIPSL input, mean', modelTssFile, modelStartDate=modelStartDate, scatterSize=10, getStat=getTotMean)
  f.savefig(outputfig, dpi=300)
  plt.cla()

  outputfig = 'testValerioSttsIPSLinput_min.png'
  modelTssFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/validationData/disWin_test_valerioStts_IPSLinput.tss'
  modelStartDate = datetime(1990, 1, 1, 0, 0)
  f = plt.figure(figsize=(3, 3))
  ax = f.gca()
  plotModelScatter(ax, 'test hindcast stts\nIPSL input, min', modelTssFile, modelStartDate=modelStartDate, scatterSize=10, getStat=getYMinMean)
  f.savefig(outputfig, dpi=300)
  plt.cla()

def plotModelScatter_testOldLisvap_CLMcom_ICHEC_EC_EARTH():
  outputfig = 'testOldLisvap_max.png'
  modelTssFile = '/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/src/git/lisfloodRunManager/CORDEXRuns/lisvapRuns/lisfloodTest/out/disWin.tss'
  modelStartDate = datetime(1981, 1, 1, 0, 0)
  endDate = datetime(2015, 1, 1)
  timeHorizon = [modelStartDate, endDate]
  f = plt.figure(figsize=(3, 3))
  ax = f.gca()
  plotModelScatter(ax, 'test old lisvap\nCLMcom ICHEC_ECEARTH\nmax', modelTssFile, modelStartDate=modelStartDate, scatterSize=10, getStat=getYMaxMean, timeHorizon=timeHorizon)
  f.savefig(outputfig, dpi=300)
  plt.cla()

  outputfig = 'testOldLisvap_mean.png'
  f = plt.figure(figsize=(3, 3))
  ax = f.gca()
  plotModelScatter(ax, 'test old lisvap\nCLMcom ICHEC_ECEARTH\nmean', modelTssFile, modelStartDate=modelStartDate, scatterSize=10, getStat=getTotMean, timeHorizon=timeHorizon)
  f.savefig(outputfig, dpi=300)
  plt.cla()

  outputfig = 'testOldLisvap_min.png'
  f = plt.figure(figsize=(3, 3))
  ax = f.gca()
  plotModelScatter(ax, 'test old lisvap\nCLMcom ICHEC_ECEARTH\nmin', modelTssFile, modelStartDate=modelStartDate, scatterSize=10, getStat=getYMinMean, timeHorizon=timeHorizon)
  f.savefig(outputfig, dpi=300)
  plt.cla()


