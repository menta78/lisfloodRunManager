import numpy as np
from scipy import stats
from scipy.interpolate import interp1d
from matplotlib import pyplot as plt
from matplotlib import gridspec

import loadWlVsScenChange
from getWarmingLevels import getWarmingLevels

nmodels = -1
axFontSize = 14
#excludedModels = ['IPSL-INERIS-WRF331F_BC']
excludedModels = []


#def getNYrsTimeSeriesAroundWl(years, timeSeries, warmingLevelYears, models, halfWindowSize=3):
#  yrsRel = np.arange(-15, 16, 5)
#  yrsRel_ = np.arange(-20, 21, 5)
#  tsshp = timeSeries.shape
#  outTs = np.zeros([tsshp[0], halfWindowSize*2+1, tsshp[2], tsshp[3]])*np.nan
#  for mdl, imdl in zip(models, range(len(models))):
#    ywl = warmingLevelYears[mdl]
#    yrs = yrsRel + ywl
#    # rounding to 5 years
#    ywl_ = np.round(ywl/5.)*5
#    yrs_ = ywl_ + yrsRel_
#    iywl = np.where(years == ywl_)[0][0]
#    vls_ = timeSeries[imdl, iywl-halfWindowSize-1:iywl+halfWindowSize+2]
#    vls = interp1d(yrs_, vls_, axis=0)(yrs)
#    outTs[imdl, :] = vls
#  return outTs

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
  srs_ = srs[:, yindx, :, :]
  srs_[srs_ == np.inf] = np.nan
  srsMean = np.nanmean(srs_, 0)
  srsSigma = np.std(srs_, 0)
  return srsMean, srsSigma


def plotTimeSerie30YVariability_hiExt(ax=None, plotXLabel=True, plotYLabel=True, warmingLev=2.0):
  yrs, rpR8Srs, rpR4Srs, models = loadWlVsScenChange.loadRetPerAllYears(nmodels=nmodels, excludedModels=excludedModels)
  rpR8 = getRelChng(yrs, rpR8Srs)
  rpR4 = getRelChng(yrs, rpR4Srs)

  wlyR8 = getWarmingLevels('rcp85', warmingLev)
  r8srs = getNYrsTimeSeriesAroundWl(yrs, rpR8, wlyR8, models)
  r8meanWl, r8sigmaWl = getMeanAndSigma(r8srs)
  cndSignR8 = np.abs(r8meanWl) > r8sigmaWl
  cndPosi = r8meanWl > 0
 #cnd = np.logical_and(cndSignR8, cndPosi)
  cnd = cndPosi
  cndMtx = np.tile(cnd, [r8srs.shape[0], r8srs.shape[1], 1, 1])
  r8srs[~cndMtx] = np.nan
  r8mean_ = np.nanmean(r8srs, 0)
  r8mean = r8mean_.reshape(r8mean_.shape[0], r8mean_.shape[1]*r8mean_.shape[2])
  r8mean = np.nanmedian(r8mean, 1)
 #r8mean = np.nanmean(r8mean, 1)

  r8spmean = r8srs.reshape(r8srs.shape[0], r8srs.shape[1], r8srs.shape[2]*r8srs.shape[3])
  r8spmean = np.nanmean(r8spmean, 2)
 #r8spmean = np.nanmean(r8spmean, 2)
  r8skew = stats.skew(r8spmean[:, 3])
  r8sigma = np.std(r8spmean[:, 3])
  r8mean = np.nanmean(r8spmean, 0)

  wlyR4 = getWarmingLevels('rcp45', warmingLev)
  r4srs = getNYrsTimeSeriesAroundWl(yrs, rpR4, wlyR4, models)
  r4meanWl, r4sigmaWl = getMeanAndSigma(r4srs)
  cndSignR4 = np.abs(r4meanWl) > r4sigmaWl
  cndPosi = r4meanWl > 0
  cnd = cndPosi
  cndMtx = np.tile(cnd, [r4srs.shape[0], r4srs.shape[1], 1, 1])
  r4srs[~cndMtx] = np.nan
  r4mean_ = np.nanmean(r4srs, 0)
  r4mean = r4mean_.reshape(r4mean_.shape[0], r4mean_.shape[1]*r4mean_.shape[2])
  r4mean = np.nanmedian(r4mean, 1)
 #r4mean = np.nanmean(r4mean, 1)

  r4spmean = r4srs.reshape(r4srs.shape[0], r4srs.shape[1], r4srs.shape[2]*r4srs.shape[3])
  r4spmean = np.nanmean(r4spmean, 2)
 #r4spmean = np.nanmean(r4spmean, 2)
  r4skew = stats.skew(r4spmean[:, 3])
  r4sigma = np.std(r4spmean[:, 3])
  r4mean = np.nanmean(r4spmean, 0)

  yr = [-15, -10, -5, 0, 5, 10, 15]
  if ax is None:
    fg = plt.figure(figsize=[8.46, 4.98])
 #pmdlr8 = plt.plot(yr, r8spmean.transpose()*100, 'peachpuff', label='RCP8.5 models ($\sigma={sgm:1.2f}\%, skw.={s:1.2f}$)'.format(sgm=r8sigma*100, s=r8skew)); 
 #pmdlr4 = plt.plot(yr, r4spmean.transpose()*100, 'skyblue', label='RCP4.5 models ($\sigma={sgm:1.2f}\%, skw.={s:1.2f})$'.format(sgm=r4sigma*100, s=r4skew)); 
  pmdlr8 = plt.plot(yr, r8spmean.transpose()*100, 'peachpuff', label='RCP8.5 models ($\sigma={sgm:1.2f}\%$'.format(sgm=r8sigma*100, s=r8skew)); 
  pmdlr4 = plt.plot(yr, r4spmean.transpose()*100, 'skyblue', label='RCP4.5 models ($\sigma={sgm:1.2f}\%$'.format(sgm=r4sigma*100, s=r4skew)); 
  pmedr8 = plt.plot(yr, r8mean*100, 'firebrick', linewidth=6, label='RCP8.5 mean'); 
  pmedr4 = plt.plot(yr, r4mean*100, 'royalblue', linewidth=6, label='RCP4.5 mean'); 
  plt.grid('on')
  plt.legend(handles=[pmdlr8[0], pmedr8[0], pmdlr4[0], pmedr4[0]], fontsize=12, loc=2)
  if plotXLabel:
    plt.xlabel('years to $' + str(warmingLev) + '^\circ$C w.l.', fontsize=18)
  else:
    ax.set_xticklabels([])
  if plotYLabel:
    plt.ylabel('$Q_{H100}$ % change', fontsize=17)
  else:
    ax.set_yticklabels([])
  ax.tick_params(axis="x", labelsize=axFontSize)
  ax.tick_params(axis="y", labelsize=axFontSize)
  plt.tight_layout()
  if ax is None:
    fg.savefig('./ensemblesVariabilityAround2deg.png', dpi=400)


