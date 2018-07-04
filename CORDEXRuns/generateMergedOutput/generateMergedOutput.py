import jrcNetcdfUtil

import os, glob, sys, netCDF4, time



def generateMergedOutput(rootInDir, rootOutDir, measureName):
  scenarios = ['historical', 'rcp85', 'rcp45']
  scen0dir = os.path.join(rootInDir, scenarios[0])
  models = [d for d in os.listdir(scen0dir) 
                 if os.path.isdir(os.path.join(scen0dir, d))]
  wuChangStrs = ['wuConst', 'wuChang']
  
  for scen in scenarios:
    for model in models:
      for wuChangStr in wuChangStrs:
        tmstart = time.time()

        print('Copy-merging ' + measureName + ' for [scenario, model, waterUse]=[' + scen + ', ' + model + ', ' + wuChangStr + ']')
        inDir = os.path.join(rootInDir, scen, model, wuChangStr)
        if not os.path.isdir(inDir):
          print('... input directory does not exist')
          continue
        print('Input dir: ' + inDir)
        outDir = os.path.join(rootOutDir, scen, model, wuChangStr)
        print('Output dir: ' + outDir)
        flPattern = measureName + '*.nc'
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
        
        flIterator = jrcNetcdfUtil.ncDataIterator(inDir, varName, flPattern, outNcDir=outDir, listFileMode='wildcard')
        flIterator.generateSingleOutFile(outFlPath)

        tmend = time.time()
        tmpassed = tmend - tmstart
        print('model [' + scen + ', ' + model + ', ' + wuChangStr + '] successfully copied.')
        print('  time elapsed: ' + str(tmpassed) + ' s')

  print('All done!!')



def main():
  args = sys.argv[1:]
  if len(args) != 3:
    print('Sample call:')
    print('python generateMergedOutput.py /inputRootDir /outputRootDir dis')
    return
    
  inDir, outDir, msrName = args
  generateMergedOutput(inDir, outDir, msrName)


if __name__ == '__main__':
  main()
