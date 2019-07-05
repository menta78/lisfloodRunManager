import numpy as np
from scipy import stats
from matplotlib import pyplot as plt
from matplotlib import gridspec

import loadWlVsScenChange
from getWarmingLevels import getWarmingLevels

nmodels=-1



def getNYrsTimeSeriesAroundWl(years, timeSeries, warmingLevelYears, models, halfWindowSize=3):
  tsshp = timeSeries.shape
  outTs = np.zeros([tsshp[0], halfWindowSize*2+1, tsshp[2], tsshp[3]])*np.nan
  for mdl, imdl in zip(models, range(len(models))):
    ywl_ = warmingLevelYears[mdl]
    # rounding to 5 years
    ywl = np.round(ywl_/5.)*5
    iywl = np.where(years == ywl)[0][0]
    outTs[imdl, :] = timeSeries[imdl, iywl-halfWindowSize:iywl+halfWindowSize+1]
  return outTs

def getRelChng(yrs, tmsrs, baselineYear=1995):
  ibsln = yrs == baselineYear
  vlbsln_ = tmsrs[:, ibsln, :, :]
  vlbsln = np.tile(vlbsln_, [1, tmsrs.shape[1], 1, 1])
  relChng = (tmsrs-vlbsln)/vlbsln
  return relChng

def getMeanAndSigma(srs):
  timeSz = srs.shape[1]
  yindx = timeSz / 2
  srsMean = np.mean(srs[:, yindx, :, :], 0)
  srsSigma = np.std(srs[:, yindx, :, :], 0)
  return srsMean, srsSigma


def plotTimeSerie30YVariability_hiExt(ax=None, plotXLabel=True):
  yrs, rpR8Srs, rpR4Srs, models = loadWlVsScenChange.loadRetPerAllYears(nmodels=nmodels)
  rpR8 = getRelChng(yrs, rpR8Srs)
  rpR4 = getRelChng(yrs, rpR4Srs)

  wlyR8 = getWarmingLevels('rcp85', 2.0)
  r8srs = getNYrsTimeSeriesAroundWl(yrs, rpR8, wlyR8, models)
  r8medianWl, r8sigmaWl = getMeanAndSigma(r8srs)
  cndSignR8 = np.abs(r8medianWl) > r8sigmaWl
  cndPosi = r8medianWl > 0
 #cnd = np.logical_and(cndSignR8, cndPosi)
  cnd = cndPosi
  cndMtx = np.tile(cnd, [r8srs.shape[0], r8srs.shape[1], 1, 1])
  r8srs[~cndMtx] = np.nan
  r8median_ = np.median(r8srs, 0)
  r8median = r8median_.reshape(r8median_.shape[0], r8median_.shape[1]*r8median_.shape[2])
  r8median = np.nanmedian(r8median, 1)
 #r8median = np.nanmean(r8median, 1)

  r8spmean = r8srs.reshape(r8srs.shape[0], r8srs.shape[1], r8srs.shape[2]*r8srs.shape[3])
  r8spmean = np.nanmedian(r8spmean, 2)
 #r8spmean = np.nanmean(r8spmean, 2)
  r8skew = stats.skew(r8spmean[:, 3])
  r8sigma = np.std(r8spmean[:, 3])
  r8median = np.nanmedian(r8spmean, 0)

  wlyR4 = getWarmingLevels('rcp45', 2.0)
  r4srs = getNYrsTimeSeriesAroundWl(yrs, rpR4, wlyR4, models)
  r4medianWl, r4sigmaWl = getMeanAndSigma(r4srs)
  cndSignR4 = np.abs(r4medianWl) > r4sigmaWl
  cndPosi = r4medianWl > 0
  cnd = cndPosi
  cndMtx = np.tile(cnd, [r4srs.shape[0], r4srs.shape[1], 1, 1])
  r4srs[~cndMtx] = np.nan
  r4median_ = np.median(r4srs, 0)
  r4median = r4median_.reshape(r4median_.shape[0], r4median_.shape[1]*r4median_.shape[2])
  r4median = np.nanmedian(r4median, 1)
 #r4median = np.nanmean(r4median, 1)

  r4spmean = r4srs.reshape(r4srs.shape[0], r4srs.shape[1], r4srs.shape[2]*r4srs.shape[3])
  r4spmean = np.nanmedian(r4spmean, 2)
 #r4spmean = np.nanmean(r4spmean, 2)
  r4skew = stats.skew(r4spmean[:, 3])
  r4sigma = np.std(r4spmean[:, 3])
  r4median = np.nanmedian(r4spmean, 0)

  yr = [-15, -10, -5, 0, 5, 10, 15]
  if ax is None:
    fg = plt.figure(figsize=[8.46, 4.98])
  pmdlr8 = plt.plot(yr, r8spmean.transpose()*100, 'peachpuff', label='RCP8.5 models ($\sigma={sgm:1.2f}\%, skw.={s:1.2f}$)'.format(sgm=r8sigma*100, s=r8skew)); 
  pmdlr4 = plt.plot(yr, r4spmean.transpose()*100, 'skyblue', label='RCP4.5 models ($\sigma={sgm:1.2f}\%, skw.={s:1.2f})$'.format(sgm=r4sigma*100, s=r4skew)); 
  pmedr8 = plt.plot(yr, r8median*100, 'firebrick', linewidth=6, label='RCP8.5 median'); 
  pmedr4 = plt.plot(yr, r4median*100, 'royalblue', linewidth=6, label='RCP4.5 median'); 
  plt.grid('on')
  plt.legend(handles=[pmdlr8[0], pmedr8[0], pmdlr4[0], pmedr4[0]])
  if plotXLabel:
    plt.xlabel('years to $2^\circ C w.l.$', fontsize=14)
  plt.ylabel('$Q_{H100}$ % change', fontsize=14)
  plt.tight_layout()
  if ax is None:
    fg.savefig('./ensemblesVariabilityAround2deg.png', dpi=400)