def plotTimeSerie30YVariability_lowExt(ax=None, plotXLabel=True, plotYLabel=True, warmingLev=2.0):
  yrs, rpR8Srs, rpR4Srs, models = loadWlVsScenChange.loadRetPerAllYears(rlVarName='rl_min', nmodels=nmodels, excludedModels=excludedModels)
  rpR8 = getRelChng(yrs, rpR8Srs)
  rpR4 = getRelChng(yrs, rpR4Srs)

  wlyR8 = getWarmingLevels('rcp85', warmingLev)
  r8srs = getNYrsTimeSeriesAroundWl(yrs, rpR8, wlyR8, models)
  r8srs[r8srs == np.inf] = np.nan
  r8meanWl, r8sigmaWl = getMeanAndSigma(r8srs)
  cndSignR8 = np.abs(r8meanWl) > r8sigmaWl
  cndPosi = r8meanWl > 0
 #cnd = np.logical_and(cndSignR8, cndPosi)
  cnd = cndPosi
  cndMtx = np.tile(cnd, [r8srs.shape[0], r8srs.shape[1], 1, 1])
  r8srs[~cndMtx] = np.nan
  r8mean_ = np.nanmean(r8srs, 0)
  r8mean = r8mean_.reshape(r8mean_.shape[0], r8mean_.shape[1]*r8mean_.shape[2])
  r8mean = np.nanmedian(r8mean, 1)
 #r8mean = np.nanmean(r8mean, 1)

  r8spmean = r8srs.reshape(r8srs.shape[0], r8srs.shape[1], r8srs.shape[2]*r8srs.shape[3])
  r8spmean = np.nanmedian(r8spmean, 2)
 #r8spmean = np.nanmean(r8spmean, 2)
  r8skew = stats.skew(r8spmean[:, 3])
  r8sigma = np.std(r8spmean[:, 3])
  r8mean = np.nanmean(r8spmean, 0)

  wlyR4 = getWarmingLevels('rcp45', warmingLev)
  r4srs = getNYrsTimeSeriesAroundWl(yrs, rpR4, wlyR4, models)
  r4srs[r4srs == np.inf] = np.nan
  r4meanWl, r4sigmaWl = getMeanAndSigma(r4srs)
  cndSignR4 = np.abs(r4meanWl) > r4sigmaWl
  cndPosi = r4meanWl > 0
 #cnd = np.logical_and(cndSignR4, cndPosi)
  cnd = cndPosi
  cndMtx = np.tile(cnd, [r4srs.shape[0], r4srs.shape[1], 1, 1])
  r4srs[~cndMtx] = np.nan
  r4mean_ = np.nanmean(r4srs, 0)
  r4mean = r4mean_.reshape(r4mean_.shape[0], r4mean_.shape[1]*r4mean_.shape[2])
  r4mean = np.nanmedian(r4mean, 1)
 #r4mean = np.nanmean(r4mean, 1)

  r4spmean = r4srs.reshape(r4srs.shape[0], r4srs.shape[1], r4srs.shape[2]*r4srs.shape[3])
  r4spmean = np.nanmedian(r4spmean, 2)
 #r4spmean = np.nanmean(r4spmean, 2)
  r4skew = stats.skew(r4spmean[:, 3])
  r4sigma = np.std(r4spmean[:, 3])
  r4mean = np.nanmean(r4spmean, 0)

  yr = [-15, -10, -5, 0, 5, 10, 15]
  if ax is None:
    fg = plt.figure(figsize=[8.46, 4.98])
 #pmdlr8 = plt.plot(yr, r8spmean.transpose()*100, 'peachpuff', label='RCP8.5 models ($\sigma={sgm:1.2f}\%, skw.={s:1.2f}$)'.format(sgm=r8sigma*100, s=r8skew)); 
 #pmdlr4 = plt.plot(yr, r4spmean.transpose()*100, 'skyblue', label='RCP4.5 models ($\sigma={sgm:1.2f}\%, skw.={s:1.2f}$)'.format(sgm=r4sigma*100, s=r4skew)); 
  pmdlr8 = plt.plot(yr, r8spmean.transpose()*100, 'peachpuff', label='RCP8.5 models ($\sigma={sgm:1.2f}\%$)'.format(sgm=r8sigma*100, s=r8skew)); 
  pmdlr4 = plt.plot(yr, r4spmean.transpose()*100, 'skyblue', label='RCP4.5 models ($\sigma={sgm:1.2f}\%$)'.format(sgm=r4sigma*100, s=r4skew)); 
  pmedr8 = plt.plot(yr, r8mean*100, 'firebrick', linewidth=6, label='RCP8.5 mean'); 
  pmedr4 = plt.plot(yr, r4mean*100, 'royalblue', linewidth=6, label='RCP4.5 mean'); 
  plt.grid('on')
  plt.legend(handles=[pmdlr8[0], pmedr8[0], pmdlr4[0], pmedr4[0]], fontsize=12, loc=2)
  if plotXLabel:
    plt.xlabel('years to $' + str(warmingLev) + '^\circ$C w.l.', fontsize=18)
  else:
    ax.set_xticklabels([])
  if plotYLabel:
    plt.ylabel('$Q_{L15}$ % change', fontsize=17)
  else:
    ax.set_yticklabels([])
  ax.tick_params(axis="x", labelsize=axFontSize)
  ax.tick_params(axis="y", labelsize=axFontSize)
  plt.tight_layout()
  if ax is None:
    fg.savefig('./ensemblesVariabilityAround2deg_lowExt.png', dpi=400)


