from datetime import datetime
import numpy as np
from matplotlib import pyplot as plt

import loadTssFile



def plotSingle(tms, dis):
  p = plt.plot(tms, dis[:,0])
  plt.grid('on')
  return p



def testPlotMax():
  flpth = '/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/ClimateRuns/LisfloodEuroCordex/historical/IPSL-INERIS-WRF331F_BC/wuConst/disWin_IPSL-INERIS-WRF331F_BC_historical_wuConst_1982010100.tss'

  fldirHist = '/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/ClimateRuns/LisfloodEuroCordex/historical/IPSL-INERIS-WRF331F_BC/wuConst/'
  fldirRcp85 = '/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/ClimateRuns/LisfloodEuroCordex/rcp85/IPSL-INERIS-WRF331F_BC/wuChang/'
  fldirRcp45 = '/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/ClimateRuns/LisfloodEuroCordex/rcp45/IPSL-INERIS-WRF331F_BC/wuChang/'
  histStartDate = datetime(1981, 01, 01)
  rcpStartDate = datetime(2011, 01, 01)

  tms, statIds, dis = loadTssFile.loadTssFile(flpth)
  mxindx = np.where(dis[-1,:] == max(dis[-1,:]))
  selectStatIds = statIds[mxindx]
  tmsHist, statIds, disHist = loadTssFile.loadTssFromDir(fldirHist, startDate=histStartDate, selectStatIds=selectStatIds)
  plotSingle(tmsHist, disHist)
  tmsRcp85, statIds, disRcp85 = loadTssFile.loadTssFromDir(fldirRcp85, startDate=rcpStartDate, selectStatIds=selectStatIds)
  plotSingle(tmsRcp85, disRcp85)
  tmsRcp45, statIds, disRcp45 = loadTssFile.loadTssFromDir(fldirRcp45, startDate=rcpStartDate, selectStatIds=selectStatIds)
  plotSingle(tmsRcp45, disRcp45)



def testPlotStat(statId = 210):
  fldirHist = '/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/ClimateRuns/LisfloodEuroCordex/historical/IPSL-INERIS-WRF331F_BC/wuConst/'
  fldirRcp85 = '/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/ClimateRuns/LisfloodEuroCordex/rcp85/IPSL-INERIS-WRF331F_BC/wuChang/'
  fldirRcp45 = '/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/ClimateRuns/LisfloodEuroCordex/rcp45/IPSL-INERIS-WRF331F_BC/wuChang/'
  msrsFl = '/STORAGE/src1/git/lisfloodRunManager/verifyOutput/testdata/disWin_measuresGauges.tss'
  histStartDate = datetime(1981, 01, 01)
  rcpStartDate = datetime(2011, 01, 01)
  msrsStartDate = datetime(1991, 01, 01)

  selectStatIds = [statId]
  tmsHist, statIds, disHist = loadTssFile.loadTssFromDir(fldirHist, startDate=histStartDate, selectStatIds=selectStatIds)
  tmsRcp85, statIds, disRcp85 = loadTssFile.loadTssFromDir(fldirRcp85, startDate=rcpStartDate, selectStatIds=selectStatIds)
  tmsRcp45, statIds, disRcp45 = loadTssFile.loadTssFromDir(fldirRcp45, startDate=rcpStartDate, selectStatIds=selectStatIds)
  tmsMsrs, statIds, disMsrs = loadTssFile.loadTssFile(msrsFl, startDate=msrsStartDate, selectStatIds=selectStatIds)
  plotSingle(tmsHist, disHist)
  plotSingle(tmsRcp85, disRcp85)
  plotSingle(tmsRcp45, disRcp45)
  plotSingle(tmsMsrs, disMsrs)
  plt.plot(tmsMsrs, disMsrs)




def testSalzburgScatters():
  statId = 210
  fldirHist = '/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/ClimateRuns/LisfloodEuroCordex/historical/IPSL-INERIS-WRF331F_BC/wuConst/'

  