def plotTimeSerie30YVariability_lowExt(ax=None, plotXLabel=True):
  yrs, rpR8Srs, rpR4Srs, models = loadWlVsScenChange.loadRetPerAllYears(rlVarName='rl_min', nmodels=nmodels)
  rpR8 = getRelChng(yrs, rpR8Srs)
  rpR4 = getRelChng(yrs, rpR4Srs)

  wlyR8 = getWarmingLevels('rcp85', 2.0)
  r8srs = getNYrsTimeSeriesAroundWl(yrs, rpR8, wlyR8, models)
  r8medianWl, r8sigmaWl = getMeanAndSigma(r8srs)
  cndSignR8 = np.abs(r8medianWl) > r8sigmaWl
  cndPosi = r8medianWl > 0
 #cnd = np.logical_and(cndSignR8, cndPosi)
  cnd = cndPosi
  cndMtx = np.tile(cnd, [r8srs.shape[0], r8srs.shape[1], 1, 1])
  r8srs[~cndMtx] = np.nan
  r8median_ = np.median(r8srs, 0)
  r8median = r8median_.reshape(r8median_.shape[0], r8median_.shape[1]*r8median_.shape[2])
  r8median = np.nanmedian(r8median, 1)
 #r8median = np.nanmean(r8median, 1)

  r8spmean = r8srs.reshape(r8srs.shape[0], r8srs.shape[1], r8srs.shape[2]*r8srs.shape[3])
  r8spmean = np.nanmedian(r8spmean, 2)
 #r8spmean = np.nanmean(r8spmean, 2)
  r8skew = stats.skew(r8spmean[:, 3])
  r8sigma = np.std(r8spmean[:, 3])
  r8median = np.nanmedian(r8spmean, 0)

  wlyR4 = getWarmingLevels('rcp45', 2.0)
  r4srs = getNYrsTimeSeriesAroundWl(yrs, rpR4, wlyR4, models)
  r4medianWl, r4sigmaWl = getMeanAndSigma(r4srs)
  cndSignR4 = np.abs(r4medianWl) > r4sigmaWl
  cndPosi = r4medianWl > 0
 #cnd = np.logical_and(cndSignR4, cndPosi)
  cnd = cndPosi
  cndMtx = np.tile(cnd, [r4srs.shape[0], r4srs.shape[1], 1, 1])
  r4srs[~cndMtx] = np.nan
  r4median_ = np.median(r4srs, 0)
  r4median = r4median_.reshape(r4median_.shape[0], r4median_.shape[1]*r4median_.shape[2])
  r4median = np.nanmedian(r4median, 1)
 #r4median = np.nanmean(r4median, 1)

  r4spmean = r4srs.reshape(r4srs.shape[0], r4srs.shape[1], r4srs.shape[2]*r4srs.shape[3])
  r4spmean = np.nanmedian(r4spmean, 2)
 #r4spmean = np.nanmean(r4spmean, 2)
  r4skew = stats.skew(r4spmean[:, 3])
  r4sigma = np.std(r4spmean[:, 3])
  r4median = np.nanmedian(r4spmean, 0)

  yr = [-15, -10, -5, 0, 5, 10, 15]
  if ax is None:
    fg = plt.figure(figsize=[8.46, 4.98])
  pmdlr8 = plt.plot(yr, r8spmean.transpose()*100, 'peachpuff', label='RCP8.5 models ($\sigma={sgm:1.2f}\%, skw.={s:1.2f}$)'.format(sgm=r8sigma*100, s=r8skew)); 
  pmdlr4 = plt.plot(yr, r4spmean.transpose()*100, 'skyblue', label='RCP4.5 models ($\sigma={sgm:1.2f}\%, skw.={s:1.2f}$)'.format(sgm=r4sigma*100, s=r4skew)); 
  pmedr8 = plt.plot(yr, r8median*100, 'firebrick', linewidth=6, label='RCP8.5 median'); 
  pmedr4 = plt.plot(yr, r4median*100, 'royalblue', linewidth=6, label='RCP4.5 median'); 
  plt.grid('on')
  plt.legend(handles=[pmdlr8[0], pmedr8[0], pmdlr4[0], pmedr4[0]])
  if plotXLabel:
    plt.xlabel('years to $2^\circ C w.l.$', fontsize=14)
  plt.ylabel('$Q_{L15}$ % change', fontsize=14)
  plt.tight_layout()
  if ax is None:
    fg.savefig('./ensemblesVariabilityAround2deg_lowExt.png', dpi=400)


