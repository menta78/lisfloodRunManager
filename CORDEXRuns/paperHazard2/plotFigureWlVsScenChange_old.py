import numpy as np
from matplotlib import pyplot as plt
from matplotlib import gridspec
from mpl_toolkits import basemap as bm

import estimateChngSignificanceAndRobustness
import loadWlVsScenChange as ldEnsmbl
import getWarmingLevels as gwl


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
    llcrnrlon = -11.5
    llcrnrlat = 23
    urcrnrlon = 44
    urcrnrlat = 74
    mp = bm.Basemap(llcrnrlon=llcrnrlon, llcrnrlat=llcrnrlat, urcrnrlon=urcrnrlon, 
             urcrnrlat=urcrnrlat, resolution='l')

  lon, lat = estimateChngSignificanceAndRobustness.getLonLat()
  lon, lat = lon.transpose(), lat.transpose()

  plt.axes(ax)
  mp.drawcoastlines(linewidth=.25)

  pvl_ = pValue.copy()
  pvl_[pvl_ > .5] = np.nan
 #pvl_[relChngDiff <= 0] = pvl_[relChngDiff <= 0] - 1
 #pvl_[relChngDiff > 0] = 1 - pvl_[relChngDiff > 0]
 #pcl = mp.pcolor(lon, lat, pvl_, cmap='Spectral')
 #pcl = mp.pcolor(lon, lat, pvl_, cmap='hot', vmin=0, vmax=.5)

  txtpos = mp(-7, 27)
  plt.annotate(txt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=13)

  return pcl, mp
  

def plotSigma(ax, sigma, relChngDiff, mp, txt, sigmamax=2, signSigmaThreshold1=1, signSigmaThreshold2=2, prcTxtTmpl='', printSignTxt=True):
  if mp == None:
    llcrnrlon = -11.5
    llcrnrlat = 23
    urcrnrlon = 44
    urcrnrlat = 74
    mp = bm.Basemap(llcrnrlon=llcrnrlon, llcrnrlat=llcrnrlat, urcrnrlon=urcrnrlon, 
             urcrnrlat=urcrnrlat, resolution='l')

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
  sc = plt.scatter(x, y, s=1, c=absSigma, linewidth=0, cmap='PuBu_r', vmax=sigmamax)
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


def plotFigureWlVsScenChange():
  outPng = 'wlRelChngScenVsScen.png'

  f = plt.figure(figsize=(8.5, 12))
  gs = gridspec.GridSpec(3, 3, width_ratios=[1,1,.5/8.5])

  mp = None

  ax0 = plt.subplot(gs[0,0])
  relChngDiff, _ = ldEnsmbl.loadWlVsScenChange(warmingLev=1.5)
  pcl, mp = plotRelChngDiff(ax0, relChngDiff, mp, 'a: $\Delta RCP85 - \Delta RCP45$, w.l. $1.5^\circ$')

  ax = plt.subplot(gs[0,1])
  relChngDiff, _ = ldEnsmbl.loadWlVsScenChange(warmingLev=2)
  pcl, mp = plotRelChngDiff(ax, relChngDiff, mp, 'b: $\Delta RCP85 - \Delta RCP45$, w.l. $2.0^\circ$')

  cax = plt.subplot(gs[0,2])
  cb = plt.colorbar(pcl, ax=ax, cax=cax)
  cb.set_label('$\Delta RCP85 - \Delta RCP45$ (%)')
  ax0.set_aspect('auto')
  ax.set_aspect('auto')
  cax.set_aspect('auto')


  ax0 = plt.subplot(gs[1,0])  
  pValue, agrMdlCnt15, std15 = estimateChngSignificanceAndRobustness.computeRlChngPValueAtWarmingLevBtwScen(warmingLev=1.5)
  pcl, mp = plotPvalue(ax0, pValue, relChngDiff, mp, 'c: p-value, w.l. $1.5^\circ$')

  ax = plt.subplot(gs[1,1])  
  pValue, agrMdlCnt20, std20 = estimateChngSignificanceAndRobustness.computeRlChngPValueAtWarmingLevBtwScen(warmingLev=2)
  pcl, mp = plotPvalue(ax, pValue, relChngDiff, mp, 'd: p-value. w.l. $2.0^\circ$')

  cax = plt.subplot(gs[1,2])
  cb = plt.colorbar(pcl, ax=ax, cax=cax)
  cb.set_label('p-value')
  ax0.set_aspect('auto')
  ax.set_aspect('auto')
  cax.set_aspect('auto')


  ax0 = plt.subplot(gs[2,0])  
  pcl, mp = plotAgreeingMdlCnt(ax0, agrMdlCnt15, mp, 'e: agr. mdl. count $1.5^\circ$')

  ax = plt.subplot(gs[2,1])  
  pcl, mp = plotAgreeingMdlCnt(ax, agrMdlCnt20, mp, 'f: agr. mdl.c ount $2.0^\circ$')

  cax = plt.subplot(gs[2,2])
  cb = plt.colorbar(pcl, ax=ax, cax=cax)
  cb.set_label('agreeing mdl. count')
  ax0.set_aspect('auto')
  ax.set_aspect('auto')
  cax.set_aspect('auto')


  plt.tight_layout()

  f.savefig(outPng, dpi=300)
  
  

