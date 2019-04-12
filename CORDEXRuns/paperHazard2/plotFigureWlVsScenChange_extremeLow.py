import numpy as np
from matplotlib import pyplot as plt
from matplotlib import gridspec
from mpl_toolkits import basemap as bm

import estimateChngSignificanceAndRobustness
import loadWlVsScenChange as ldEnsmbl
import getWarmingLevels as gwl

from scipy.ndimage.filters import gaussian_filter


def plotRelChngDiff(ax, relChngDiff, mp, txt, cmap='RdBu', vmax=20, vmin=None):
  if mp == None:
   #llcrnrlon = -11.5
   #llcrnrlat = 23
   #urcrnrlon = 44
   #urcrnrlat = 74

    llcrnrlon = -25
    llcrnrlat = 25
    urcrnrlon = 44
    urcrnrlat = 71.5

   #mp = bm.Basemap(llcrnrlon=llcrnrlon, llcrnrlat=llcrnrlat, urcrnrlon=urcrnrlon, 
   #         urcrnrlat=urcrnrlat, resolution='l')
    mp = bm.Basemap(llcrnrlon=llcrnrlon, llcrnrlat=llcrnrlat, urcrnrlon=urcrnrlon, 
             urcrnrlat=urcrnrlat, resolution='l', projection='lcc', lon_0=-15, lat_1=-15, lat_2=10)

  lon, lat = estimateChngSignificanceAndRobustness.getLonLat()
  lon, lat = lon.transpose(), lat.transpose()

  plt.axes(ax)
  mp.drawcoastlines(linewidth=.25)
  mp.fillcontinents(color=[.95, .95, .95], lake_color=[.95, .95, .95], zorder=0)
 #mp.drawparallels(np.arange(-180, 180, 10), labels=[1,1])
 #mp.drawmeridians(np.arange(-90, 90, 10), labels=[1,1])
 # pcl = mp.pcolor(lon, lat, relChngDiff*100, cmap=cmap)
  x, y = mp(lon, lat)
  sc = plt.scatter(x, y, s=1, c=relChngDiff*100, linewidth=0, cmap=cmap)
  vmin = -vmax if vmin is None else vmin
  plt.clim(vmin, vmax)
  print('mean absolute change: ' + str(np.nanmean(np.abs(relChngDiff)*100)) + '%')

  txtpos = mp(-20, 69)
  plt.annotate(txt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=13)

  return sc, mp




def plotPvalue(ax, pValue, relChngDiff, mp, txt):
  if mp == None:
   #llcrnrlon = -11.5
   #llcrnrlat = 23
   #urcrnrlon = 44
   #urcrnrlat = 74

    llcrnrlon = -25
    llcrnrlat = 25
    urcrnrlon = 44
    urcrnrlat = 71.5

   #mp = bm.Basemap(llcrnrlon=llcrnrlon, llcrnrlat=llcrnrlat, urcrnrlon=urcrnrlon, 
   #         urcrnrlat=urcrnrlat, resolution='l')
    mp = bm.Basemap(llcrnrlon=llcrnrlon, llcrnrlat=llcrnrlat, urcrnrlon=urcrnrlon, 
             urcrnrlat=urcrnrlat, resolution='l', projection='lcc', lon_0=-15, lat_1=-15, lat_2=10)

  lon, lat = estimateChngSignificanceAndRobustness.getLonLat()
  lon, lat = lon.transpose(), lat.transpose()

  plt.axes(ax)
  mp.drawcoastlines(linewidth=.25)

  pvl_ = pValue.copy()
  pvl_[pvl_ > .5] = np.nan
 #pcl = mp.pcolor(lon, lat, pvl_, cmap='hot', vmin=0, vmax=.5)
  x, y = mp(lon, lat)
  sc = plt.scatter(x, y, s=1, c=pvl_, linewidth=0, cmap='hot')

  txtpos = mp(-7, 27)
  plt.annotate(txt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=13)

  return sc, mp

  

