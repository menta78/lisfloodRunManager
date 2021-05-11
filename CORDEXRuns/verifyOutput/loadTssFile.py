import os, re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
import netCDF4
import pandas as pd



"""
example of file path:
/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/ClimateRuns/LisfloodEuroCordex/historical/IPSL-INERIS-WRF331F/wuConst/disWin_IPSL-INERIS-WRF331F_historical_1981010100.tss
which startDate is 19810101
"""
def loadTssFile(filePath, startDate=datetime(1981, 1, 1), timeDelta = relativedelta(days=1), selectStatIds = None):
  fl = open(filePath)
  fl.readline()
  ln = fl.readline().strip(' \n\r\t')
  nstat = int(ln)
  fl.readline()
  statIds = []
  for i in range(nstat-1):
    ln = fl.readline().strip(' \n\r\t')
    statIds.append(int(ln))
  
  tms = []
  dis = []
  actDate = startDate
  for ln in fl:
    ln = ln.strip(' \n\r\t')
    vls = ln.split()
    timeStep = int(vls[0])
    disActDate = [float(v) for v in vls[1:]]
    actDate = startDate + (timeStep - 1)*timeDelta
    tms.append(actDate)
    dis.append(disActDate)

  tms = np.array(tms)
  statIds = np.array(statIds)
  dis = np.array(dis)

  statIndx = np.argsort(statIds)
  statIds = statIds[statIndx]
  dis = dis[:, statIndx]

  if not selectStatIds is None:
    selectStatIds = np.array(selectStatIds)
    idx = np.searchsorted(statIds, selectStatIds)
    dis = dis[:, idx]
    statIds = selectStatIds

  dis[dis > 1e20] = np.nan

  return tms, statIds, dis



def loadTssFromDir(dirPath, selectStatIds=None, startDate=datetime(1981, 1, 1), timeDelta = relativedelta(days=1)):
  print('loading from ' + dirPath)
  fls = [f for f in os.listdir(dirPath) if re.match('disWin(.*)\.tss', f)]
  fls.sort()
  tms, dis = None, None
  actDate = startDate - timeDelta
  for f in fls:
    print('  loading ' + f)
    fpth = os.path.join(dirPath, f)
    tmsAct, statIds, disAct = loadTssFile(fpth, startDate=startDate, timeDelta=timeDelta, selectStatIds=selectStatIds)
    indx = np.where(tmsAct > actDate)[0]
    tmsAct = tmsAct[indx]
    disAct = disAct[indx, :]
    tms = tmsAct if tms is None else np.concatenate([tms, tmsAct], 0)
    dis = disAct if dis is None else np.concatenate([dis, disAct], 0)
    actDate = np.max(tmsAct)
  return tms, statIds, dis
    
    


# msr file: /STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/validationData/Qts_Europe_measurements.csv
def loadMeasurePseudoTss(msrFilePath, selectStatIds = None):
  fl = open(msrFilePath)
  stats = fl.readline().strip(' \n\r\t,').split(',')
  statIds = [int(st.replace('C', '')) for st in stats]
  
  tms = []
  dis = []
  for ln in fl:
    ln = ln.strip(' \n\r\t')
    vls = ln.split(',')
    disActDate =[float(v) if v != '' else np.nan for v in vls[1:]]
    actDate = datetime.strptime(vls[0], '%m/%d/%Y')
    tms.append(actDate)
    dis.append(disActDate)

  tms = np.array(tms)
  statIds = np.array(statIds)
  dis = np.array(dis)

  statIndx = np.argsort(statIds)
  statIds = statIds[statIndx]
  dis = dis[:, statIndx]

  if not selectStatIds is None:
    selectStatIds = np.array(selectStatIds)
    idx = np.searchsorted(statIds, selectStatIds)
    dis = dis[:, idx]
    statIds = selectStatIds

  dis[dis > 1e20] = np.nan

  return tms, statIds, dis


