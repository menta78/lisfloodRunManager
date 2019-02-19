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
  


def plotRelativeSigma(ax, sigma, relChngDiff, mp, txt, sigmamax=2, signSigmaThreshold1=1, signSigmaThreshold2=2, prcTxtTmpl='', printSignTxt=True):
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
  pcl = mp.scatter(x.flatten(), y.flatten(), .07, c=absSigma.flatten(), cmap='PuBu_r', alpha=1, vmin=0, vmax=sigmamax)
  prcTxtTmpl = '% of pixel where ${thr}\|\Delta Q_{{100-wl}}\| > \sigma_{{im}}$: {p:2.0f}%' if prcTxtTmpl == '' else prcTxtTmpl

  percSign = float(np.nansum(absSigma <= signSigmaThreshold1))/np.nansum(np.logical_not(np.isnan(absSigma)))
  thrstr = '{thr:1.0f}'.format(thr=signSigmaThreshold1) if signSigmaThreshold1 != 1 else ''
  prcTxt1 = prcTxtTmpl.format(p=percSign*100, thr=thrstr)
  print(prcTxt1)

  percSign = float(np.nansum(absSigma <= signSigmaThreshold2))/np.nansum(np.logical_not(np.isnan(absSigma)))
  thrstr = '{thr:1.0f}\cdot'.format(thr=signSigmaThreshold2) if signSigmaThreshold2 != 1 else ''
  prcTxt2 = prcTxtTmpl.format(p=percSign*100, thr=thrstr)
  print(prcTxt2)

 #txtpos = mp(-7, 71)
  txtpos = mp(-24, 32)
  plt.annotate(txt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=13)
  if printSignTxt:
   #txtpos = mp(-8, 27)
    txtpos = mp(-24.3, 70.3)
    bb = {'boxstyle': 'square,pad=0', 'ec': 'none', 'fc': 'w'}
    plt.annotate(prcTxt1, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=10, bbox=bb)
   #txtpos = mp(-8, 24)
    txtpos = mp(-24.3, 69.1)
    plt.annotate(prcTxt2, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=10, bbox=bb)

  return pcl, mp
  


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
  prcTxtTmpl = '% of pixel where ${thr}\|\Delta Q_{{100-wl}}\| > \sigma_{{im}}$: {p:2.0f}%' if prcTxtTmpl == '' else prcTxtTmpl

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
  txtpos = mp(-24, 32)
  plt.annotate(txt, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=13)
  if printSignTxt:
   #txtpos = mp(-8, 27)
    txtpos = mp(-24.3, 70.3)
    bb = {'boxstyle': 'square,pad=0', 'ec': 'none', 'fc': 'w'}
    plt.annotate(prcTxt1, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=10, bbox=bb)
   #txtpos = mp(-8, 24)
    txtpos = mp(-24.3, 69.1)
    plt.annotate(prcTxt2, xy=txtpos, xycoords='data', xytext=txtpos, textcoords='data', fontsize=10, bbox=bb)

  return pcl, mp
  
  

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
  pcl, mp = plotRelChngDiff(ax0, rc_mega, mp, 'a: $\Delta$ RCP all at $' + str(warmingLev) +'^\circ$', vmax=30)
  
  sigma_im = np.nanstd(np.concatenate([rc_r8all, rc_r4all], 0), 0)
  sigmaT = getTimeSigmaGrossEnsemble(warmingLev)
  sigma = np.sqrt(sigma_im**2. + sigmaT**2.)
 #sigma_ratio = sigma/rc_mega
 #sigma_ratio[np.abs(rc_mega)<=.05] = np.nan
  ax1 = plt.subplot(gs[1,0])
  pcl, mp = plotSigma(ax1, sigma*100, rc_mega*100, mp, 'c: $\sigma$, ratio of $\Delta$ at $' + str(warmingLev) +'^\circ$',
    prcTxtTmpl = '% of pixel where ${thr}\|\Delta Q_{{100-wl}}\| > \sigma$: {p:2.0f}%')

  warmingLev = 2.0

  relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all = ldEnsmbl.loadWlVsScenChange(warmingLev=warmingLev)
  rc_mega = (rc_r8 + rc_r4)/2.
  ax2 = plt.subplot(gs[0,1])
  pclChng, mp = plotRelChngDiff(ax2, rc_mega, mp, 'b: $\Delta$ RCP all at $' + str(warmingLev) +'^\circ$', vmax=30)
  
  sigma_im = np.nanstd(np.concatenate([rc_r8all, rc_r4all], 0), 0)
  sigmaT = getTimeSigmaGrossEnsemble(warmingLev)
  sigma = np.sqrt(sigma_im**2. + sigmaT**2.)
 #sigma_ratio = sigma/rc_mega
 #sigma_ratio[np.abs(rc_mega)<=.05] = np.nan
  ax3 = plt.subplot(gs[1,1])
  pclSigma, mp = plotSigma(ax3, sigma*100, rc_mega*100, mp, 'd: $\sigma$, ratio of $\Delta$ at $' + str(warmingLev) +'^\circ$',
    prcTxtTmpl = '% of pixel where ${thr}\|\Delta Q_{{100-wl}}\| > \sigma$: {p:2.0f}%')
  
  cax1 = plt.subplot(gs[0,2])
  cb = plt.colorbar(pclChng, ax=ax2, cax=cax1)
  cb.set_label('$\Delta$ 100-y discharge (%)')
  
  cax2 = plt.subplot(gs[1,2])
  cb = plt.colorbar(pclSigma, ax=ax3, cax=cax2)
  cb.set_label('$\sigma$ (%)')

  ax0.set_aspect('auto')
  ax1.set_aspect('auto')
  ax2.set_aspect('auto')
  ax3.set_aspect('auto')
  cax1.set_aspect('auto')
  cax2.set_aspect('auto')

  plt.tight_layout()

  f.savefig(outPng, dpi=300)



if __name__ == '__main__':
  plotGrossEnsembles()
 #printStatsByScenEnsemble('rcp85', 2.0)
 #printStatsByGrossEnsemble(2.0)
  plt.show()
