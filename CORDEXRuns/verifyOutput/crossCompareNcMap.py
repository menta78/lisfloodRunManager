import xarray

inputSmplMap1 = '/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/lisflood/input/LAEAETRS89_BIAS_CORDEX/IPSL-INERIS-WRF331F/historical/e0.nc'



def getMeanFromNc(ncflpth, varName, xVarName='x', yVarName='y', timeVarName='time'):
  ds = xarray.open_dataset(ncflpth)
  xx = ds.variables[xVarName][:]
  yy = ds.variables[yVarName][:]
  varnc = ds.variables[varName]
  mn = varnc.mean(dim=timeVarName)
  ds.close()
  return xx, yy, mn
  

def getPercentileFromNc(ncflpth, varName, perc=99, xVarName='x', yVarName='y', timeVarName='time')
  ds = xarray.open_dataset(ncflpth)
  xx = ds.variables[xVarName][:]
  yy = ds.variables[yVarName][:]
  varnc = ds.variables[varName]
  qtl = perc/100.
  prctl = varnc.quantile(qtl, dim=timeVarName)
  ds.close()
  return xx, yy, prctl


def getMaps(ncflpth):
  pass

