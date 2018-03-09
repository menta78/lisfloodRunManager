import os, re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy as np



"""
example of file path:
/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/ClimateRuns/LisfloodEuroCordex/historical/IPSL-INERIS-WRF331F/notWaterUse/disWin_IPSL-INERIS-WRF331F_historical_1981010100.tss
which startDate is 19810101
"""
def loadTssFile(filePath, startDate=datetime(1981, 01, 01), timeDelta = relativedelta(days=1), selectStatIds = None):
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

  dis[dis > 1e20] = 0

  return tms, statIds, dis



def loadTssFromDir(dirPath, selectStatIds=None, startDate=datetime(1981, 01, 01), timeDelta = relativedelta(days=1)):
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
    
    