def plotTimeSerie30YVariability_mean(ax=None, plotXLabel=True):
  _, _, _, r8srs, r4srs = loadWlVsScenChange.loadMeanChangesAtWl_nYearsAroundWLYear(warmingLev=2.0, nmodels=nmodels)

  r8medianWl, r8sigmaWl = getMeanAndSigma(r8srs)
  cndSignR8 = np.abs(r8medianWl) > r8sigmaWl
  cndPosi = r8medianWl > 0
 #cnd = np.logical_and(cndSignR8, cndPosi)
  cnd = cndPosi
  cndMtx = np.tile(cnd, [r8srs.shape[0], r8srs.shape[1], 1, 1])
  r8srs[~cndMtx] = np.nan
  r8median_ = np.median(r8srs, 0)
  r8median = r8median_.reshape(r8median_.shape[0], r8median_.shape[1]*r8median_.shape[2])
  r8median = np.nanmedian(r8median, 1)
 #r8median = np.nanmean(r8median, 1)

  r8spmean = r8srs.reshape(r8srs.shape[0], r8srs.shape[1], r8srs.shape[2]*r8srs.shape[3])
  r8spmean = np.nanmedian(r8spmean, 2)
  r8skew = stats.skew(r8spmean[:, 3])
  r8sigma = np.std(r8spmean[:, 3])
  r8median = np.nanmedian(r8spmean, 0)

  r4medianWl, r4sigmaWl = getMeanAndSigma(r4srs)
  cndSignR4 = np.abs(r4medianWl) > r4sigmaWl
  cndPosi = r4medianWl > 0
 #cnd = np.logical_and(cndSignR4, cndPosi)
  cnd = cndPosi
  cndMtx = np.tile(cnd, [r4srs.shape[0], r4srs.shape[1], 1, 1])
  r4srs[~cndMtx] = np.nan
  r4median_ = np.median(r4srs, 0)
  r4median = r4median_.reshape(r4median_.shape[0], r4median_.shape[1]*r4median_.shape[2])
  r4median = np.nanmedian(r4median, 1)
 #r4median = np.nanmean(r4median, 1)

  r4spmean = r4srs.reshape(r4srs.shape[0], r4srs.shape[1], r4srs.shape[2]*r4srs.shape[3])
  r4spmean = np.nanmedian(r4spmean, 2)
  r4skew = stats.skew(r4spmean[:, 3])
  r4sigma = np.std(r4spmean[:, 3])
  r4median = np.nanmedian(r4spmean, 0)

  yr = [-15, -10, -5, 0, 5, 10, 15]
  if ax is None:
    fg = plt.figure(figsize=[8.46, 4.98])
  pmdlr8 = plt.plot(yr, r8spmean.transpose()*100, 'peachpuff', label='RCP8.5 models ($\sigma={sgm:1.2f}\%, skw.={s:1.2f}$)'.format(sgm=r8sigma*100, s=r8skew)); 
  pmdlr4 = plt.plot(yr, r4spmean.transpose()*100, 'skyblue', label='RCP4.5 models ($\sigma={sgm:1.2f}\%, skw.={s:1.2f}$)'.format(sgm=r4sigma*100, s=r4skew)); 
  pmedr8 = plt.plot(yr, r8median*100, 'firebrick', linewidth=6, label='RCP8.5 median'); 
  pmedr4 = plt.plot(yr, r4median*100, 'royalblue', linewidth=6, label='RCP4.5 median'); 
  plt.grid('on')
  plt.legend(handles=[pmdlr8[0], pmedr8[0], pmdlr4[0], pmedr4[0]])
  if plotXLabel:
    plt.xlabel('years to $2^\circ C w.l.$', fontsize=14)
  plt.ylabel('$Q_M$ % change', fontsize=14)
  plt.tight_layout()
  if ax is None:
    fg.savefig('./ensemblesVariabilityAround2deg_mean.png', dpi=400)


