from scipy.stats import genextreme as gev
import numpy as np

import os
from datetime import datetime
from matplotlib import pyplot as plt
from sklearn.metrics import r2_score

import loadTssFile


retPer = np.array([5, 10, 20])


def getQminTimeSeries(tms, dis, startDate, endDate):
  cnd = np.logical_and(tms >= startDate, tms <= endDate)
  tms = tms[cnd]
  dis = dis[cnd, :]
  # computing the moving average
  nma = 7
  discs = np.nancumsum(dis, axis=0)
  nancountcs = np.nancumsum(np.isnan(dis), axis=0)
  dissum = discs[nma:,:] - discs[:-nma,:]
  nnan = nancountcs[nma:,:] - nancountcs[:-nma,:]
  ndis = (nma - nnan).astype(float)
  assert np.all(ndis >= 0)
  ndis[ndis == 0] = np.nan
  dis_ = dissum/ndis
  ii = int(np.floor(nma/2))
  tms_ = tms[ii:-ii-1]

  estYrs = np.array([t.year for t in tms_])
  yrs = np.unique(estYrs)
  ny = len(yrs)
  disMin = np.ones([ny, dis_.shape[1]])*np.nan

  for iy in range(ny):
    y = yrs[iy]
    cndy = estYrs == y
    disy = dis_[cndy, :]
   #nanratio = np.sum(np.isnan(disy), 0) / len(disy)
    disMiny = np.nanmin(disy, 0)
   #disMiny[nanratio > .5] = np.nan
    disMin[iy, :] = disMiny
  return yrs, disMin


def doGev(dis, retPerYr):
  prob = 1-1/retPerYr
  npt = dis.shape[1]
  nretper = len(retPerYr)
  retLev = np.ones([npt, nretper])*np.nan
  for ipt in range(npt):
    disii = dis[:,ipt]
    disii = disii[~np.isnan(disii)]
    if len(disii) > 15:
      shape, loc, scale = gev.fit(-disii)
      retLevII = -gev.ppf(prob, shape, loc=loc, scale=scale)
      if sum(retLevII < 0) == 0:
        retLev[ipt, :] = retLevII
  return retLev
   

def getHindcast():
  startDate = datetime(1990, 1, 1)
  endDate = datetime(2016, 1, 1)
  hindTssFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/efasTss/disWin.tss'
  tmsHind, statIds, disHind = loadTssFile.loadTssFile(hindTssFile, startDate=startDate)
  yrs, hindQMin = getQminTimeSeries(tmsHind, disHind, startDate, endDate)
  qminMean = np.nanmean(hindQMin, 0)
  
  retLev = doGev(hindQMin, retPer)

  return statIds, retLev, qminMean


def getObservation(statIds, dbversion='new'):
  startDate = datetime(1990, 1, 1)
  endDate = datetime(2016, 1, 1)
  if dbversion == 'old':
    msrsTssFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/validationData/Qts_Europe_measurements.csv'
    tmsMsrs, statIdsMsrs, disMsrs = loadTssFile.loadMeasurePseudoTss(msrsTssFile, selectStatIds=statIds)
  else:
    msrFlPath = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/validationData/newObservationsDb/Daily_Discharge_from_1950.csv'
    statIdFlPath = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/validationData/newObservationsDb/EfasToC.xls'
    cacheFilePath = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/validationData/newObservationsDb/Daily_Discharge_from_1950.cache'
    tmsMsrs, statIdsMsrs, disMsrs = loadTssFile.loadNewObservationDataset(msrFlPath, statIdFlPath, cacheFilePath, timeHorizon=[startDate, endDate], selectStatIds=statIds)
  assert(np.all(statIdsMsrs == statIds))
  yrs, msrsQMin = getQminTimeSeries(tmsMsrs, disMsrs, startDate, endDate)
  qminMean = np.nanmean(msrsQMin, 0)
  
  retLev = doGev(msrsQMin, retPer)
  cndNan = np.isnan(retLev[:,1])
  qminMean[cndNan] = np.nan

  return statIds, retLev, qminMean


