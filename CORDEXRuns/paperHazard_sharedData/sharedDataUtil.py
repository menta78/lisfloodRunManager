import numpy as np

  
def getSignificance(chmdn, chByModel):
  posi = np.zeros(chByModel.shape)*np.nan
  posi[chByModel > 0] = 1
  nega = np.zeros(chByModel.shape)*np.nan
  nega[chByModel < 0] = 1
  mdlvalid = ~np.isnan(chByModel)
  nmdl = np.nansum(mdlvalid, 0)
  sigthr = np.floor(nmdl/3*2)
  smposi = np.nansum(posi, 0)
  smnega = np.nansum(nega, 0)
  sgn = np.zeros(chmdn.shape)
  sgn[chmdn > 0] = (smposi > sigthr)[chmdn > 0]
  sgn[chmdn < 0] = (smnega > sigthr)[chmdn < 0]
  sgn[np.isnan(chmdn)] = np.nan
  return sgn