def plotTimeSerie30YVariability_mean(ax=None, plotXLabel=True, plotYLabel=True, warmingLev=2.0):
  _, _, _, r8srs, r4srs = loadWlVsScenChange.loadMeanChangesAtWl_nYearsAroundWLYear(warmingLev=warmingLev, nmodels=nmodels, excludedModels=excludedModels)

  r8meanWl, r8sigmaWl = getMeanAndSigma(r8srs)
  cndSignR8 = np.abs(r8meanWl) > r8sigmaWl
  cndPosi = r8meanWl > 0
 #cnd = np.logical_and(cndSignR8, cndPosi)
  cnd = cndPosi
  cndMtx = np.tile(cnd, [r8srs.shape[0], r8srs.shape[1], 1, 1])
  r8srs[~cndMtx] = np.nan
  r8mean_ = np.nanmean(r8srs, 0)
  r8mean = r8mean_.reshape(r8mean_.shape[0], r8mean_.shape[1]*r8mean_.shape[2])
  r8mean = np.nanmedian(r8mean, 1)
 #r8mean = np.nanmean(r8mean, 1)

  r8spmean = r8srs.reshape(r8srs.shape[0], r8srs.shape[1], r8srs.shape[2]*r8srs.shape[3])
  r8spmean = np.nanmean(r8spmean, 2)
  r8skew = stats.skew(r8spmean[:, 3])
  r8sigma = np.std(r8spmean[:, 3])
  r8mean = np.nanmean(r8spmean, 0)

  r4meanWl, r4sigmaWl = getMeanAndSigma(r4srs)
  cndSignR4 = np.abs(r4meanWl) > r4sigmaWl
  cndPosi = r4meanWl > 0
 #cnd = np.logical_and(cndSignR4, cndPosi)
  cnd = cndPosi
  cndMtx = np.tile(cnd, [r4srs.shape[0], r4srs.shape[1], 1, 1])
  r4srs[~cndMtx] = np.nan
  r4mean_ = np.nanmean(r4srs, 0)
  r4mean = r4mean_.reshape(r4mean_.shape[0], r4mean_.shape[1]*r4mean_.shape[2])
  r4mean = np.nanmedian(r4mean, 1)
 #r4mean = np.nanmean(r4mean, 1)

  r4spmean = r4srs.reshape(r4srs.shape[0], r4srs.shape[1], r4srs.shape[2]*r4srs.shape[3])
  r4spmean = np.nanmean(r4spmean, 2)
  r4skew = stats.skew(r4spmean[:, 3])
  r4sigma = np.std(r4spmean[:, 3])
  r4mean = np.nanmean(r4spmean, 0)

  yr = [-15, -10, -5, 0, 5, 10, 15]
  if ax is None:
    fg = plt.figure(figsize=[8.46, 4.98])
 #pmdlr8 = plt.plot(yr, r8spmean.transpose()*100, 'peachpuff', label='RCP8.5 models ($\sigma={sgm:1.2f}\%, skw.={s:1.2f}$)'.format(sgm=r8sigma*100, s=r8skew)); 
 #pmdlr4 = plt.plot(yr, r4spmean.transpose()*100, 'skyblue', label='RCP4.5 models ($\sigma={sgm:1.2f}\%, skw.={s:1.2f}$)'.format(sgm=r4sigma*100, s=r4skew)); 
  pmdlr8 = plt.plot(yr, r8spmean.transpose()*100, 'peachpuff', label='RCP8.5 models ($\sigma={sgm:1.2f}\%$)'.format(sgm=r8sigma*100, s=r8skew)); 
  pmdlr4 = plt.plot(yr, r4spmean.transpose()*100, 'skyblue', label='RCP4.5 models ($\sigma={sgm:1.2f}\%$)'.format(sgm=r4sigma*100, s=r4skew)); 
  pmedr8 = plt.plot(yr, r8mean*100, 'firebrick', linewidth=6, label='RCP8.5 mean'); 
  pmedr4 = plt.plot(yr, r4mean*100, 'royalblue', linewidth=6, label='RCP4.5 mean'); 
  plt.grid('on')
  plt.legend(handles=[pmdlr8[0], pmedr8[0], pmdlr4[0], pmedr4[0]], fontsize=12, loc=2)
  if plotXLabel:
    plt.xlabel('years to $' + str(warmingLev) + '^\circ$C w.l.', fontsize=18)
  else:
    ax.set_xticklabels([])
  if plotYLabel:
    plt.ylabel('$Q_M$ % change', fontsize=17)
  else:
    ax.set_yticklabels([])
  ax.tick_params(axis="x", labelsize=axFontSize)
  ax.tick_params(axis="y", labelsize=axFontSize)
  plt.tight_layout()
  if ax is None:
    fg.savefig('./ensemblesVariabilityAround2deg_mean.png', dpi=400)


