import os
from datetime import datetime
import pandas as pd
import numpy as np
import netCDF4
from matplotlib import pyplot as plt

import loadTssFile


dftBaseDir = '/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/ClimateRuns/LisfloodEuroCordex/'
dftModel = 'CLMcom-CCLM4-8-17_BC_ICHEC-EC-EARTH'
dftScenH = 'historical'
timeHorzH = [datetime(1981, 01, 01), datetime(2010, 01, 01)]
yearH = 1995
dftScenR = 'rcp85'
timeHorzR = [datetime(2060, 01, 01), datetime(2100, 01, 01)]
yearR = 2085
dftWuStr = 'wuConst'

dftStid = 25 # close to duna
dftStid = 136 # close to po

dftEvaNcFile = 'test/rcp85_CLMcom-CCLM4-8-17_BC_ICHEC-EC-EARTH_wuConst_dis_statistics.nc'
dftEvaNcFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/lisfloodEVA/test/rcp85_CLMcom-CCLM4-8-17_BC_ICHEC-EC-EARTH_wuConst_dis_statistics_5EvtPerYear.nc'

def plotDiagnostics( baseDir=dftBaseDir, model=dftModel, scenH=dftScenH, scenR=dftScenR, wuStr=dftWuStr, stid=dftStid, evaNcFile=dftEvaNcFile ):
  outletNcFl = '../util/outlets.nc'
  dso = netCDF4.Dataset(outletNcFl)
  otl = dso.variables['outlets'][:]
  otlx = dso.variables['x'][:]
  otly = dso.variables['y'][:]
  [iyst, ixst] = np.where(otl == stid)
  xst = otlx[ixst]
  yst = otly[iyst]
  dso.close()

  pathH = os.path.join(baseDir, scenH, model, wuStr)
  tmsH, statIds, disH = loadTssFile.loadTssFromDir(pathH, selectStatIds=[stid], startDate=datetime(1981, 1, 1))
  dt = pd.DataFrame([np.array([t.year for t in tmsH]), disH]).transpose()
  dtgp = dt.groupby(0)
  yrsH = np.array(dtgp.groups.keys())
  mxH = np.array(dtgp.max()[1])
  
  pathR = os.path.join(baseDir, scenR, model, wuStr)
  tmsR, statIds, disR = loadTssFile.loadTssFromDir(pathR, selectStatIds=[stid], startDate=datetime(2011, 1, 1))
  cndt = np.logical_and(tmsR >= timeHorzR[0], tmsR <= timeHorzR[1])
  tmsR = tmsR[cndt]
  disR = disR[cndt]
  dt = pd.DataFrame([np.array([t.year for t in tmsR]), disR]).transpose()
  dtgp = dt.groupby(0)
  yrsR = np.array(dtgp.groups.keys())
  mxR = np.array(dtgp.max()[1])

  ds = netCDF4.Dataset(evaNcFile)
  rl = ds.variables['rl'][:]
  rp = ds.variables['return_period'][:]
  x = ds.variables['x'][:]
  y = ds.variables['y'][:]
  yrs = ds.variables['year'][:]
  ds.close()
  irp0 = np.where(rp == 20)
  irp1 = np.where(rp == 50)
  irp2 = np.where(rp == 100)
 #iyh = np.where(yrs == yearH)
  iyh = 3
 #iyr = np.where(yrs == yearR)
  iyr = 21
  ix = np.where(x == xst)
  iy = np.where(y == yst)

  rlh0 = np.squeeze(rl[irp0, iyh, ix, iy])*np.ones(yrsH.shape) 
  rlh1 = np.squeeze(rl[irp1, iyh, ix, iy])*np.ones(yrsH.shape)
  rlh2 = np.squeeze(rl[irp2, iyh, ix, iy])*np.ones(yrsH.shape) 
  fgh = plt.figure()
  prlh0, = plt.plot(yrsH, rlh0) 
  prlh1, = plt.plot(yrsH, rlh1) 
  prlh2, = plt.plot(yrsH, rlh2) 
  pymxh, = plt.plot(yrsH, mxH, 'o')
  plt.legend([prlh0, prlh1, prlh2], ['20y', '50y', '100y'])
  plt.title('1981-2010')
  
  rlr0 = np.squeeze(rl[irp0, iyr, ix, iy])*np.ones(yrsR.shape) 
  rlr1 = np.squeeze(rl[irp1, iyr, ix, iy])*np.ones(yrsR.shape)
  rlr2 = np.squeeze(rl[irp2, iyr, ix, iy])*np.ones(yrsR.shape) 
  fgh = plt.figure()
  prlr0, = plt.plot(yrsR, rlr0) 
  prlr1, = plt.plot(yrsR, rlr1) 
  prlr2, = plt.plot(yrsR, rlr2) 
  pymxr, = plt.plot(yrsR, mxR, 'o')
  plt.legend([prlr0, prlr1, prlr2], ['20y', '50y', '100y'])
  plt.title('2070-2100')
  
  
  


