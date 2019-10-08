import numpy as np
from scipy import stats
from matplotlib import pyplot as plt
from matplotlib import gridspec
from mpl_toolkits import basemap as bm

import estimateChngSignificanceAndRobustness
import loadWlVsScenChange as ldEnsmbl
import getWarmingLevels as gwl



nmodels = -1

def plotRelChngDiff(ax, relChngDiff, mp, txt, cmap='RdBu', vmax=20, vmin=None):
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
 #mp.drawparallels(np.arange(-180, 180, 10), labels=[1,1])
 #mp.drawmeridians(np.arange(-90, 90, 10), labels=[1,1])
 #pcl = mp.pcolor(lon, lat, relChngDiff*100, cmap=cmap)
 #pcl = mp.scatter(lon.flatten(), lat.flatten(), .07, c=relChngDiff.flatten()*100, cmap=cmap, alpha=1)
  pcl = plt.scatter(x.flatten(), y.flatten(), .07, c=relChngDiff.flatten()*100, cmap=cmap, alpha=1)
  vmin = -vmax if vmin is None else vmin
  plt.clim(vmin, vmax)
  print('mean absolute change: ' + str(np.nanmean(np.abs(relChngDiff)*100)) + '%')

  txtpos = mp(-24, 32)
 #txtpos = mp(-22, 69)
  plt.annotate(txt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=13)

  return pcl, mp
  



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
  


def plotSigma(ax, sigma, relChngDiff, mp, txt, sigmamax=30, signSigmaThreshold1=1, signSigmaThreshold2=2, prcTxtTmpl='', printSignTxt=True):
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
 #pcl = mp.pcolor(lon, lat, sigma, cmap='hot_r', vmin=0, vmax=sigmamax)
 #pcl = mp.pcolor(lon, lat, sigma, cmap='Spectral_r', vmin=0, vmax=sigmamax)
 #pcl = mp.pcolor(lon, lat, sigma, cmap='coolwarm', vmin=0, vmax=sigmamax)
 #pcl = mp.pcolor(lon, lat, np.abs(sigma), cmap='RdBu_r', vmin=0, vmax=sigmamax)
 #pcl = mp.pcolor(lon, lat, absSigma, cmap='PuBu_r', vmin=0, vmax=sigmamax)
 #pcl = mp.scatter(lon.flatten(), lat.flatten(), .07, c=absSigma.flatten(), cmap='PuBu_r', alpha=1, vmin=0, vmax=sigmamax)
  pcl = mp.scatter(x.flatten(), y.flatten(), .07, c=absSigma.flatten(), cmap='Oranges', alpha=1, vmin=0, vmax=sigmamax)
 #prcTxtTmpl = '% of pixel where ${thr}\|\Delta Q_{{100-wl}}\| > \sigma_{{im}}$: {p:2.0f}%' if prcTxtTmpl == '' else prcTxtTmpl

  if prcTxtTmpl != '':
    sigma_ratio = sigma/np.abs(relChngDiff)
    percSign = float(np.nansum(sigma_ratio <= signSigmaThreshold1))/np.nansum(np.logical_not(np.isnan(sigma_ratio)))
    thrstr = '{thr:1.0f}'.format(thr=signSigmaThreshold1) if signSigmaThreshold1 != 1 else ''
    prcTxt1 = prcTxtTmpl.format(p=percSign*100, thr=thrstr)
    print(prcTxt1)
  
    percSign = float(np.nansum(sigma_ratio <= signSigmaThreshold2))/np.nansum(np.logical_not(np.isnan(sigma_ratio)))
    thrstr = '{thr:1.0f}\cdot'.format(thr=signSigmaThreshold2) if signSigmaThreshold2 != 1 else ''
    prcTxt2 = prcTxtTmpl.format(p=percSign*100, thr=thrstr)
    print(prcTxt2)
  
   #txtpos = mp(-7, 71)
    txtpos = mp(-24, 32) if printSignTxt else mp(-21, 69.5)
    plt.annotate(txt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=13)
    if printSignTxt:
     #txtpos = mp(-8, 27)
      txtpos = mp(-24.3, 70.3)
      bb = {'boxstyle': 'square,pad=0', 'ec': 'none', 'fc': 'w'}
      plt.annotate(prcTxt1, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=10, bbox=bb)
     #txtpos = mp(-8, 24)
     #txtpos = mp(-24.3, 69.1)
     #plt.annotate(prcTxt2, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=10, bbox=bb)
  else:
    txtpos = mp(-24, 32)
    plt.annotate(txt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=13)

  return pcl, mp
  