def diagnoseObsVsHindcastAnnualMean():
  hindTssFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/efasTss/disWin.tss'
  tmsHind, statIds0, disHind = loadTssFile.loadTssFile(hindTssFile, startDate=datetime(1990, 1, 1))
  statIds_ = loadTssFile.filterCatchmentAreasLowerThan(statIds0)
  statIdsMsk = np.in1d(statIds0, statIds_)
  statIds = statIds0[statIdsMsk]
  disHind = disHind[:, statIdsMsk]
  hindYrs, hindQmin = compareLowFlowGevs.getQminTimeSeries(tmsHind, disHind, startDate, endDate)
  hindMn = np.nanmean(hindQmin, 0)

  startDate = datetime(1990, 1, 1)
  endDate = datetime(2014, 12, 31)
  msrFlPath = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/validationData/newObservationsDb/Daily_Discharge_from_1950.csv'
  statIdFlPath = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/validationData/newObservationsDb/EfasToC.xls'
  cacheFilePath = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/validationData/newObservationsDb/Daily_Discharge_from_1950.cache'
  tmsMsrs, statIdsMsrs, disMsrs = loadTssFile.loadNewObservationDataset(msrFlPath, statIdFlPath, cacheFilePath, timeHorizon=[startDate, endDate], selectStatIds=statIds)
  msrsYrs, msrsQmin = getQminTimeSeries(tmsMsrs, disMsrs)
  msrsMn = np.nanmean(msrsQmin, 0)

  msrsTssFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/validationData/Qts_Europe_measurements.csv'
  tmsMsrs_old, statIdsMsrs_old, disMsrs_old = loadTssFile.loadMeasurePseudoTss(msrsTssFile, selectStatIds=statIds)
  msrsYrs_old, msrsQmin_old = compareLowFlowGevs.getQminTimeSeries(tmsMsrs_old, disMsrs_old, startDate, endDate)
  msrsMn_old = np.nanmean(msrsQmin_old, 0)

  diagStatIndex = 320 #50th percentile of bias
  plt.plot(tmsHind, disHind[:,diagStatIndex], label='hindcast')
  plt.plot(tmsMsrs, disMsrs[:,diagStatIndex], label='db new')
  plt.plot(tmsMsrs_old, disMsrs_old[:,diagStatIndex], label='db old')
  plt.legend()
  plt.show()



def getR2Score(ref, model):
  cnd = np.logical_and(~np.isnan(ref), ~np.isnan(model))
  ref = ref[cnd]
  model = model[cnd]
  r2 = 1 - np.nanmean((model - ref)**2)/np.nanvar(ref)
 #r2 = r2_score(ref, model)
  return r2

def getPBias(ref, model):
  cnd = np.logical_and(~np.isnan(ref), ~np.isnan(model))
  ref = ref[cnd]
  model = model[cnd]
  pbias = 100 * np.nansum(model - ref)/np.nansum(ref)
  return pbias


def plotScatter(ax, msrsRL, hindRL, xlim, text):
  lowlim = 1.1
  cnd = np.logical_and(msrsRL >= lowlim, hindRL >= lowlim)
  plt.scatter(msrsRL[cnd], hindRL[cnd], s=30)
  ax.set_aspect('equal')
  ax.grid('on')
  ax.set_xscale('log')
  ax.set_yscale('log')
 #xlim = ax.get_xlim()
 #ylim = ax.get_ylim()
  ylim = xlim
  lm = [min(min(xlim), min(ylim)), max(max(xlim), max(ylim))]
 #lm = [1, 1e4]
  ax.set_xlim(lm)
  ax.set_ylim(lm)
  ax.plot(lm, lm, 'k')
  txtx = .5
  txty = 1./1.2
  ax.text(txtx, txty, text, fontsize=14, ha='center', va='center', transform=ax.transAxes)
  txty = 1/15
  ax.text(txtx, txty, 'observations', fontsize=12, ha='center', va='center', transform=ax.transAxes)
  txtx = txty
  txty = .5
  ax.text(txtx, txty, 'model', fontsize=12, ha='center', va='center', rotation=-90, transform=ax.transAxes)

  txtx = .5
  txty = .27
  r2 = getR2Score(msrsRL, hindRL)
  ax.text(txtx, txty, '$NSE = {r2:1.2f}$'.format(r2=r2), fontsize=12, ha='left', va='center', transform=ax.transAxes)
  txty = .2
  bi = getPBias(msrsRL, hindRL)
  ax.text(txtx, txty, '$bias = {bi:1.0f} \%$'.format(bi=bi), fontsize=12, ha='left', va='center', transform=ax.transAxes)

  plt.xlabel('$Q_{min}$, $m^3 s^{-1}$', fontsize=12)


