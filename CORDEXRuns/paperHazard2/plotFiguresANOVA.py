import numpy as np
from scipy import stats
from matplotlib import pyplot as plt
from matplotlib import gridspec, cm
from mpl_toolkits import basemap as bm

import estimateChngSignificanceAndRobustness
import loadWlVsScenChange as ldEnsmbl
import getWarmingLevels as gwl

nmodels = -1


def plotSigma(ax, sigma, mp, txt, txt2='', sigmamax=30):
  if mp == None:
   #llcrnrlon = -11.5
   #llcrnrlat = 23
   #urcrnrlon = 44
   #urcrnrlat = 74
    llcrnrlon = -25
    llcrnrlat = 31
    urcrnrlon = 37
    urcrnrlat = 71.5
    mp = bm.Basemap(llcrnrlon=llcrnrlon, llcrnrlat=llcrnrlat, urcrnrlon=urcrnrlon, 
             urcrnrlat=urcrnrlat, resolution='l', projection='lcc', lon_0=-15, lat_1=-15, lat_2=10)

  lon, lat = estimateChngSignificanceAndRobustness.getLonLat()
  lon, lat = lon.transpose(), lat.transpose()
  x, y = mp(lon, lat)

  plt.axes(ax)
  mp.drawcoastlines(linewidth=.25)
  mp.fillcontinents(color=[.95, .95, .95], lake_color=[.95, .95, .95], zorder=0)

  absSigma = np.abs(sigma)
  pcl = mp.scatter(x.flatten(), y.flatten(), .07, c=absSigma.flatten(), cmap='Oranges', alpha=1, vmin=0, vmax=sigmamax)

  txtpos = mp(-21, 69.5)
  plt.annotate(txt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=13)

  if txt2 != '':
    txtpos = mp(-17, 67.5)
    plt.annotate(txt2, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=14, weight='bold')

  return pcl, mp



  

def plotPvalue(ax, pValue, mp, txt):
  if mp == None:
    llcrnrlon = -25
    llcrnrlat = 31
    urcrnrlon = 37
    urcrnrlat = 71.5
    mp = bm.Basemap(llcrnrlon=llcrnrlon, llcrnrlat=llcrnrlat, urcrnrlon=urcrnrlon, 
             urcrnrlat=urcrnrlat, resolution='l', projection='lcc', lon_0=-15, lat_1=-15, lat_2=10)

  lon, lat = estimateChngSignificanceAndRobustness.getLonLat()
  lon, lat = lon.transpose(), lat.transpose()
  x, y = mp(lon, lat)

  plt.axes(ax)
  mp.drawcoastlines(linewidth=.25)
  mp.fillcontinents(color=[.95, .95, .95], lake_color=[.95, .95, .95], zorder=0)

  cnd = ~np.isnan(pValue)
  x_ = x[cnd]
  y_ = y[cnd]
  pval_ = pValue[cnd]

 #cmap = 'autumn_r'
 #pcl = mp.scatter(x_, y_, .07, c=sgn_, cmap=cmap, alpha=1, vmin=0, vmax=1)

  signClr = 'red'
  cnd = pval_ <= .05
  prc = float(np.sum(cnd))/len(cnd)*100.
  scSgn = mp.scatter(x_[cnd], y_[cnd], .07, c=signClr, alpha=1, label='p-value $\leq$ 0.05 ({prc:1.1f}% of pts)'.format(prc=prc))

  nonSignClr = 'lightgreen'
  cnd = pval_ > .05
  scNonSgn = mp.scatter(x_[cnd], y_[cnd], .07, c=nonSignClr, alpha=1, label='p-value $>$ 0.05')

 #txtpos = mp(-21, 69.5)
  txtpos = mp(-21, 32)
  plt.annotate(txt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=13)

  plt.legend(markerscale=10, loc='upper left', fontsize=9)

  return scNonSgn, scSgn, mp


def anovaAnalysis(relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all):
  sigmaTot = np.nanstd(np.concatenate([rc_r8all, rc_r4all], 0), 0)
  sigmaWithin = np.nanstd(np.concatenate([rc_r8all-rc_r8, rc_r4all-rc_r4]), 0)  
  sigmaBetween = relChngDiff/2.

  nScen = 2
  nModel = rc_r8all.shape[0]
  N = nScen*nModel

  freedomDegBetween = nScen - 1
  freedomDegWithin = N - nScen
  freedomDegTotal = N - 1

  meanSquareBetween = sigmaBetween**2./freedomDegBetween
  meanSquareWithin = sigmaWithin**2./freedomDegWithin

  fValue = meanSquareBetween/meanSquareWithin

  # comparing the pvalue from the F-distribution
  pValue = stats.f.sf(fValue, freedomDegBetween, freedomDegWithin)
  effectSize = sigmaBetween**2./sigmaTot**2.
  
  return sigmaTot, sigmaWithin, sigmaBetween, pValue, effectSize