def printStatsByScenEnsemble(scen='rcp85', warmingLev=2.0, ncDir='/ClimateRun4/multi-hazard/eva'):
  _, _, sigma_im = estimateChngSignificanceAndRobustness.computeRlChngPValueAtWarmingLev(scen=scen, warmingLev=warmingLev, ncDir=ncDir)
  sigmaT = getTimeSigmaByScen(warmingLev, scen, ncDir)
  sigma2 = sigma_im**2. + sigmaT**2.
  sigma_im_ratio = sigma_im**2./sigma2
  sigmaT_ratio = sigmaT**2./sigma2
  print('% sigma_im**2: ' + str(np.nanmean(sigma_im_ratio)*100))
  print('% sigma_t**2: ' + str(np.nanmean(sigmaT_ratio)*100))
  



def printPosNegChanges(warmingLev, relChngDiff):
  cnd = ~np.isnan(relChngDiff)
  rlchngdf = relChngDiff[cnd]
  prcntPos = float(np.sum(rlchngdf > 0))/np.sum(cnd)*100
  prcntNeg = 100. - prcntPos
  print('  warming lvl = ' + str(warmingLev))
  print('    %positive - %negative = ' + str(prcntPos) + ' - ' + str(prcntNeg))



def printStatsByGrossEnsemble(warmingLev=2.0, ncDir='/ClimateRun4/multi-hazard/eva'):
  relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all = ldEnsmbl.loadWlVsScenChange(warmingLev=warmingLev, ncDir=ncDir)
  rc_mega = (rc_r8 + rc_r4)/2.
  sigma_im = np.nanstd(np.concatenate([rc_r8all, rc_r4all], 0), 0)
  sigmaT = getTimeSigmaGrossEnsemble(warmingLev)
  sigma_rcpdiff = np.abs(relChngDiff)/2.
  sigma_im0 = np.sqrt(sigma_im**2. - sigma_rcpdiff**2.)
  sigma2 = sigma_im**2. + sigmaT**2.
  sigma_im0_ratio = sigma_im0**2./sigma2
  sigmaT_ratio = sigmaT**2./sigma2
  sigma_rcpdiff_ratio = sigma_rcpdiff**2./sigma2
  print('% sigma_im0**2: ' + str(np.nanmean(sigma_im0_ratio)*100))
  print('% sigma_t**2: ' + str(np.nanmean(sigmaT_ratio)*100))
  print('% sigma_rcpdiff**2: ' + str(np.nanmean(sigma_rcpdiff_ratio)*100))
  printPosNegChanges(relChngDiff)
  