def plotSigma(ax, sigma, relChngDiff, mp, txt, sigmamax=2, signSigmaThreshold1=1, signSigmaThreshold2=2, prcTxtTmpl='', printSignTxt=True):
  if mp == None:
   #llcrnrlon = -11.5
   #llcrnrlat = 23
   #urcrnrlon = 44
   #urcrnrlat = 74

    llcrnrlon = -25
    llcrnrlat = 25
    urcrnrlon = 44
    urcrnrlat = 71.5

   #mp = bm.Basemap(llcrnrlon=llcrnrlon, llcrnrlat=llcrnrlat, urcrnrlon=urcrnrlon, 
   #         urcrnrlat=urcrnrlat, resolution='l')
    mp = bm.Basemap(llcrnrlon=llcrnrlon, llcrnrlat=llcrnrlat, urcrnrlon=urcrnrlon, 
             urcrnrlat=urcrnrlat, resolution='l', projection='lcc', lon_0=-15, lat_1=-15, lat_2=10)

  lon, lat = estimateChngSignificanceAndRobustness.getLonLat()
  lon, lat = lon.transpose(), lat.transpose()

  plt.axes(ax)
  mp.drawcoastlines(linewidth=.25)
  mp.fillcontinents(color=[.8, .8, .8], lake_color=[.8, .8, .8], zorder=0)

  absSigma = np.abs(sigma)
 #pcl = mp.pcolor(lon, lat, sigma, cmap='hot_r', vmin=0, vmax=sigmamax)
 #pcl = mp.pcolor(lon, lat, sigma, cmap='Spectral_r', vmin=0, vmax=sigmamax)
 #pcl = mp.pcolor(lon, lat, sigma, cmap='coolwarm', vmin=0, vmax=sigmamax)
 #pcl = mp.pcolor(lon, lat, np.abs(sigma), cmap='RdBu_r', vmin=0, vmax=sigmamax)
 #pcl = mp.pcolor(lon, lat, absSigma, cmap='PuBu_r', vmin=0, vmax=sigmamax)
  x, y = mp(lon, lat)
 #sc = plt.scatter(x, y, s=1, c=absSigma, linewidth=0, cmap='PuBu_r')
  absSigma[absSigma > 1.75] = 1.75
  sc = plt.scatter(x, y, s=1, c=absSigma, linewidth=0, cmap='PuBu_r', vmin=0, vmax=sigmamax)
  prcTxtTmpl = '% of pixel where ${thr}\|\Delta d_{{100-wl}}\| > \sigma_{{im}}$: {p:2.2f}%' if prcTxtTmpl == '' else prcTxtTmpl

  percSign = float(np.nansum(absSigma <= signSigmaThreshold1))/np.nansum(np.logical_not(np.isnan(absSigma)))
  thrstr = '{thr:1.0f}'.format(thr=signSigmaThreshold1) if signSigmaThreshold1 != 1 else ''
  prcTxt1 = prcTxtTmpl.format(p=percSign*100, thr=thrstr)
  print(prcTxt1)

  percSign = float(np.nansum(absSigma <= signSigmaThreshold2))/np.nansum(np.logical_not(np.isnan(absSigma)))
  thrstr = '{thr:1.0f}\cdot'.format(thr=signSigmaThreshold2) if signSigmaThreshold2 != 1 else ''
  prcTxt2 = prcTxtTmpl.format(p=percSign*100, thr=thrstr)
  print(prcTxt2)

  txtpos = mp(-20, 69)
  plt.annotate(txt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=13)
  if printSignTxt:
    txtpos = mp(-20, 27)
    plt.annotate(prcTxt1, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=10)

  return sc, mp
  

def printStatsByScenEnsemble(scen='rcp85', warmingLev=2.0):
  _, _, sigma_im = estimateChngSignificanceAndRobustness.computeRlChngPValueAtWarmingLev(scen=scen, warmingLev=warmingLev)
  sigmaT = getTimeSigmaByScen(warmingLev, scen)
  sigma2 = sigma_im**2. + sigmaT**2.
  sigma_im_ratio = sigma_im**2./sigma2
  sigmaT_ratio = sigmaT**2./sigma2
  print('% sigma_im**2: ' + str(np.nanmean(sigma_im_ratio)*100))
  print('% sigma_t**2: ' + str(np.nanmean(sigmaT_ratio)*100))



