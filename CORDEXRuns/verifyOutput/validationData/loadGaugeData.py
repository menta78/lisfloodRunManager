from datetime import datetime
import numpy as np

def loadGaugeData(flpth):
  fl = open(flpth)
  tm = []
  dis = []
  for ln in fl:
    ln = ln.strip(' \n\t\r')
    vlstr = ln.split(';')
    dt = datetime.strptime(vlstr[1], '%Y-%m-%d %H:%M:%S')
    ds = float(vlstr[3])
    tm.append(dt)
    dis.append(ds)
  return np.array(tm), np.array(dis)