def plotGrossEnsembles_highExt(ncDir='/ClimateRun4/multi-hazard/eva'):
  outPng = 'wlRelChngGrossEnsembles_extHigh.png'
  
  f = plt.figure(figsize=(9,12))
  gs = gridspec.GridSpec(3, 3, width_ratios=[1,1,.05])

  mp = None

  def writeSigmaRatioTxt(ax, sigma, relChng, varname):
    sigma_ratio = sigma/np.abs(relChng)
    percSign = float(np.nansum(sigma_ratio <= 1))/np.nansum(np.logical_not(np.isnan(sigma_ratio)))
    prcTxtTmpl = '% of pixel where $\|{varname}\| > \sigma$: {p:2.0f}%'
    prcTxt = prcTxtTmpl.format(varname=varname, p=percSign*100)
    plt.axes(ax)
    txtpos = mp(-24.3, 70.2)
    bb = {'boxstyle': 'square,pad=0', 'ec': 'none', 'fc': 'w'}
    plt.annotate(prcTxt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=10, bbox=bb)

  warmingLev = 1.5

  relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all = ldEnsmbl.loadWlVsScenChange(ncDir=ncDir, warmingLev=warmingLev, nmodels=nmodels)
  rc_mega = (rc_r8 + rc_r4)/2.
  ax0 = plt.subplot(gs[0,0])
  pcl, mp = plotRelChngDiff(ax0, rc_mega, mp, 'a: $\Delta Q_{H100}$ at $' + str(warmingLev) +'^\circ$', vmax=30)
  printPosNegChanges(warmingLev, rc_mega)
  
 #sigma_im = np.nanstd(np.concatenate([rc_r8all, rc_r4all], 0), 0)
 #sigmaT = getTimeSigmaGrossEnsemble(warmingLev, ncDir=ncDir)
 #sigma = np.sqrt(sigma_im**2. + sigmaT**2.)

  sigmaTot, sigmaWithin, sigmaBetween, pValue, effectSize = anovaAnalysis(relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all)
  writeSigmaRatioTxt(ax0, sigmaTot, rc_mega, '\Delta Q_{H100}')

  ax1 = plt.subplot(gs[1,0])
  pcl, mp = plotSigma(ax1, sigmaWithin*100, rc_mega*100, mp, 'c: $\sigma_{within}$ (%) at $' + str(warmingLev) +'^\circ$',
    prcTxtTmpl = '')

  ax2 = plt.subplot(gs[2,0])
  pcl, mp = plotSigma(ax2, sigmaBetween*100, rc_mega*100, mp, 'e: $\sigma_{between}$ (%) at $' + str(warmingLev) +'^\circ$',
    prcTxtTmpl = '')

  warmingLev = 2.0

  relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all = ldEnsmbl.loadWlVsScenChange(ncDir=ncDir, warmingLev=warmingLev, nmodels=nmodels)
  rc_mega = (rc_r8 + rc_r4)/2.
  ax3 = plt.subplot(gs[0,1])
  pclChng, mp = plotRelChngDiff(ax3, rc_mega, mp, 'b: $\Delta Q_{H100}$ at $' + str(warmingLev) +'^\circ$', vmax=30)
  printPosNegChanges(warmingLev, rc_mega)

  sigmaTot, sigmaWithin, sigmaBetween, pValue, effectSize = anovaAnalysis(relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all)
  writeSigmaRatioTxt(ax3, sigmaTot, rc_mega, '\Delta Q_{H100}')

  ax4 = plt.subplot(gs[1,1])
  pclSigma, mp = plotSigma(ax4, sigmaWithin*100, rc_mega*100, mp, 'd: $\sigma_{within}$ (%) at $' + str(warmingLev) +'^\circ$',
    prcTxtTmpl = '')

  ax5 = plt.subplot(gs[2,1])
  pclSigma, mp = plotSigma(ax5, sigmaBetween*100, rc_mega*100, mp, 'f: $\sigma_{between}$ (%) at $' + str(warmingLev) +'^\circ$',
    prcTxtTmpl = '')
  
  cax1 = plt.subplot(gs[0,2])
  cb = plt.colorbar(pclChng, ax=ax2, cax=cax1)
  cb.set_label('$\Delta Q_{H100}$ (%)')
  
  cax2 = plt.subplot(gs[1:,2])
  cb = plt.colorbar(pclSigma, ax=ax3, cax=cax2)
  cb.set_label('$\sigma_{H100}$ (%)')

  ax0.set_aspect('auto')
  ax1.set_aspect('auto')
  ax2.set_aspect('auto')
  ax3.set_aspect('auto')
  ax4.set_aspect('auto')
  ax5.set_aspect('auto')
  cax1.set_aspect('auto')
  cax2.set_aspect('auto')

  plt.tight_layout()

  f.savefig(outPng, dpi=300)
  
  