def nanGaussianBlur(U, sigma):
  V = U.copy()
  V[np.isnan(U)] = 0
  VV = gaussian_filter(V, sigma=sigma)

  W = np.ones(V.shape)
  W[np.isnan(U)] = 0
  WW = gaussian_filter(W, sigma=sigma)
  blrd = VV/WW
  blrd[np.isnan(U)] = np.nan
  return blrd
  


def plotScenVsScen(warmingLev=2.0):
  # DON'T USE THIS, USE plotScenVsScen2

  outPng = 'wlRelChngScenVsScen_lowDis_wl' + str(warmingLev) + '.png'

  f = plt.figure(figsize=(13, 8))
  gs = gridspec.GridSpec(2, 4, width_ratios=[1,1,1,1./12.])

  mp = None
  blurSigma = 1

  relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all = ldEnsmbl.loadWlVsScenChange(warmingLev=warmingLev, rlVarName='rl_min', threshold=.0001, retPer=15)
  relChngDiff = nanGaussianBlur(relChngDiff, blurSigma)
  rc_r8 = nanGaussianBlur(rc_r8, blurSigma)
  rc_r4 = nanGaussianBlur(rc_r4, blurSigma)

  ax0 = plt.subplot(gs[0,0])
  cmap = 'bwr_r'
  pcl, mp = plotRelChngDiff(ax0, rc_r8, mp, 'a: RCP85 - hist., w.l. $' + str(warmingLev) +'^\circ$', vmax=60, cmap=cmap)
  ax1 = plt.subplot(gs[0,1])
  pcl, mp = plotRelChngDiff(ax1, rc_r4, mp, 'b: RCP45 - hist., w.l. $' + str(warmingLev) +'^\circ$', vmax=60, cmap=cmap)
  ax2 = plt.subplot(gs[0,2])
  pcl, mp = plotRelChngDiff(ax2, relChngDiff, mp, 'c: $\Delta RCP85 - \Delta RCP45$', vmax=60, cmap=cmap)
  cax = plt.subplot(gs[0,3])
  cb = plt.colorbar(pcl, ax=ax2, cax=cax)
  cb.set_label('$\Delta$ 15-y low discharge (%)')
  ax0.set_aspect('auto')
  ax1.set_aspect('auto')
  ax2.set_aspect('auto')
  cax.set_aspect('auto')

  ax0 = plt.subplot(gs[1,0])
  pValue, _, sigma_im = estimateChngSignificanceAndRobustness.computeRlChngPValueAtWarmingLev(scen='rcp85', warmingLev=warmingLev, rlVarName='rl_min', rlErrVarName='se_rl_min', retPer=10)
  std = sigma_im/np.abs(rc_r8)
  std = nanGaussianBlur(std, blurSigma)
 #pcl, mp = plotPvalue(ax0, pValue, None, mp, 'd: p-value, $\Delta rcp85$')
  pcl, mp = plotSigma(ax0, std, None, mp, 'd: $\sigma_{im}$, ratio of $\Delta RCP85$', sigmamax=2.)
  ax1 = plt.subplot(gs[1,1])
  pValue, _, sigma_im = estimateChngSignificanceAndRobustness.computeRlChngPValueAtWarmingLev(scen='rcp45', warmingLev=warmingLev, rlVarName='rl_min', rlErrVarName='se_rl_min', retPer=10)
  std = sigma_im/np.abs(rc_r4)
  std = nanGaussianBlur(std, blurSigma)
 #pcl, mp = plotPvalue(ax1, pValue, None, mp, 'e: p-value, $\Delta rcp45$')
  pcl, mp = plotSigma(ax1, std, None, mp, 'e: $\sigma_{im}$, ratio of $\Delta RCP45$', sigmamax=2)
  ax2 = plt.subplot(gs[1,2])  
 #pValue, _, _ = estimateChngSignificanceAndRobustness.computeRlChngPValueAtWarmingLevBtwScen(warmingLev=warmingLev)
 #pcl, mp = plotPvalue(ax2, pValue, relChngDiff, mp, 'f: p-value, $\Delta RCP85 - \Delta RCP45$')
  std = np.std(rc_r8all-rc_r4all, 0)
  std = std/np.abs(rc_r8)
  std = nanGaussianBlur(std, blurSigma)
  pcl, mp = plotSigma(ax2, std, relChngDiff, mp, 'f: $\sigma_{im}$, $\Delta RCP85 - \Delta RCP45$', sigmamax=2, printSignTxt=False)
  cax = plt.subplot(gs[1,3])
  cb = plt.colorbar(pcl, ax=ax2, cax=cax)
 #cb.set_label('p-value')
  cb.set_label('$\sigma_{im}$ (fraction of relative change)')
  ax0.set_aspect('auto')
  ax1.set_aspect('auto')
  ax2.set_aspect('auto')
  cax.set_aspect('auto')

  plt.tight_layout()

  f.savefig(outPng, dpi=300)

  


