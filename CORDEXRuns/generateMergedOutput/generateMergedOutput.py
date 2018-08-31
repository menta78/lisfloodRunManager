import jrcNetcdfUtil

import os, glob, sys, netCDF4, time



def generateMergedOutput(rootInDir, rootOutDir, measureName, recoveryRun=True, firstModelForRecoveryRun=''):
  scenarios = ['historical', 'rcp85', 'rcp45']
  scen0dir = os.path.join(rootInDir, scenarios[0])
  models = [d for d in os.listdir(scen0dir) 
                 if os.path.isdir(os.path.join(scen0dir, d))]
  wuChangStrs = ['wuConst', 'wuChang']
  
  recoveringGeneratedFiles = recoveryRun
  for scen in scenarios:
    for model in models:
      for wuChangStr in wuChangStrs:

        if recoveringGeneratedFiles:
          modelStr = '_'.join([scen, wuChangStr, model])
          if modelStr == firstModelForRecoveryRun:
            recoveringGeneratedFiles = False
          else:
            print('  model ' + modelStr + ' already generated. Skipping')
            continue

        tmstart = time.time()

        print('Copy-merging ' + measureName + ' for [scenario, model, waterUse]=[' + scen + ', ' + model + ', ' + wuChangStr + ']')
        inDir = os.path.join(rootInDir, scen, model, wuChangStr)
        if not os.path.isdir(inDir):
          print('... input directory does not exist')
          continue
        print('Input dir: ' + inDir)
        outDir = os.path.join(rootOutDir, scen, model, wuChangStr)
        print('Output dir: ' + outDir)
        flPattern = measureName + '_*.nc'
        print('Input file pattern: ' + flPattern)

        testFlPattern = os.path.join(inDir, flPattern)
        testFls = glob.glob(testFlPattern)
        if len(testFls) == 0:
          raise Exception('No file found corresponding to pattern')
        testFls.sort()
        fl0 = testFls[0]
        ds = netCDF4.Dataset(fl0)
        varName = ds.variables.keys()[-1] 
        ds.close()
        print('Variable name: ' + varName)
        
        try:
          os.makedirs(outDir)
        except:
          pass

        outNcFileName = '_'.join([measureName, model, scen, wuChangStr]) + '.nc'
        outFlPath = os.path.join(outDir, outNcFileName) 
        if (not os.path.isfile(outFlPath)) or (not checkExistingFile(outFlPath, testFls[0], testFls[-1])):
          flIterator = jrcNetcdfUtil.ncDataIterator(inDir, varName, flPattern, outNcDir=outDir, listFileMode='wildcard')
          flIterator.generateSingleOutFile(outFlPath)

          tmend = time.time()
          tmpassed = tmend - tmstart
          print('model [' + scen + ', ' + model + ', ' + wuChangStr + '] successfully copied.')
          print('  time elapsed: ' + str(tmpassed) + ' s')
        else:
          print('    file already generated: ' + outFlPath)

  print('All done!!')


def checkExistingFile(mergedFile, firstUmFile, lastUmFile):
  result = False
  try:
    ds = netCDF4.Dataset(mergedFile)
    tmnc = ds.variables['time']
    tmMerge = [tmnc[0], tmnc[-1]] 
    ds.close()
    ds = netCDF4.Dataset(firstUmFile)
    tmIni = ds.variables['time'][0]
    ds.close()
    ds = netCDF4.Dataset(lastUmFile)
    tmLas = ds.variables['time'][-1]
    ds.close()
    
    result = (tmMerge[0] == tmIni) and (tmMerge[-1] == tmLas)
  except:
    pass
  return result


def main():
  args = sys.argv[1:]
  if len(args) < 3:
    print('Sample call:')
    print('python generateMergedOutput.py /inputRootDir /outputRootDir dis <firstModelForRecoveryRun>')
    print('  the 4th argument is supplementary, and specifies the first model to be considered, as a string')
    print('  scenario_wuChangeStr_model')
    return
    
  inDir, outDir, msrName = args[:3]
  firstModelForRecoveryRun = args[3] if len(args) > 3 else ''
  recoveryRun = firstModelForRecoveryRun != ''
  generateMergedOutput(inDir, outDir, msrName, recoveryRun, firstModelForRecoveryRun)


if __name__ == '__main__':
  main()
