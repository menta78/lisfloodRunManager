import netCDF4
import numpy as np


def loadOutletDischarge(ncOutletPth, ncDischargeMapPth):
  outletDs = netCDF4.Dataset(ncOutletPth)
  outlets = outletDs.variables['outlets'][:]
  oirow, oicol = np.where(np.logical_not(outlets.mask))

  disDs = netCDF4.Dataset(ncDischargeMapPth)
  tmnc = disDs.variables['time']
  try:
    calendar = tmnc.calendar
  except:
    calendar = 'gregorian'
  tmnum = tmnc[:]
  tm = netCDF4.num2date(tmnc[:], tmnc.units, calendar)
  dis = disDs.variables['dis'][:]
  
  outPtIds = []
  timeSrs = []
  npts = len(oirow)
  for irow, icol in zip(oirow, oicol):
    outPtIdAct = outlets[irow, icol]
    outPtIds.append(outPtIdAct)
    timeSrsAct = dis[:, irow, icol]
    timeSrs.append(timeSrsAct)
  outPtIds = np.array(outPtIds)
  timeSrsWithNan = np.array(timeSrs).transpose()
  timeSrs = timeSrsWithNan
  timeSrs[np.isnan(timeSrs)] = 1e31

  outPtIdsFinal = np.arange(max(outPtIds)) + 1
  timeSrsFinal = np.ones([timeSrs.shape[0], outPtIdsFinal.shape[0]])*1e31 
  outPtIndxs = outPtIds - 1
  timeSrsFinal[:, outPtIndxs] = timeSrs
  return tm, tmnum, outPtIdsFinal, timeSrsFinal
  

def saveOutletDischargeToTss(timenum, outPtIds, timeSrs, outFlPth):
  fl = open(outFlPth, 'w')
  fl.write('timeseries scalar\n')
  fl.write(str(len(outPtIds) + 1) + '\n')
  fl.write('timestep\n')
  for ptid in outPtIds:
    fl.write(str(ptid) + '\n')
  for itm in range(timeSrs.shape[0]):
    tmstr = str(int(timenum[itm]) + 1)
    vls = timeSrs[itm, :]
    vlstrs = [str(v)[:7] for v in vls]
    vlstrs.insert(0, tmstr)
    ln = '    ' + '        '.join(vlstrs) + '\n'
    fl.write(ln)
  fl.close()

def nc2tss(ncOutletPth, ncDischargeMapPth, outTssFlPth):
  tm, timenum, outPtIds, timeSrs = loadOutletDischarge(ncOutletPth, ncDischargeMapPth)
  saveOutletDischargeToTss(timenum, outPtIds, timeSrs, outTssFlPth)