def plotScenVsScen2(warmingLev=2.0):

  outPng = 'wlRelChngScenVsScen_lowDis_wl' + str(warmingLev) + '.png'

  f = plt.figure(figsize=(13, 8))
  gs = gridspec.GridSpec(2, 4, width_ratios=[1,1,1,1./12.])

  mp = None
 #blurSigma = 2

  relChngDiff, rc_r8, rc_r4, std_r8, std_r4, std_diff, pvl_r8, pvl_r4, pvl_diff = ldEnsmbl.loadWlVsScenChange2(
       warmingLev=warmingLev, rlVarName='rl_min', threshold=.0001, retPer=15)
 #relChngDiff = nanGaussianBlur(relChngDiff, blurSigma)
 #rc_r8 = nanGaussianBlur(rc_r8, blurSigma)
 #rc_r4 = nanGaussianBlur(rc_r4, blurSigma)

  ax0 = plt.subplot(gs[0,0])
  cmap = 'bwr_r'
 #cmap = 'RdBu'
  pcl, mp = plotRelChngDiff(ax0, rc_r8, mp, 'a: RCP85 - hist., w.l. $' + str(warmingLev) +'^\circ$', vmax=60, cmap=cmap)
  ax1 = plt.subplot(gs[0,1])
  pcl, mp = plotRelChngDiff(ax1, rc_r4, mp, 'b: RCP45 - hist., w.l. $' + str(warmingLev) +'^\circ$', vmax=60, cmap=cmap)
  ax2 = plt.subplot(gs[0,2])
  pcl, mp = plotRelChngDiff(ax2, relChngDiff, mp, 'c: $\Delta RCP85 - \Delta RCP45$', vmax=60, cmap=cmap)
  cax = plt.subplot(gs[0,3])
  cb = plt.colorbar(pcl, ax=ax2, cax=cax)
  cb.set_label('$\Delta$ 15-y low discharge (%)')
  ax0.set_aspect('auto')
  ax1.set_aspect('auto')
  ax2.set_aspect('auto')
  cax.set_aspect('auto')

  ax0 = plt.subplot(gs[1,0])
  std = std_r8/np.abs(rc_r8)
  pcl, mp = plotSigma(ax0, std, None, mp, 'd: $\sigma_{im}$, ratio of $\Delta RCP85$', sigmamax=2.)
 #pcl, mp = plotPvalue(ax0, pvl_r8, relChngDiff, mp, 'test')
  ax1 = plt.subplot(gs[1,1])
  std = std_r4/np.abs(rc_r4)
  pcl, mp = plotSigma(ax1, std, None, mp, 'e: $\sigma_{im}$, ratio of $\Delta RCP45$', sigmamax=2)
  ax2 = plt.subplot(gs[1,2])  
  std = std_diff/np.abs(rc_r8)
  pcl, mp = plotSigma(ax2, std, relChngDiff, mp, 'f: $\sigma_{im}$, $\Delta RCP85 - \Delta RCP45$', sigmamax=2, printSignTxt=False)
  cax = plt.subplot(gs[1,3])
  cb = plt.colorbar(pcl, ax=ax2, cax=cax)
  cb.set_label('$\sigma_{im}$ (fraction of relative change)')
  ax0.set_aspect('auto')
  ax1.set_aspect('auto')
  ax2.set_aspect('auto')
  cax.set_aspect('auto')

  plt.tight_layout()

  f.savefig(outPng, dpi=300)


if __name__ == '__main__':
  plotScenVsScen2(2.0)
 #plotScenVsScenAll()
 #plotGrossEnsembles()
 #printStatsByScenEnsemble('rcp85', 1.5)
 #printStatsByGrossEnsemble(2.0)
  plt.show()