def plotGrossEnsembles_mean(ncDir='/ClimateRun4/multi-hazard/eva'):
  outPng = 'wlRelChngGrossEnsembles_mean.png'
  
  f = plt.figure(figsize=(9,12))
  gs = gridspec.GridSpec(3, 3, width_ratios=[1,1,.05])

  mp = None

  def writeSigmaRatioTxt(ax, sigma, relChng, varname):
    sigma_ratio = sigma/np.abs(relChng)
    percSign = float(np.nansum(sigma_ratio <= 1))/np.nansum(np.logical_not(np.isnan(sigma_ratio)))
    prcTxtTmpl = '% of pixel where $\|{varname}\| > \sigma$: {p:2.0f}%'
    prcTxt = prcTxtTmpl.format(varname=varname, p=percSign*100)
    plt.axes(ax)
    txtpos = mp(-24.3, 70.2)
    bb = {'boxstyle': 'square,pad=0', 'ec': 'none', 'fc': 'w'}
    plt.annotate(prcTxt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=10, bbox=bb)

  warmingLev = 1.5

  relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all = ldEnsmbl.loadMeanChangesAtWl(ncDir=ncDir, warmingLev=warmingLev, nmodels=nmodels)
  rc_mega = (rc_r8 + rc_r4)/2.
  ax0 = plt.subplot(gs[0,0])
  pcl, mp = plotRelChngDiff(ax0, rc_mega, mp, 'a: $\Delta Q_M$ at $' + str(warmingLev) +'^\circ$', vmax=25)
  printPosNegChanges(warmingLev, rc_mega)

  sigmaTot, sigmaWithin, sigmaBetween, pValue, effectSize = anovaAnalysis(relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all)
  writeSigmaRatioTxt(ax0, sigmaTot, rc_mega, '\Delta Q_M')

  ax1 = plt.subplot(gs[1,0])
  pcl, mp = plotSigma(ax1, sigmaWithin*100, rc_mega*100, mp, 'c: $\sigma_{within}$ (%) at $' + str(warmingLev) +'^\circ$',
    prcTxtTmpl = '', sigmamax=25)

  ax2 = plt.subplot(gs[2,0])
  pcl, mp = plotSigma(ax2, sigmaBetween*100, rc_mega*100, mp, 'e: $\sigma_{between}$ (%) at $' + str(warmingLev) +'^\circ$',
    prcTxtTmpl = '', sigmamax=25)

  warmingLev = 2.0

  relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all = ldEnsmbl.loadMeanChangesAtWl(ncDir=ncDir, warmingLev=warmingLev, nmodels=nmodels)
  rc_mega = (rc_r8 + rc_r4)/2.
  ax3 = plt.subplot(gs[0,1])
  pclChng, mp = plotRelChngDiff(ax3, rc_mega, mp, 'b: $\Delta Q_M$ at $' + str(warmingLev) +'^\circ$', vmax=30)
  printPosNegChanges(warmingLev, rc_mega)
  
  sigmaTot, sigmaWithin, sigmaBetween, pValue, effectSize = anovaAnalysis(relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all)
  writeSigmaRatioTxt(ax3, sigmaTot, rc_mega, '\Delta Q_M')

  ax4 = plt.subplot(gs[1,1])
  pclSigma, mp = plotSigma(ax4, sigmaWithin*100, rc_mega*100, mp, 'd: $\sigma_{within}$ (%) at $' + str(warmingLev) +'^\circ$',
    prcTxtTmpl = '', sigmamax=30)

  ax5 = plt.subplot(gs[2,1])
  pclSigma, mp = plotSigma(ax5, sigmaBetween*100, rc_mega*100, mp, 'f: $\sigma_{between}$ (%) at $' + str(warmingLev) +'^\circ$',
    prcTxtTmpl = '', sigmamax=30)
  
  cax1 = plt.subplot(gs[0,2])
  cb = plt.colorbar(pclChng, ax=ax2, cax=cax1)
  cb.set_label('$\Delta Q_M$ (%)')
  
  cax2 = plt.subplot(gs[1:,2])
  cb = plt.colorbar(pclSigma, ax=ax3, cax=cax2)
  cb.set_label('$\sigma_M$ (%)')

  ax0.set_aspect('auto')
  ax1.set_aspect('auto')
  ax2.set_aspect('auto')
  ax3.set_aspect('auto')
  ax4.set_aspect('auto')
  ax5.set_aspect('auto')
  cax1.set_aspect('auto')
  cax2.set_aspect('auto')

  plt.tight_layout()

  f.savefig(outPng, dpi=300)