def plotTimeSerie30YVariability_hiLowExt():
  outPng = './ensemblesVariabilityAround2deg_hiLowExt.png'

  fg = plt.figure(figsize=[10, 4.98*3])
  gs = gridspec.GridSpec(3, 1)
  xtxt = 13

  ax1 = plt.subplot(gs[0,0])
  plotTimeSerie30YVariability_hiExt(ax1, plotXLabel=False)
  ylm = plt.ylim()
  ytxt = min(ylm) + (max(ylm) - min(ylm))*.93
  plt.text(xtxt, ytxt, 'a', fontsize=15)

  ax2 = plt.subplot(gs[1,0])
  plotTimeSerie30YVariability_mean(ax1, plotXLabel=False)
  ylm = plt.ylim()
  ytxt = min(ylm) + (max(ylm) - min(ylm))*.93
  plt.text(xtxt, ytxt, 'b', fontsize=15)

  ax3 = plt.subplot(gs[2,0])
  plotTimeSerie30YVariability_lowExt(ax1, plotXLabel=True)
  ylm = plt.ylim()
  ytxt = min(ylm) + (max(ylm) - min(ylm))*.93
  plt.text(xtxt, ytxt, 'c', fontsize=15)

  ax1.set_aspect('auto')
  ax2.set_aspect('auto')
  ax3.set_aspect('auto')

  plt.tight_layout()
  fg.savefig(outPng, dpi=300)


if __name__ == '__main__':
  plotTimeSerie30YVariability_hiLowExt()
 #plotTimeSerie30YVariability_hiExt()
 #plotTimeSerie30YVariability_mean()
  plt.show()
