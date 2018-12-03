import numpy as np

from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec

import getWarmingLevels as gwl


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
  plt.arrow(mn, .012, stdev, 0, head_length=1, length_includes_head=True)
  plt.arrow(mn, .012, -stdev, 0, head_length=1, length_includes_head=True)
  plt.text(mn, .007, 'one $\sigma$ c.i.', fontsize=13, ha='center')

  plt.ylabel('pdf', fontsize=15)
  plt.grid('on')
  if showLegend:
    lgnd = plt.legend(fontsize=13)
  plt.text(2002, -.005, text, fontsize=14)
  ax.tick_params(axis='both', labelsize=12)





def plotTimeUncertainty():
  fig = plt.figure(figsize=[15,8])
  gc = GridSpec(2, 3, width_ratios=[2,1,.5])

  ax = plt.subplot(gc[0, 0])
  pdfTot, pdfR8, pdfR4 = gwl.getWarmingLevelMixDistributions(1.5)
  plotPdfs(ax, pdfR8, pdfR4, pdfTot, 'a: time pdf, warming level $1.5^\circ$', showLegend=True)
  ax.set_xticklabels([])


  ax = plt.subplot(gc[1, 0])
  pdfTot, pdfR8, pdfR4 = gwl.getWarmingLevelMixDistributions(2.0)
  plotPdfs(ax, pdfR8, pdfR4, pdfTot, 'a: time pdf, warming level $2.0^\circ$', showLegend=False)

  plt.tight_layout()