def getTimeSigmaByScen(warmingLev, scen):
  _, pdfR8, pdfR4 = gwl.getWarmingLevelMixDistributions(warmingLev)
  pdf = None
  if scen == 'rcp85':
    pdf = pdfR8
  elif scen == 'rcp45':
    pdf = pdfR4
  
  
  stdev = pdf.std()
  mn = pdf.mean()
  sdvmin = int(np.round(mn - stdev))
  sdvmax = int(np.round(mn + stdev))

  rlChngInf = ldEnsmbl.getRcpEnsembleAtYear(sdvmin, scen=scen)
  rlChngSup = ldEnsmbl.getRcpEnsembleAtYear(sdvmax, scen=scen)

  sigmaT = np.abs(rlChngSup-rlChngInf)
  return sigmaT


def getTimeSigmaGrossEnsemble(warmingLev):
  pdfTot, pdfR8, pdfR4 = gwl.getWarmingLevelMixDistributions(warmingLev)
  
  stdev = pdfTot.std()
  mn = pdfTot.mean()
  sdvmin = int(np.round(mn - stdev))
  sdvmax = int(np.round(mn + stdev))

  rlChngInf = ldEnsmbl.getGrossEnsembleAtYear(sdvmin)
  rlChngSup = ldEnsmbl.getGrossEnsembleAtYear(sdvmax)

  sigmaT = np.abs(rlChngSup-rlChngInf)
  return sigmaT
  

def printStatsByScenEnsemble(scen='rcp85', warmingLev=2.0):
  _, _, sigma_im = estimateChngSignificanceAndRobustness.computeRlChngPValueAtWarmingLev(scen=scen, warmingLev=warmingLev)
  sigmaT = getTimeSigmaByScen(warmingLev, scen)
  sigma2 = sigma_im**2. + sigmaT**2.
  sigma_im_ratio = sigma_im**2./sigma2
  sigmaT_ratio = sigmaT**2./sigma2
  print('% sigma_im**2: ' + str(np.nanmean(sigma_im_ratio)*100))
  print('% sigma_t**2: ' + str(np.nanmean(sigmaT_ratio)*100))
  

def printStatsByGrossEnsemble(warmingLev=2.0):
  relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all = ldEnsmbl.loadWlVsScenChange(warmingLev=warmingLev)
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
  


def plotGrossEnsembles():
    

  outPng = 'wlRelChngGrossEnsembles.png'
  
  f = plt.figure(figsize=(9,8))
  gs = gridspec.GridSpec(2, 3, width_ratios=[1,1,.05])

  mp = None

  warmingLev = 1.5

  relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all = ldEnsmbl.loadWlVsScenChange(warmingLev=warmingLev)
  rc_mega = (rc_r8 + rc_r4)/2.
  ax0 = plt.subplot(gs[0,0])
  pcl, mp = plotRelChngDiff(ax0, rc_mega, mp, 'a: rcp all, rel. chng. at $' + str(warmingLev) +'^\circ$', vmax=30)
  
  sigma_im = np.nanstd(np.concatenate([rc_r8all, rc_r4all], 0), 0)
  sigmaT = getTimeSigmaGrossEnsemble(warmingLev)
  sigma = np.sqrt(sigma_im**2. + sigmaT**2.)
  sigma_ratio = sigma/rc_mega
  ax1 = plt.subplot(gs[1,0])
  pcl, mp = plotSigma(ax1, sigma_ratio, None, mp, 'c: $\sigma$, % of rel. chng. at $' + str(warmingLev) +'^\circ$', sigmamax=2,
    prcTxtTmpl = '% of pixel where ${thr}\|\Delta d_{{100-wl}}\| > \sigma$: {p:2.2f}%')

  warmingLev = 2.0

  relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all = ldEnsmbl.loadWlVsScenChange(warmingLev=warmingLev)
  rc_mega = (rc_r8 + rc_r4)/2.
  ax2 = plt.subplot(gs[0,1])
  pclChng, mp = plotRelChngDiff(ax2, rc_mega, mp, 'b: rcp all, rel. chng. at $' + str(warmingLev) +'^\circ$', vmax=30)
  
  sigma_im = np.nanstd(np.concatenate([rc_r8all, rc_r4all], 0), 0)
  sigmaT = getTimeSigmaGrossEnsemble(warmingLev)
  sigma = np.sqrt(sigma_im**2. + sigmaT**2.)
  sigma_ratio = sigma/rc_mega
  ax3 = plt.subplot(gs[1,1])
  pclSigma, mp = plotSigma(ax3, sigma_ratio, None, mp, 'd: $\sigma$, % of rel. chng. at $' + str(warmingLev) +'^\circ$', sigmamax=2,
    prcTxtTmpl = '% of pixel where ${thr}\|\Delta d_{{100-wl}}\| > \sigma$: {p:2.2f}%')
  
  cax1 = plt.subplot(gs[0,2])
  cb = plt.colorbar(pclChng, ax=ax2, cax=cax1)
  cb.set_label('$\Delta$ 100-y discharge (%)')
  
  cax2 = plt.subplot(gs[1,2])
  cb = plt.colorbar(pclSigma, ax=ax3, cax=cax2)
  cb.set_label('$\sigma$ (fraction of relative change)')

  ax0.set_aspect('auto')
  ax1.set_aspect('auto')
  ax2.set_aspect('auto')
  ax3.set_aspect('auto')
  cax1.set_aspect('auto')
  cax2.set_aspect('auto')

  plt.tight_layout()

  f.savefig(outPng, dpi=300)