def plotGrossEnsembles_lowExt(ncDir='/ClimateRun4/multi-hazard/eva'):
  outPng = 'wlRelChngGrossEnsembles_extLow.png'
  
  f = plt.figure(figsize=(9,12))
  gs = gridspec.GridSpec(3, 3, width_ratios=[1,1,.05])

  mp = None

  def writeSigmaRatioTxt(ax, sigma, relChng, varname):
    sigma_ratio = sigma/np.abs(relChng)
    percSign = float(np.nansum(sigma_ratio <= 1))/np.nansum(np.logical_not(np.isnan(sigma_ratio)))
    prcTxtTmpl = '% of pixel where $\|{varname}\| > \sigma$: {p:2.0f}%'
    prcTxt = prcTxtTmpl.format(varname=varname, p=percSign*100)
   #prcTxt = '% of pixel where $\|\Delta ' + varname + '\| > \sigma$: {p:2.0f}%'.format(p=percSign*100)
    plt.axes(ax)
    txtpos = mp(-24.3, 70.3)
    bb = {'boxstyle': 'square,pad=0', 'ec': 'none', 'fc': 'w'}
    plt.annotate(prcTxt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=10, bbox=bb)

  warmingLev = 1.5

  retPer = 15
  rlVarName = 'rl_min'
  relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all = ldEnsmbl.loadWlVsScenChange(ncDir=ncDir, 
      warmingLev=warmingLev, rlVarName=rlVarName, retPer=retPer,
      nmodels=nmodels, threshold=.1)
  rc_mega = (rc_r8 + rc_r4)/2.
  ax0 = plt.subplot(gs[0,0])
  pcl, mp = plotRelChngDiff(ax0, rc_mega, mp, 'a: $\Delta Q_{L15}$ at $' + str(warmingLev) +'^\circ$', vmax=50)
  printPosNegChanges(warmingLev, rc_mega)

  sigmaTot, sigmaWithin, sigmaBetween, pValue, effectSize = anovaAnalysis(relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all)
  writeSigmaRatioTxt(ax0, sigmaTot, rc_mega, '\Delta Q_{L15}')

  ax1 = plt.subplot(gs[1,0])
  pcl, mp = plotSigma(ax1, sigmaWithin*100, rc_mega*100, mp, 'c: $\sigma_{within}$ (%) at $' + str(warmingLev) +'^\circ$',
    prcTxtTmpl = '', sigmamax=50)

  ax2 = plt.subplot(gs[2,0])
  pcl, mp = plotSigma(ax2, sigmaBetween*100, rc_mega*100, mp, 'e: $\sigma_{between}$ (%) at $' + str(warmingLev) +'^\circ$',
    prcTxtTmpl = '', sigmamax=50)

  warmingLev = 2.0

  relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all = ldEnsmbl.loadWlVsScenChange(ncDir=ncDir, 
      warmingLev=warmingLev, rlVarName=rlVarName, retPer=retPer,
      nmodels=nmodels, threshold=.1)
  rc_mega = (rc_r8 + rc_r4)/2.
  ax3 = plt.subplot(gs[0,1])
  pclChng, mp = plotRelChngDiff(ax3, rc_mega, mp, 'b: $\Delta Q_{{L15}}$ at $' + str(warmingLev) +'^\circ$', vmax=50)
  printPosNegChanges(warmingLev, rc_mega)
  
  sigmaTot, sigmaWithin, sigmaBetween, pValue, effectSize = anovaAnalysis(relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all)
  writeSigmaRatioTxt(ax3, sigmaTot, rc_mega, '\Delta Q_{L15}')

  ax4 = plt.subplot(gs[1,1])
  pclSigma, mp = plotSigma(ax4, sigmaWithin*100, rc_mega*100, mp, 'd: $\sigma_{within}$ (%) at $' + str(warmingLev) +'^\circ$',
    prcTxtTmpl = '', sigmamax=50)

  ax5 = plt.subplot(gs[2,1])
  pclSigma, mp = plotSigma(ax5, sigmaBetween*100, rc_mega*100, mp, 'f: $\sigma_{between}$ (%) at $' + str(warmingLev) +'^\circ$',
    prcTxtTmpl = '', sigmamax=50)
  
  cax1 = plt.subplot(gs[0,2])
  cb = plt.colorbar(pclChng, ax=ax2, cax=cax1)
  cb.set_label('$\Delta Q_{L15}$ (%)')
  
  cax2 = plt.subplot(gs[1:,2])
  cb = plt.colorbar(pclSigma, ax=ax3, cax=cax2)
  cb.set_label('$\sigma_{L15}$ (%)')

  ax0.set_aspect('auto')
  ax1.set_aspect('auto')
  ax2.set_aspect('auto')
  ax3.set_aspect('auto')
  ax4.set_aspect('auto')
  ax5.set_aspect('auto')
  cax1.set_aspect('auto')
  cax2.set_aspect('auto')

  plt.tight_layout()

  f.savefig(outPng, dpi=300)



if __name__ == '__main__':
  import pdb; pdb.set_trace()
 #plotGrossEnsembles_highExt()
 #plotGrossEnsembles_lowExt()
  plotGrossEnsembles_mean()
 #plotGrossEnsembleChange()
 #plotGrossEnsembles(ncDir='/ClimateRun/menta/eva_50y_timeWindow/')
 #printStatsByScenEnsemble('rcp85', 1.5)
 #printStatsByScenEnsemble('rcp85', 1.5, ncDir='/ClimateRun/menta/eva_50y_timeWindow/')
 #printStatsByGrossEnsemble(1.5)
 #printStatsByGrossEnsemble(1.5, ncDir='/ClimateRun/menta/eva_50y_timeWindow/')
 #plotErrorDecomposition()
 #plotErrorDecomposition(ncDir='/ClimateRun/menta/eva_50y_timeWindow/')
  plt.show()
