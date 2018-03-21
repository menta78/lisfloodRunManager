import numpy as np
import xarray
import os, re, pickle
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


def getMeanFromNc(ncflpth, varName, xVarName='x', yVarName='y', timeVarName='time'):
  ds = xarray.open_dataset(ncflpth)
  xx = np.array(ds.variables[xVarName][:])
  yy = np.array(ds.variables[yVarName][:])
  varnc = ds.variables[varName]
  mn = np.array(varnc.mean(dim=timeVarName))
  ds.close()
  return xx, yy, mn
  

def getPercentileFromNc(ncflpth, varName, perc=99, xVarName='x', yVarName='y', timeVarName='time'):
  ds = xarray.open_dataset(ncflpth)
  xx = np.array(ds.variables[xVarName][:])
  yy = np.array(ds.variables[yVarName][:])
  varnc = ds.variables[varName]
  qtl = perc/100.
  prctl = np.array(varnc.quantile(qtl, dim=timeVarName))
  ds.close()
  return xx, yy, prctl


def getMaps(ncflpth, varName, modelName, xVarName='x', yVarName='y', timeVarName='time'):
  flnm = os.path.basename(ncflpth)
  dr = os.path.dirname(os.path.abspath(__file__))
  cachedir = os.path.join(dr, 'mapCache')
  try:
    os.mkdir(cachedir)
  except:
    pass
  cacheFl = os.path.join(cachedir, flnm + '.' + modelName + '.stat.pickle')
  if not os.path.isfile(cacheFl):
    xx, yy, mn = getMeanFromNc(ncflpth, varName, xVarName=xVarName, yVarName=yVarName, timeVarName=timeVarName)
    _, _, pctl95 = getPercentileFromNc(ncflpth, varName, perc=95, xVarName=xVarName, yVarName=yVarName, timeVarName=timeVarName)
    _, _, pctl99 = getPercentileFromNc(ncflpth, varName, perc=99, xVarName=xVarName, yVarName=yVarName, timeVarName=timeVarName)
    cf = open(cacheFl, 'w')
    pickle.dump([xx, yy, mn, pctl95, pctl99], cf, pickle.HIGHEST_PROTOCOL)
    cf.close()
  else:
    cf = open(cacheFl)
    xx, yy, mn, pctl95, pctl99 = pickle.load(cf)
    cf.close()
  return xx, yy, mn, pctl95, pctl99


  
def plotAll():
  outputfig = 'crossComparisonInputMaps.png'

  cordexMeteoDir = '/ADAPTATION/mentalo/lisfloodRun/testCordex/meteo/IPSL-INERIS-WRF331F/'
  hindcastMeteoDir = '/FLOODS/lisflood/Europe/meteo/noshift/'

  fg, axmtx = plt.subplots(3, 4, figsize=(12, 9))
  plt.tight_layout()

  fls = [f for f in os.listdir(cordexMeteoDir) if re.match('(.*)\.nc$', f)]
  firstFile = True
  for f, i in zip(fls, range(len(fls))):
    varName = re.sub('\.nc', '', f)

    if varName == 'e0':
      pVarName = 'e'
    elif varName == 'ta':
      pVarName = 'tas'
    else:
      pVarName = varName

    print('loading ' + f)
    print('  from hindcast:')
    flpth = os.path.join(hindcastMeteoDir, f)
    xx, yy, mnH, pctl95H, pctl99H = getMaps(flpth, varName, 'hindcast')
    print('  from projection:')
    flpth = os.path.join(cordexMeteoDir, f)
    _, _, mnP, pctl95P, pctl99P = getMaps(flpth, pVarName, 'proj')

    if varName != 'ta':
      ratioM = (mnP/mnH - 1)*100.
      ratioP95 = (pctl95P/pctl95H - 1)*100.
      ratioP99 = (pctl99P/pctl99H - 1)*100.
      mxM = int(np.ceil(np.nanpercentile(ratioM[:], 99.5)/10)*10)
      mxP95 = int(np.ceil(np.nanpercentile(ratioP95[:], 99.5)/10)*10)
      mxP99 = int(np.ceil(np.nanpercentile(ratioP99[:], 99.5)/10)*10)
      mx = max([mxM, mxP95, mxP99])
      dc = 10
    else:
      mnH = mnH + 273.15
      pctl95H = pctl95H + 273.15
      pctl99H = pctl99H + 273.15
      ratioM = mnP - mnH
      ratioP95 = pctl95P - pctl95H
      ratioP99 = pctl99P - pctl99H
      mx = 10
      dc = 1

    ax = axmtx[0, i]
    ct = ax.contourf(xx, yy, ratioM, range(-mx, mx, dc), cmap='jet')
    cbaxes = inset_axes(ax, width='3%', height='50%', loc=1)
    cb = plt.colorbar(ct, cax=cbaxes, orientation='vertical')
    if varName == 'ta':
      cb.set_label('$\Delta T (K)$', labelpad=-40)
    cbaxes.yaxis.set_ticks_position('left')
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid('on')
    if firstFile:
      ax.set_ylabel('Mean (% $\Delta$ proj. - hind.)', fontsize=11, labelpad=.2)
    xlm = ax.get_xlim()
    xt = np.mean(xlm)
    ylm = ax.get_ylim()
    yt = np.max(ylm) + (np.max(ylm) - np.min(ylm))/50.
    ax.text(xt, yt, varName, fontsize=14)

    ax = axmtx[1, i]
    ct = ax.contourf(xx, yy, ratioP95, range(-mx, mx, 10), cmap='jet')
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid('on')
    if firstFile:
      ax.set_ylabel('95 perc. (% $\Delta$ proj. - hind.)', fontsize=11, labelpad=.2)

    ax = axmtx[2, i]
    ct = ax.contourf(xx, yy, ratioP99, range(-mx, mx, 10), cmap='jet')
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid('on')
    if firstFile:
      ax.set_ylabel('99 perc. (% $\Delta$ proj. - hind.)', fontsize=11, labelpad=.2)
    
    firstFile = False
  plt.tight_layout()

  fg.savefig(outputfig, dpi=300)

  