def printAnovaStats(sigmaTot, sigmaWithin, sigmaBetween):
  sw = np.nanmean(sigmaWithin**2/sigmaTot**2 *100.)
  sb = np.nanmean(sigmaBetween**2/sigmaTot**2 *100.)
  print('  sigma_within: ' + str(sw) + '%')
  print('  sigma_between: ' + str(sb) + '%')



def plotFigureANOVA(varType='extHigh', ncDir='/ClimateRun4/multi-hazard/eva'):
 #varType can be extHigh, extLow, mean
 
  outPng = 'anova_' + varType + '.png'


  f = plt.figure(figsize=(9,12))
  gs = gridspec.GridSpec(3, 3, width_ratios=[1,1,.05])

  mp = None


  #### at 1.5 ####
  warmingLev = 1.5

  if varType == 'mean':
    relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all = ldEnsmbl.loadMeanChangesAtWl(ncDir=ncDir, warmingLev=warmingLev, nmodels=nmodels)
    descrTxt = 'Means'
    sigmaMax = 25
  elif varType == 'extHigh':
    relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all = ldEnsmbl.loadWlVsScenChange(ncDir=ncDir, warmingLev=warmingLev, nmodels=nmodels, rlVarName='rl', retPer=100, shapeParamNcVarName='shape_fit')
    descrTxt = 'High extremes'
    sigmaMax = 30
  elif varType == 'extLow':
    relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all = ldEnsmbl.loadWlVsScenChange(ncDir=ncDir, warmingLev=warmingLev, nmodels=nmodels, rlVarName='rl_min', retPer=15, threshold=.1, shapeParamNcVarName='')
    descrTxt = 'Low extremes'
    sigmaMax = 50

  sigmaTot, sigmaWithin, sigmaBetween, pValue, effectSize = anovaAnalysis(relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all)
  printAnovaStats(sigmaTot, sigmaWithin, sigmaBetween)

  ax00 = plt.subplot(gs[0, 0])
  plt00, mp = plotSigma(ax00, sigmaWithin*100, mp, 'a: $\sigma_{within}, 1.5^\circ C$', txt2=descrTxt, sigmamax=sigmaMax)  
  ax10 = plt.subplot(gs[1, 0])
  plt10, mp = plotSigma(ax10, sigmaBetween*100, mp, 'c: $\sigma_{between}, 1.5^\circ C$', sigmamax=sigmaMax)  
  ax20 = plt.subplot(gs[2, 0])
  _, _, mp = plotPvalue(ax20, pValue, mp, 'e: p-val of interpathway diff.')


  #### at 2.0 ####
  warmingLev = 2.0

  if varType == 'mean':
    relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all = ldEnsmbl.loadMeanChangesAtWl(ncDir=ncDir, warmingLev=warmingLev, nmodels=nmodels)
  elif varType == 'extHigh':
    relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all = ldEnsmbl.loadWlVsScenChange(ncDir=ncDir, warmingLev=warmingLev, nmodels=nmodels, rlVarName='rl', retPer=100)
  elif varType == 'extLow':
    relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all = ldEnsmbl.loadWlVsScenChange(ncDir=ncDir, warmingLev=warmingLev, nmodels=nmodels, rlVarName='rl_min', retPer=15, threshold=.1)

  sigmaTot, sigmaWithin, sigmaBetween, pValue, effectSize = anovaAnalysis(relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all)
  printAnovaStats(sigmaTot, sigmaWithin, sigmaBetween)

  ax01 = plt.subplot(gs[0, 1])
  plt01, mp = plotSigma(ax01, sigmaWithin*100, mp, 'b: $\sigma_{within}, 2.0^\circ C$', sigmamax=sigmaMax)  
  ax11 = plt.subplot(gs[1, 1])
  plt11, mp = plotSigma(ax11, sigmaBetween*100, mp, 'd: $\sigma_{between}, 2.0^\circ C$', sigmamax=sigmaMax)  
  ax21 = plt.subplot(gs[2, 1])
  _, _, mp = plotPvalue(ax21, pValue, mp, 'f: p-val of interpathway diff.')


  cax = plt.subplot(gs[:2, 2])
  cb = plt.colorbar(plt01, ax=ax01, cax=cax)
  cb.set_label('$\sigma$ (%)')

  ax00.set_aspect('auto')  
  ax10.set_aspect('auto')  
  ax20.set_aspect('auto')  
  ax01.set_aspect('auto')  
  ax11.set_aspect('auto')  
  ax21.set_aspect('auto')  
  cax.set_aspect('auto')  

  plt.tight_layout()

  f.savefig(outPng, dpi=300)



