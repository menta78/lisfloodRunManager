import netCDF4
import numpy as np
import pandas
import os, re
from scipy.interpolate import interp1d


def getCountries():
  cntrs = pandas.read_csv('countries.csv')
  ds = netCDF4.Dataset('EU27plusUK_code.nc')
  cdMap = ds.variables['code'][:]
  ds.close()
  return cntrs, cdMap


def elabModel(scen, model, inputNcFlPath, outputCsvFlPath, mask, diagnosticsDataDir=None):
  print('elaborating scen,model = ' + scen + ',' + model)

  bslnYear = 1995

  print('  loading the data ...')
  dsin = netCDF4.Dataset(inputNcFlPath)
  x = dsin.variables['x'][:]
  y = dsin.variables['y'][:]
  inRetPer = dsin.variables['return_period'][:]
  rlYrs = dsin.variables['year'][:]
  bslnYIndx = np.where(rlYrs ==  bslnYear)[0][0]
  retLev = dsin.variables['rl_min_ws'][:, bslnYIndx, :, :].squeeze()
  yrsAll = dsin.variables['year_all'][:]
  yrMinFlw = dsin.variables['year_min_ws'][:]
  dsin.close()

  cntrs, cntrMap = getCountries()

 #mskDs = netCDF4.Dataset('upArea.nc')
 #upArea = mskDs.variables['upArea'][:].transpose()
 #smallCtchArea = upArea  < 1e9
 #mskDs.close()

  def getOutFrq(inRetPer, currentLev, retLevBsln):
    nx = currentLev.shape[0]
    ny = currentLev.shape[1]
    outRetPer = np.zeros([nx, ny])*np.nan
    for ix in range(nx):
      for iy in range(ny):
        rlcri = currentLev[ix, iy]
        if np.sum(np.isnan(rlcri)) > 0:
          continue
        rlbsln = retLevBsln[:, ix, iy]
       #if rlbsln[0] < .3:
       #  continue
        outRetPer[ix, iy] = max(interp1d(rlbsln, inRetPer, axis=0, fill_value='extrapolate')(rlcri), 0)
    frq = 1/outRetPer
    frq[frq < 0] = np.nan
    frq[np.isinf(frq)] = np.nan
    return frq

  cols = ['COUNTRY']
  cols.extend(str(int(y)) for y in yrsAll)
  outdf = pandas.DataFrame(columns=cols, index=cntrs.values[:,1])
  for cnt in cntrs.values:
    outdf.loc[cnt[1]]['COUNTRY'] = cnt[0]

  for yr, mnfl in zip(yrsAll, yrMinFlw):
    print('  elaborating year ' + str(int(yr)))
    print('    interpolating ...')
   #mnfl[smallCtchArea] = np.nan
    mnfl[~mask] = np.nan
    frq = getOutFrq(inRetPer, mnfl, retLev)
    if not diagnosticsDataDir is None:
      outFlName = os.path.join(diagnosticsDataDir, '_'.join('droughtFrqDiagnostics', model, scen, str(y))
      np.save(outFlName)
    print('    compute median by country ...')
    for cnt in cntrs.values:
      print('      ' + cnt[0])
      msk_ = cntrMap == cnt[1]
      frqC = np.nanmedian(frq[msk_.transpose()])
      outdf.loc[cnt[1]][str(int(yr))] = frqC
      
  outdf.to_csv(outputCsvFlPath)


def loadMask(baselineEnsembleFilePath):
  ds = netCDF4.Dataset(baselineEnsembleFilePath)
  rl = ds.variables['baseline_return_level']
  mask = ~np.isnan(rl)
  return mask


def loopModels(inputDir, inputFlPattern, baselineEnsembleFilePath, outputDir, diagnosticsDataDir=None):
  if not os.path.isfile(baselineEnsembleFilePath):
    raise Exception('file ' + baselineEnsembleFilePath + ' does not exist. Generate it with the script doCreateEnsembleFile.py')
  mask = loadMask(baselineEnsembleFilePath)
  infls = [fl for fl in os.listdir(inputDir) if re.match(inputFlPattern, fl)]
  for fl in infls:
    print('elaborating file ' + fl)
    flpth = os.path.join(inputDir, fl)
    outflpth = os.path.join(outputDir, fl.replace('projection_', 'freqByCountry_').replace('.nc', '.csv'))
    print('  output file path: ' + outflpth)
    if os.path.isfile(outflpth):
      print('    file already exists, skipping ...')
      continue
    m = re.match(inputFlPattern, fl)
    scen = m.groups()[0]
    model = m.groups()[1]
    elabModel(scen, model, flpth, outflpth, mask, diagnosticsDataDir=diagnosticsDataDir)


if __name__ == '__main__':
  import pdb; pdb.set_trace()


  inputDir = '/ClimateRun4/multi-hazard/eva/'
  inputFlPattern = 'projection_dis_(rcp45|rcp85)_(.*)_wuConst_statistics.nc'
  outputDir = '/DATA/mentalo/Dropbox/notSynced/xGustavo/lowFlowWrmSsnByCountry'
  diagnosticsDataDir = '/DATA/ClimateRuns/droughtFreqDiagnostics/'
  baselineEnsembleFilePath = '/DATA/mentalo/Dropbox/notSynced/xAlessandra/minDisWrmSsnEnsemble.nc'

 # precipitations
 #inputDir = '/ClimateRun4/multi-hazard/eva/'
 #inputDir = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/lisfloodEVA_pr/test'
 #inputFlPattern = 'projection_pr_(rcp45|rcp85)_(.*)_statistics.nc'
 #outputDir = '/ClimateRun4/multi-hazard/eva/prFrequencyShift/'

  loopModels(inputDir, inputFlPattern, baselineEnsembleFilePath, outputDir, diagnosticsDataDir=diagnosticsDataDir)