def plotTimeSerie30YVariability_hiLowExt(warmingLev=2.0):
  outPng = './ensemblesVariabilityAround2deg_hiLowExt_' + str(warmingLev) + '.png'

  fg = plt.figure(figsize=[10, 4.98*3])
  gs = gridspec.GridSpec(3, 1)
  xtxt = 13

  ax1 = plt.subplot(gs[0,0])
  plotTimeSerie30YVariability_hiExt(ax1, plotXLabel=False, warmingLev=warmingLev)
  ylm = plt.ylim()
  ytxt = min(ylm) + (max(ylm) - min(ylm))*.93
  plt.text(xtxt, ytxt, 'a', fontsize=17)

  ax2 = plt.subplot(gs[1,0])
  plotTimeSerie30YVariability_mean(ax2, plotXLabel=False, warmingLev=warmingLev)
  ylm = plt.ylim()
  ytxt = min(ylm) + (max(ylm) - min(ylm))*.93
  plt.text(xtxt, ytxt, 'b', fontsize=17)

  ax3 = plt.subplot(gs[2,0])
  plotTimeSerie30YVariability_lowExt(ax3, plotXLabel=True, warmingLev=warmingLev)
  ylm = plt.ylim()
  ytxt = min(ylm) + (max(ylm) - min(ylm))*.93
  plt.text(xtxt, ytxt, 'c', fontsize=17)

 #ax1.set_aspect('auto')
 #ax2.set_aspect('auto')
  ax3.set_aspect('auto')

  plt.tight_layout()
  fg.savefig(outPng, dpi=300)


