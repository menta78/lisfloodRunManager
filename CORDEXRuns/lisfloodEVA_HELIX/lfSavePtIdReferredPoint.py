#!/ADAPTATION/mentalo/usr/anaconda2/bin/python
import netCDF4, os
import numpy as np
from matplotlib import pyplot as plt

def referFileToPointIds(inputNc, outputNc, ptIdNc='idChan_5km.nc'):
  dsin = netCDF4.Dataset(inputNc)
  rl = dsin.variables['rl'][:]
  se_rl = dsin.variables['se_rl'][:]
  x = dsin.variables['x'][:]
  y = dsin.variables['y'][:]
  year = dsin.variables['year'][:]
  return_period = dsin.variables['return_period'][:]
  dsin.close()

  dsptid = netCDF4.Dataset(ptIdNc)
  channelPtIds = dsptid.variables['idChan_5km.map'][:].transpose()
  dsptid.close()
  
  ymtx, xmtx = np.meshgrid(y, x)
  
  rlswp = rl.swapaxes(0, 2).swapaxes(1,3)
  rlflatten = rlswp.reshape((1000*950, 21, 25))
  
  se_rlswp = se_rl.swapaxes(0, 2).swapaxes(1,3)
  se_rlflatten = se_rlswp.reshape((1000*950, 21, 25))
  
  xflatten = xmtx.reshape(1000*950)
  yflatten = ymtx.reshape(1000*950)

  channelPtIdsFlatten = channelPtIds.reshape(1000*950)
  channelPtNotNan = np.logical_not(np.isnan(channelPtIdsFlatten))
  channelPtNotNan = np.logical_not(channelPtNotNan.mask)
  ptId = channelPtIdsFlatten[channelPtNotNan]
  rlPtId = rlflatten[channelPtNotNan, :, :]
  se_rlPtId = se_rlflatten[channelPtNotNan, :, :]
  xPtId = xflatten[channelPtNotNan]
  yPtId = yflatten[channelPtNotNan]

  if os.path.isfile(outputNc):
    os.remove(outputNc)
  outDs = netCDF4.Dataset(outputNc, 'w')

  outDs.createDimension('ptId', len(ptId))
  ptIdNc = outDs.createVariable('ptId', np.int32, ('ptId',))
  ptIdNc[:] = ptId

  outDs.createDimension('return_period', len(return_period))
  return_periodNc = outDs.createVariable('return_period', np.float64, ('return_period',))  
  return_periodNc[:] = return_period

  outDs.createDimension('year', len(year))
  yearNc = outDs.createVariable('year', np.int32, ('year',))
  yearNc[:] = year

  xNc = outDs.createVariable('x', np.float64, ('ptId',))
  xNc[:] = xPtId

  yNc = outDs.createVariable('y', np.float64, ('ptId',))
  yNc[:] = yPtId

  rlNc = outDs.createVariable('rl', np.float64, ('ptId', 'return_period', 'year',))
  rlNc[:] = rlPtId

  se_rlNc = outDs.createVariable('se_rl', np.float64, ('ptId', 'return_period', 'year',))
  se_rlNc[:] = se_rlPtId

  outDs.close()
  
  
def testReferFileToPointIds():
  import pdb; pdb.set_trace()
  inputNc = '/ADAPTATION/peseta4/tsEvaDischarge/projection_dis_rcp45_CLMcom-CCLM4-8-17_BC_ICHEC-EC-EARTH_wuChang_statistics.nc'
  outputNc = 'test.nc'
  referFileToPointIds(inputNc, outputNc)


def referFileToPointsIdsDir(inputDirectory, outputDirectory):
  infls = [f for f in os.listdir(inputDirectory) if f[-3:] == '.nc']
  for infl in infls:
    print('elaborating file ' + infl)
    oufl = infl[:-3] + '_ptId.nc'
    inflPth = os.path.join(inputDirectory, infl)
    ouflPth = os.path.join(outputDirectory, oufl)
    print('    input: ' + inflPth)
    print('    output: ' + ouflPth)
    referFileToPointIds(inflPth, ouflPth)


if __name__ == '__main__':
 #testReferFileToPointIds()
 import pdb; pdb.set_trace()
 inputDirectory = '/ADAPTATION/peseta4/tsEvaDischarge/'
 outputDirectory = '/ADAPTATION/peseta4/tsEvaDischarge_ptId/'
 referFileToPointsIdsDir(inputDirectory, outputDirectory)
  