def plotAllAlfieri():
  outputfig = 'crossComparisonInputMaps_Alfieri.png'

  cordexMeteoDir = '/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/lisflood/in'
  hindcastMeteoDir = '/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/lisflood/input/hindcast/'

  fg, axmtx = plt.subplots(3, 4, figsize=(12, 9))
  plt.tight_layout()

  fls = [f for f in os.listdir(cordexMeteoDir) if re.match('(.*)\.nc$', f)]
  firstFile = True
  for f, i in zip(fls, range(len(fls))):
    varName = re.sub('\.nc', '', f)

    if varName == 'e0':
      pVarName = 'e'
    elif varName == 'ta':
      pVarName = 'tas'
    else:
      pVarName = varName

    print('loading ' + f)
    print('  from hindcast:')
    flpth = os.path.join(hindcastMeteoDir, f)
    xx, yy, mnH, pctl95H, pctl99H = getMaps(flpth, varName, 'hindcast')
    print('  from projection:')
    flpth = os.path.join(cordexMeteoDir, f)
    _, _, mnP, pctl95P, pctl99P = getMaps(flpth, pVarName, 'proj')

    if varName != 'ta':
      ratioM = (mnP/mnH - 1)*100.
      ratioP95 = (pctl95P/pctl95H - 1)*100.
      ratioP99 = (pctl99P/pctl99H - 1)*100.
      mxM = int(np.ceil(np.nanpercentile(ratioM[:], 99.5)/10)*10)
      mxP95 = int(np.ceil(np.nanpercentile(ratioP95[:], 99.5)/10)*10)
      mxP99 = int(np.ceil(np.nanpercentile(ratioP99[:], 99.5)/10)*10)
      mx = max([mxM, mxP95, mxP99])
      dc = 10
    else:
      mnH = mnH + 273.15
      pctl95H = pctl95H + 273.15
      pctl99H = pctl99H + 273.15
      ratioM = mnP - mnH
      ratioP95 = pctl95P - pctl95H
      ratioP99 = pctl99P - pctl99H
      mx = 10
      dc = 1

    ax = axmtx[0, i]
    ct = ax.contourf(xx, yy, ratioM, range(-mx, mx, dc), cmap='jet')
    cbaxes = inset_axes(ax, width='3%', height='50%', loc=1)
    cb = plt.colorbar(ct, cax=cbaxes, orientation='vertical')
    if varName == 'ta':
      cb.set_label('$\Delta T (K)$', labelpad=-40)
    cbaxes.yaxis.set_ticks_position('left')
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid('on')
    if firstFile:
      ax.set_ylabel('Mean (% $\Delta$ proj. - hind.)', fontsize=11, labelpad=.2)
    xlm = ax.get_xlim()
    xt = np.mean(xlm)
    ylm = ax.get_ylim()
    yt = np.max(ylm) + (np.max(ylm) - np.min(ylm))/50.
    ax.text(xt, yt, varName, fontsize=14)

    ax = axmtx[1, i]
    ct = ax.contourf(xx, yy, ratioP95, range(-mx, mx, 10), cmap='jet')
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid('on')
    if firstFile:
      ax.set_ylabel('95 perc. (% $\Delta$ proj. - hind.)', fontsize=11, labelpad=.2)

    ax = axmtx[2, i]
    ct = ax.contourf(xx, yy, ratioP99, range(-mx, mx, 10), cmap='jet')
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid('on')
    if firstFile:
      ax.set_ylabel('99 perc. (% $\Delta$ proj. - hind.)', fontsize=11, labelpad=.2)
    
    firstFile = False
  plt.tight_layout()

  fg.savefig(outputfig, dpi=300)