def plotTimeSerie30YVariability_hiLowExt_bothWarmLev():
  outPng = './ensemblesVariability_hiLowExt.png'

  fg = plt.figure(figsize=[20, 4.98*3])
  gs = gridspec.GridSpec(3, 2)
  xtxt = 6

  warmingLev = 1.5
  ax1 = plt.subplot(gs[0,0])
  plotTimeSerie30YVariability_hiExt(ax1, plotXLabel=False, warmingLev=warmingLev)
  ylm = plt.ylim([-2, 45])
  ytxt = min(ylm) + (max(ylm) - min(ylm))*.9
  plt.text(xtxt, ytxt, 'a: $\Delta Q_{H100}$ at $1.5^\circ$ C', fontsize=19)

  ax2 = plt.subplot(gs[1,0])
  plotTimeSerie30YVariability_mean(ax2, plotXLabel=False, warmingLev=warmingLev)
  ylm = plt.ylim([-2, 50])
  ytxt = min(ylm) + (max(ylm) - min(ylm))*.9
  plt.text(xtxt, ytxt, 'c: $\Delta Q_M$ at $1.5^\circ$ C', fontsize=19)

  ax3 = plt.subplot(gs[2,0])
  plotTimeSerie30YVariability_lowExt(ax3, plotXLabel=True, warmingLev=warmingLev)
  ylm = plt.ylim([-15, 90])
  ytxt = min(ylm) + (max(ylm) - min(ylm))*.9
  plt.text(xtxt, ytxt, 'e: $\Delta Q_{L15}$ at $1.5^\circ$ C', fontsize=19)

  warmingLev = 2.0
  ax4 = plt.subplot(gs[0,1])
  plotTimeSerie30YVariability_hiExt(ax4, plotXLabel=False, plotYLabel=False, warmingLev=warmingLev)
  ylm = plt.ylim([-2, 45])
  ytxt = min(ylm) + (max(ylm) - min(ylm))*.9
  plt.text(xtxt, ytxt, 'b: $\Delta Q_{H100}$ at $2.0^\circ$ C', fontsize=19)

  ax5 = plt.subplot(gs[1,1])
  plotTimeSerie30YVariability_mean(ax5, plotXLabel=False, plotYLabel=False, warmingLev=warmingLev)
  ylm = plt.ylim([-2, 50])
  ytxt = min(ylm) + (max(ylm) - min(ylm))*.9
  plt.text(xtxt, ytxt, 'b: $\Delta Q_M$ at $2.0^\circ$ C', fontsize=19)

  ax6 = plt.subplot(gs[2,1])
  plotTimeSerie30YVariability_lowExt(ax6, plotXLabel=True, plotYLabel=False, warmingLev=warmingLev)
  ylm = plt.ylim([-15, 90])
  ytxt = min(ylm) + (max(ylm) - min(ylm))*.9
  plt.text(xtxt, ytxt, 'f: $\Delta Q_{L15}$ at $2.0^\circ$ C', fontsize=19)

 #ax1.set_aspect('auto')
 #ax2.set_aspect('auto')
  ax3.set_aspect('auto')

  plt.tight_layout()
  fg.savefig(outPng, dpi=300)


if __name__ == '__main__':
  plotTimeSerie30YVariability_hiLowExt(warmingLev=1.5)
 #plotTimeSerie30YVariability_hiLowExt(warmingLev=2.0)
 #plotTimeSerie30YVariability_hiLowExt_bothWarmLev()
 #plotTimeSerie30YVariability_hiExt()
 #plotTimeSerie30YVariability_mean()
  plt.show()