def plotEnglandPoints():
  outPng = 'englandPoints_ANOVA.png'

  warmingLev = 2.0

  relChngDiffMean, rc_r8_mean, rc_r4_mean, rc_r8all_mean, rc_r4all_mean = ldEnsmbl.loadMeanChangesAtWl(ncDir=ncDir, warmingLev=warmingLev, nmodels=nmodels)
  _, _, _, pValueMean, _ = anovaAnalysis(relChngDiffMean, rc_r8_mean, rc_r4_mean, rc_r8all_mean, rc_r4all_mean)

  relChngDiffExt, rc_r8_ext, rc_r4_ext, rc_r8all_ext, rc_r4all_ext = ldEnsmbl.loadWlVsScenChange(ncDir=ncDir, warmingLev=warmingLev, nmodels=nmodels, rlVarName='rl', retPer=100)
  _, _, _, pValueExt, _ = anovaAnalysis(relChngDiffMean, rc_r8_mean, rc_r4_mean, rc_r8all_mean, rc_r4all_mean)

  dslonlat = netCDF4.Dataset('lonlat.nc')
  lon = dslonlat.variables['lon'][:].transpose()
  lat = dslonlat.variables['lat'][:].transpose()
  dslonlat.close()

  cndlonlat = np.logical_and(lon < 2, lat > 50)
  cndlonlatMtx = np.tile(cndlonlat, [rc_r8all_mean.shape[0], 1, 1])
  
  cndpval = pValueMean <= .05
  cndpvalMtx = np.tile(pvalcnd, [rc_r8all_mean.shape[0], 1, 1])
  
  cnd = np.logical_and(cndpvalMtx, cndlonlatMtx)
  rc_r8all_mean[~cnd] = np.nan
  rc_r4all_mean[~cnd] = np.nan
  shp = rc_r4all_mean.shape
  rc_r8_ = rc_r8all_mean.reshape([shp[0], shp[1]*shp[2]])
  rc_r4_ = rc_r4all_mean.reshape([shp[0], shp[1]*shp[2]])
  mn_r8_mean = np.nanmean(rc_r8_, 1)*100
  mn_r4_mean = np.nanmean(rc_r4_, 1)*100
  
  rc_r8all_ext[~cnd] = np.nan
  rc_r4all_ext[~cnd] = np.nan
  shp = rc_r4all_ext.shape
  rc_r8_ = rc_r8all_ext.reshape([shp[0], shp[1]*shp[2]])
  rc_r4_ = rc_r4all_ext.reshape([shp[0], shp[1]*shp[2]])
  mn_r8_ext = np.nanmean(rc_r8_, 1)*100
  mn_r4_ext = np.nanmean(rc_r4_, 1)*100

  f = plt.figure(figsize=(7,3))
  gs = gridspec.GridSpec(1, 2)

  vv = np.concatenate([mn_r4_mean, mn_r8_mean, mn_r4_ext, mn_r8_ext], axis=0)
  ylm = [np.min(vv) - 1, np.max(vv) + 1]

  ax0 = plt.subplot(gs[0])
  ones = np.ones(mn_r8_mean.shape)
  plt.plot(ones/3., mn_r4_mean, 'o', color='green', label='RCP4.5')
  plt.plot(ones*2./3., mn_r8_mean, 'o', color='navy', label='RCP8.5')
  plt.xlim([0, 1])
  plt.ylim(ylm)
  plt.ylabel('projected change at $2^\circ C$ (%)')
  plt.xticks([])
  plt.legend(loc='lower right')
  plt.text(.05, 17, 'a: mean dis.', fontsize=11)
  plt.grid('on')

  ax1 = plt.subplot(gs[1])
  ones = np.ones(mn_r8_ext.shape)
  plt.plot(ones/3., mn_r4_ext, 'o', color='green', label='RCP4.5')
  plt.plot(ones*2./3., mn_r8_ext, 'o', color='navy', label='RCP8.5')
  plt.xlim([0, 1])
  plt.ylim(ylm)
  ax1.set_yticklabels('')
  plt.xticks([])
  plt.text(.05, 17, 'b: extreme high dis.', fontsize=11)
  plt.grid('on')

  plt.tight_layout()

  f.savefig(outPng, dpi=300)



if __name__ == '__main__':
  import pdb; pdb.set_trace()
 #plotFigureANOVA(varType='mean')
 #plotFigureANOVA(varType='extHigh')
  plotFigureANOVA(varType='extLow')
 #plotEnglandPoints()
