import numpy as np

from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec

import getWarmingLevels as gwl
import loadWlVsScenChange as ldEnsmbl
from plotFigureWlVsScenChange import plotRelChngDiff


def plotPdfs(ax, pdfR8, pdfR4, pdfTot, text, showLegend=True):
  plt.axes(ax)
  r8 = plt.plot(pdfR8.xk, pdfR8.pk, label='rcp85')
  r4 = plt.plot(pdfR4.xk, pdfR4.pk, label='rcp45')
  rt = plt.plot(pdfTot.xk, pdfTot.pk, label='mix distrib.', color='k', linewidth=4)

  plt.xlim([2000, 2080])
  ylm = plt.ylim()
  plt.ylim([-.007, max(ylm)])

  stdev = pdfTot.std()
  mn = pdfTot.mean()
  sdvmin = int(np.round(mn - stdev))
  sdvmax = int(np.round(mn + stdev))
  imin = np.where(pdfTot.xk==sdvmin)[0][0]
  imax = np.where(pdfTot.xk==sdvmax)[0][0]
  stdevx = pdfTot.xk[imin:imax+1]
  stdevy = pdfTot.pk[imin:imax+1]
  ax.fill_between(stdevx, 0, stdevy, alpha=.2, color='lime')
  plt.arrow(mn, .008, stdev, 0, head_length=1, length_includes_head=True, color='k')
  plt.arrow(mn, .008, -stdev, 0, head_length=1, length_includes_head=True, color='k')
  plt.text(mn, .003, 'one $\sigma$ c.i.', fontsize=13, ha='center')
  imn = np.where(pdfTot.xk==np.round(mn))[0][0]
  plt.plot([mn, mn], [0, pdfTot.pk[imn]], '--', color='k')

 #stdev = pdfR4.std()
 #mn = pdfR4.mean()
 #plt.arrow(mn, .022, stdev, 0, head_length=1, length_includes_head=True, color='darkorange')
 #plt.arrow(mn, .022, -stdev, 0, head_length=1, length_includes_head=True, color='darkorange')

  plt.ylabel('pdf', fontsize=15)
  plt.grid('on')
  if showLegend:
    lgnd = plt.legend(fontsize=13)
  plt.text(2002, -.005, text, fontsize=14)
  ax.tick_params(axis='both', labelsize=12)



def plotUncertaintyMap(ax, pdfTot, mp, text, scen=None):
  stdev = pdfTot.std()
  mn = pdfTot.mean()
  sdvmin = int(np.round(mn - stdev))
  sdvmax = int(np.round(mn + stdev))
  if not scen is None:
    rlChngInf = ldEnsmbl.getRcpEnsembleAtYear(sdvmin, scen=scen)
    rlChngSup = ldEnsmbl.getRcpEnsembleAtYear(sdvmax, scen=scen)
  else:
    rlChngInf = ldEnsmbl.getGrossEnsembleAtYear(sdvmin)
    rlChngSup = ldEnsmbl.getGrossEnsembleAtYear(sdvmax)
  sigma = np.abs(rlChngSup-rlChngInf)/2.
  return plotRelChngDiff(ax, sigma, mp, text, vmin=0, vmax=10, cmap='hot_r')



def plotTimeUncertainty():
  outPng = 'timeSigma_grossEnsemble.png'

  fig = plt.figure(figsize=[15,8])
  gc = GridSpec(2, 3, width_ratios=[2,1,.05])

  ax00 = plt.subplot(gc[0, 0])
  pdfTot, pdfR8, pdfR4 = gwl.getWarmingLevelMixDistributions(1.5)
  plotPdfs(ax00, pdfR8, pdfR4, pdfTot, 'a: time pdf, warming level $1.5^\circ$', showLegend=True)
  ax00.set_xticklabels([])

  ax01 = plt.subplot(gc[0, 1])
  mp = None
  pcl, mp = plotUncertaintyMap(ax01, pdfTot, mp, 'b: $\sigma$ of relative change, w.l. $1.5^\circ$')

  ax10 = plt.subplot(gc[1, 0])
  pdfTot, pdfR8, pdfR4 = gwl.getWarmingLevelMixDistributions(2.0)
  plotPdfs(ax10, pdfR8, pdfR4, pdfTot, 'c: time pdf, warming level $2.0^\circ$', showLegend=False)

  ax11 = plt.subplot(gc[1, 1])
  pcl, mp = plotUncertaintyMap(ax11, pdfTot, mp, 'd: $\sigma$ of relative change, w.l. $2.0^\circ$')

  cax = plt.subplot(gc[:, 2])
  cb = plt.colorbar(pcl, ax=ax11, cax=cax)
  cb.set_label('$\sigma$ of % change', fontsize=14)
  cax.tick_params(labelsize=12)
  ax00.set_aspect('auto')
  ax01.set_aspect('auto')
  ax10.set_aspect('auto')
  ax11.set_aspect('auto')
  cax.set_aspect('auto')

  plt.tight_layout()

  fig.savefig(outPng, dpi=300)




def plotTimeUncertaintyOfWl(warmingLev=2.0):
  outPng = 'timeSigma_grossEnsemble_' + str(warmingLev) + 'deg.png'

  fig = plt.figure(figsize=[15,8])
  gc = GridSpec(2, 4, width_ratios=[1,1,1,.05])

  ax00 = plt.subplot(gc[0, :])
  pdfTot, pdfR8, pdfR4 = gwl.getWarmingLevelMixDistributions(warmingLev)
  plotPdfs(ax00, pdfR8, pdfR4, pdfTot, 'a: time pdf, warming level $' + str(warmingLev) + '^\circ$', showLegend=True)
  ax00.set_xticklabels([])

  ax10 = plt.subplot(gc[1, 0])
  mp = None
  pcl, mp = plotUncertaintyMap(ax10, pdfR8, mp, 'b: $\sigma$ of relative change, rcp85, w.l. $' + str(warmingLev) + '^\circ$')

  ax11 = plt.subplot(gc[1, 1])
  pcl, mp = plotUncertaintyMap(ax11, pdfR4, mp, 'c: $\sigma$ of relative change, rcp45, w.l. $' + str(warmingLev) + '^\circ$')

  ax12 = plt.subplot(gc[1, 2])
  pcl, mp = plotUncertaintyMap(ax12, pdfTot, mp, 'd: $\sigma$ of relative change, gross ensemble, $' + str(warmingLev) + '^\circ$')

  cax = plt.subplot(gc[1, 3])
  cb = plt.colorbar(pcl, ax=ax11, cax=cax)
  cb.set_label('$\sigma$ of % change', fontsize=14)
  cax.tick_params(labelsize=12)
  ax00.set_aspect('auto')
  ax10.set_aspect('auto')
  ax11.set_aspect('auto')
  ax12.set_aspect('auto')
  cax.set_aspect('auto')

  plt.tight_layout()
  plt.show()

  fig.savefig(outPng, dpi=300)
