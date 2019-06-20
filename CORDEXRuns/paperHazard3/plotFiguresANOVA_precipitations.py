import numpy as np
from scipy import stats
from matplotlib import pyplot as plt
from matplotlib import gridspec, cm, colors
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
 #lon, lat = lon.transpose(), lat.transpose()
  x, y = mp(lon, lat)

  plt.axes(ax)
  mp.drawcoastlines(linewidth=.25)
  mp.fillcontinents(color=[.95, .95, .95], lake_color=[.95, .95, .95], zorder=0)

  absSigma_ = np.abs(sigma)
  absSigma = bm.maskoceans(lon, lat, absSigma_)
 #pcl = mp.scatter(x.flatten(), y.flatten(), .07, c=absSigma.flatten(), cmap='Oranges', alpha=1, vmin=0, vmax=sigmamax)
  pcl = mp.pcolor(x, y, absSigma, cmap='Oranges', alpha=1, vmin=0, vmax=sigmamax)

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
 #lon, lat = lon.transpose(), lat.transpose()
  x, y = mp(lon, lat)

  plt.axes(ax)
  mp.drawcoastlines(linewidth=.25)
  mp.fillcontinents(color=[.95, .95, .95], lake_color=[.95, .95, .95], zorder=0)

  sgn_ = np.ones(pValue.shape)
  sgn_[pValue <= .05] = 0
  sgn_[np.isnan(pValue)] = np.nan

  sgn = bm.maskoceans(lon, lat, sgn_)

  cmap = colors.LinearSegmentedColormap.from_list('pvalue', ['red', 'white', 'lightgreen'], N=256)
  pcl = mp.pcolor(x, y, sgn, cmap=cmap, alpha=1)

  signClr = 'red'
  scSgn = mp.scatter(1e6, 1e6, .07, c=signClr, alpha=1, label='p-value $\leq$ 0.05')

  nonSignClr = 'lightgreen'
  scNonSgn = mp.scatter(1e6, 1e6, .07, c=nonSignClr, alpha=1, label='p-value $>$ 0.05')

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



def plotFigureANOVA(ncRootDir='/DATA/ClimateData/cordexEurope/yearlymeans/'):
 #varType can be extHigh, extLow, mean
 
  outPng = 'anova_precipitations.png'


  f = plt.figure(figsize=(9,12))
  gs = gridspec.GridSpec(3, 3, width_ratios=[1,1,.05])

  mp = None
  descrTxt = 'Mean precipitations'
  sigmaMax = 20


  #### at 1.5 ####
  warmingLev = 1.5

  relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all = ldEnsmbl.loadMeanPrecipitationChangesAtWl(ncRootDir=ncRootDir, warmingLev=warmingLev, nmodels=nmodels)

  sigmaTot, sigmaWithin, sigmaBetween, pValue, effectSize = anovaAnalysis(relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all)

  ax00 = plt.subplot(gs[0, 0])
  plt00, mp = plotSigma(ax00, sigmaWithin*100, mp, 'a: $\sigma_{within}, 1.5^\circ C$', txt2=descrTxt, sigmamax=sigmaMax)  
  ax10 = plt.subplot(gs[1, 0])
  plt10, mp = plotSigma(ax10, sigmaBetween*100, mp, 'c: $\sigma_{between}, 1.5^\circ C$', sigmamax=sigmaMax)  
  ax20 = plt.subplot(gs[2, 0])
  _, _, mp = plotPvalue(ax20, pValue, mp, 'e: p-val of interpathway diff.')


  #### at 2.0 ####
  warmingLev = 2.0

  relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all = ldEnsmbl.loadMeanPrecipitationChangesAtWl(ncRootDir=ncRootDir, warmingLev=warmingLev, nmodels=nmodels)

  sigmaTot, sigmaWithin, sigmaBetween, pValue, effectSize = anovaAnalysis(relChngDiff, rc_r8, rc_r4, rc_r8all, rc_r4all)

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



if __name__ == '__main__':
  import pdb; pdb.set_trace()
  plotFigureANOVA()