def doPlotScatter():
  outPngFileName = 'lowFlowGEVScatter.png'

  print('loading hindcast')
  statIds0, hindRL0, hindMn0 = getHindcast()
  statIds_ = loadTssFile.filterCatchmentAreasLowerThan(statIds0)
  statIdsMsk = np.in1d(statIds0, statIds_)
  statIds = statIds0[statIdsMsk]
  hindRL = hindRL0[statIdsMsk]
  hindMn = hindMn0[statIdsMsk]
  print('loading observations')
  statIds, msrsRL, msrsMn = getObservation(statIds, dbversion='new')
  print('number of stations: ' + str(msrsRL[:,1].shape[0]-np.sum(np.isnan(msrsRL[:,1]))))

 #f = plt.figure(figsize=(4, 4))
 #ax = f.gca()
 #xlim = [1, 1000]
 #plotScatter(ax, msrsRL[:,0], hindRL[:,0], xlim, 'hindcast\n20-year r.l.')
 #plt.tight_layout()

  f, axmtx = plt.subplots(1, 3, figsize=(8, 3))
 #f, axmtx = plt.subplots(2, 2, figsize=(6, 6))

  """
  ax = axmtx[0, 0]
  plt.axes(ax)
 #plt.scatter(msrsRL[:,0], hindRL[:,0])
  plotScatter(ax, msrsMn, hindMn, [1, 2000], 'hindcast mean')
  ax.set_aspect('equal')
  ax.grid('on')
  ax.yaxis.set_ticks_position('left')
  ax.xaxis.set_ticks_position('top')
  ax.xaxis.set_label_position('top')
  plt.tight_layout()
  """
 
  ax = axmtx[0]
  plt.axes(ax)
  plotScatter(ax, msrsRL[:,0], hindRL[:,0], [1, 10000], 'hindcast\n5-year r.l.')
  ax.set_aspect('equal')
  ax.grid('on')
 #ax.set_yticklabels([])
  ax.yaxis.set_ticks_position('left')
 #ax.xaxis.set_ticks_position('top')
 #ax.xaxis.set_label_position('top')
  ax.set_xticks([1, 10, 100, 1000, 10000])
  plt.tight_layout()

  ax = axmtx[1]
  plt.axes(ax)
  plotScatter(ax, msrsRL[:,1], hindRL[:,1], [1, 10000], 'hindcast\n10-year r.l.')
  ax.set_aspect('equal')
  ax.grid('on')
  ax.set_yticklabels([])
  ax.set_xticks([1, 10, 100, 1000, 10000])
 #ax.yaxis.set_ticks_position('left')

  ax = axmtx[2]
  plt.axes(ax)
  plotScatter(ax, msrsRL[:,2], hindRL[:,2], [1, 10000], 'hindcast\n20-year r.l.')
  ax.set_aspect('equal')
  ax.grid('on')
  ax.yaxis.set_ticks_position('right')
  ax.set_xticks([1, 10, 100, 1000, 10000])
  plt.tight_layout(pad=.01)
  
  f.savefig(outPngFileName, dpi=300)

  