def filterCatchmentAreasLowerThan(statIds, threshold=1e9):
  ds = netCDF4.Dataset('./outlets.nc')
  outlets = ds.variables['outlets'][:].astype(float)
  ds.close()

  ds = netCDF4.Dataset('./upArea.nc')
  upArea = ds.variables['upArea'][:]
  ds.close()

  msk = upArea < threshold
  outlets[msk] = np.nan
  
  stats = outlets[~np.isnan(outlets)].astype(int)
  stats = np.unique(outlets[~np.isnan(outlets)].astype(int))

  return stats



def _loadNewObservationDataset(msrFlPath, statIdFlPath, selectStatIds = None):
  dfmsrs = pd.read_csv(msrFlPath, sep=';')
  dfmsrs = dfmsrs.rename(columns={'station': 'Efas_id'})
  dfStatId = pd.read_excel(statIdFlPath)
  dfmsrs = dfmsrs.merge(dfStatId[['Efas_id', 'HylkeCalib']], on='Efas_id', how='left')  
  dfmsrs.datetime = pd.to_datetime(dfmsrs.datetime)
  
  tms_ = pd.DataFrame(dfmsrs.datetime.unique(), columns=['datetime'])
  tms_ = tms_.sort_values(by='datetime')
  if selectStatIds is None:
    hylkeCalibStat = [hid for hid in dfStatId.HylkeCalib.unique().astype(str) if not hid in ['-', ' ']]
  else:
    hylkeCalibStat = ['C' + str(sid).zfill(3) for sid in selectStatIds]
  hylkeCalibStat = np.array(hylkeCalibStat)
  disMsrs = np.ones([tms_.shape[0], hylkeCalibStat.shape[0]])*np.nan
  statIds = []
  for hstid, ist in zip(hylkeCalibStat, range(hylkeCalibStat.shape[0])):
    print('loading stations ' + hstid + ' ...')
    stid = int(hstid.replace('C', ''))
    statIds.append(stid)
    dfii_ = dfmsrs[dfmsrs.HylkeCalib == hstid]
    dfii = tms_.merge(dfii_, on='datetime', how='left')
    disMsrs[:, ist] = dfii.D.values
  return tms_, statIds, disMsrs
    
def loadNewObservationDataset(msrFlPath, statIdFlPath, cacheFilePath, selectStatIds=None, timeHorizon=None):
  if os.path.isfile(cacheFilePath + '.npz'):
    dt = np.load(cacheFilePath + '.npz', allow_pickle=True)
    tms_ = pd.DataFrame(dt['tms_'], columns=['datetime'])
    statIds = dt['statIds']
    disMsrs = dt['disMsrs']
  else:
    tms_, statIds, disMsrs = _loadNewObservationDataset(msrFlPath, statIdFlPath, selectStatIds=selectStatIds)
    np.savez(cacheFilePath, tms_=tms_, statIds=statIds, disMsrs=disMsrs)
  if not timeHorizon is None:
    startDate = timeHorizon[0]
    endDate = timeHorizon[1]
    cnd = np.logical_and(tms_.datetime >= startDate, tms_.datetime <= endDate)
    tms_ = tms_[cnd]
    disMsrs = disMsrs[cnd, :]
  disMsrs[disMsrs > 50000] = np.nan
  tms = tms_.datetime.dt.to_pydatetime()
  statIds = np.array(statIds)
  return tms, statIds, disMsrs

def saveToNcFile(tms, statIds, dis, filePath):
  import netCDF4
  if os.path.isfile(filePath):
    os.remove(filePath)
  dsout = netCDF4.Dataset(filePath, 'w')
  dsout.createDimension('station', len(statIds))
  dsout.createDimension('time', None)

  statnc = dsout.createVariable('station', 'int', ('station'))
  statnc[:] = statIds
  
  tmnc = dsout.createVariable('time', 'int', ('time'))
  unitsStr = 'Days since 1970-01-01'
  tmnum = netCDF4.date2num(tms, unitsStr)
  tmnc.units = unitsStr
  tmnc.calendar = 'standard'
  tmnc[:] = tmnum

  disnc = dsout.createVariable('dis', 'f4', ('time', 'station'))
  disnc[:] = dis

  dsout.close()