def plotScenVsScen(warmingLev=2.0):

  outPng = 'wlRelChngScenVsScen_wl' + str(warmingLev) + '.png'

  f = plt.figure(figsize=(13, 8))
  gs = gridspec.GridSpec(2, 4, width_ratios=[1,1,1,1./12.])

  mp = None

  relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all = ldEnsmbl.loadWlVsScenChange(warmingLev=warmingLev)
  ax0 = plt.subplot(gs[0,0])
  cmap = 'bwr_r'
  pcl, mp = plotRelChngDiff(ax0, rc_r8, mp, 'a: RCP85 - hist., w.l. $' + str(warmingLev) +'^\circ$', vmax=30, cmap=cmap)
  ax1 = plt.subplot(gs[0,1])
  pcl, mp = plotRelChngDiff(ax1, rc_r4, mp, 'b: RCP45 - hist., w.l. $' + str(warmingLev) +'^\circ$', vmax=30, cmap=cmap)
  ax2 = plt.subplot(gs[0,2])
  pcl, mp = plotRelChngDiff(ax2, relChngDiff, mp, 'c: $\Delta RCP85 - \Delta RCP45$', vmax=30, cmap=cmap)
  cax = plt.subplot(gs[0,3])
  cb = plt.colorbar(pcl, ax=ax2, cax=cax)
  cb.set_label('$\Delta$ 100-y discharge (%)')
  ax0.set_aspect('auto')
  ax1.set_aspect('auto')
  ax2.set_aspect('auto')
  cax.set_aspect('auto')

  ax0 = plt.subplot(gs[1,0])
  pValue, _, sigma_im = estimateChngSignificanceAndRobustness.computeRlChngPValueAtWarmingLev(scen='rcp85', warmingLev=warmingLev)
  std = sigma_im/np.abs(rc_r8)
 #pcl, mp = plotPvalue(ax0, pValue, None, mp, 'd: p-value, $\Delta rcp85$')
  pcl, mp = plotSigma(ax0, std, None, mp, 'd: $\sigma_{im}$, ratio of $\Delta RCP85$', sigmamax=2.)
  ax1 = plt.subplot(gs[1,1])
  pValue, _, sigma_im = estimateChngSignificanceAndRobustness.computeRlChngPValueAtWarmingLev(scen='rcp45', warmingLev=warmingLev)
  std = sigma_im/np.abs(rc_r4)
 #pcl, mp = plotPvalue(ax1, pValue, None, mp, 'e: p-value, $\Delta rcp45$')
  pcl, mp = plotSigma(ax1, std, None, mp, 'e: $\sigma_{im}$, ratio of $\Delta RCP45$', sigmamax=2)
  ax2 = plt.subplot(gs[1,2])  
 #pValue, _, _ = estimateChngSignificanceAndRobustness.computeRlChngPValueAtWarmingLevBtwScen(warmingLev=warmingLev)
 #pcl, mp = plotPvalue(ax2, pValue, relChngDiff, mp, 'f: p-value, $\Delta RCP85 - \Delta RCP45$')
  std = np.std(rc_r8all-rc_r4all, 0)
  std = std/np.abs(rc_r8)
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


if __name__ == '__main__':
  plotScenVsScen(1.5)
 #plotScenVsScenAll()
 #plotGrossEnsembles()
 #printStatsByScenEnsemble('rcp85', 1.5)
 #printStatsByGrossEnsemble(2.0)
  plt.show()
