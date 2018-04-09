#! /usr/bin/python

__author__="Lorenzo Mentaschi"
__version__ ="0.0"

import argparse, os, shutil, re
import xarray
import numpy as np



def parseArguments():
  descr = 'netcdf2pcraster: converts netcdf to pcraster.\nSample call:\npython netcdf2pcraster.py -c mapPrototype.map -n pr pr.nc /myMapDestinationFolder/'
  parser = argparse.ArgumentParser(description = descr, formatter_class=argparse.RawTextHelpFormatter)
 
  parser.add_argument('-c', '--clone', help='pcraster map prototype. Mandatory', required=True)
  parser.add_argument('-n', '--ncvar', help='netcdf variable name. Mandatory', required=True)
  parser.add_argument('ncfile')
  parser.add_argument('destination_dir')

  parser.add_argument('--asc2mapcmd', help='command for asc2map', default='asc2map') 
  parser.add_argument('--tmpdir', help='temporary directry path, by default /dev/shm', default='/dev/shm/') 
  parser.add_argument('-r', '--recovery', action='store_true', help='if enabled, skips stack maps already generated and generates only the missing ones') 
  parser.add_argument('-nctimevar', help='netcdf time variable', default='time')
  parser.add_argument('-ncxvar', help='netcdf x variable', default='x')
  parser.add_argument('-ncyvar', help='netcdf y variable', default='y')
  parser.add_argument('-pcrvar', help='pcraster variable name. By default equal to the nc var name', default='')

  args = parser.parse_args()
  print('Running with the following arguments:')
  vrbls = vars(args).keys()
  vrbls.sort()
  for arg in vrbls:
    print arg, getattr(args, arg)
  return args



def netcdf2pcraster(ncFilePath, ncVarName, pcrPrototype, pcrOutDir, asc2mapcmd='asc2map', tmpdir='/dev/shm/',
                    nctimevar='time', ncxvar='x', ncyvar='y', recovery=False, pcrVarName=''):
  ndim = 3
  mapNameNChar = 11

  tmpdir1 = os.path.join(tmpdir, 'tmp')
  try:
    os.makedirs(tmpdir1)
  except Exception as exc:
    if not os.path.isdir(tmpdir1):
      raise exc
  tmpAscFilePth = os.path.join(tmpdir1, 'ascimap.txt')
  pcrVarName = ncVarName if pcrVarName == '' else pcrVarName

  if recovery:
    filePattern = pcrVarName + '([0-9]*)\.([0-9]*)'
    existingFiles = [f for f in os.listdir(pcrOutDir) if re.match(filePattern, f)]
    existingFiles.sort()
    # the last 2 files will be anyway recomputed
    existingFiles = existingFiles[:-2]
  else:
    existingFiles = []

  existingFileDict = {f: None for f in existingFiles}

  ncds = xarray.open_dataset(ncFilePath)
  try:
  
    ncvar = ncds.variables[ncVarName]
    iDimTime = ncvar.dims.index(nctimevar)
    ntime = ncvar.shape[iDimTime]
    for itime in range(ntime):
      print
      print
      print('time step ' + str(itime + 1))
  
      namePaddingLen = mapNameNChar - len(pcrVarName)
      timeStepStr = str(itime + 1).zfill(namePaddingLen)
      mapFlName = pcrVarName + timeStepStr[:-3] + '.' + timeStepStr[-3:]
      mapFlPth = os.path.join(pcrOutDir, mapFlName)

      if mapFlName in existingFileDict:
        print('  file ' + mapFlName + ' already exists. Skipping')
        continue
  
      print('  saving map ' + mapFlName + ' to path')

      print(mapFlPth)
      indx = {nctimevar: slice(itime,itime+1,None), ncxvar: slice(None), ncyvar: slice(None)}
      actMap = np.array(np.squeeze(ncvar[indx]))
      astMapStr = actMap.astype(str)
      astMapStr[astMapStr == 'nan'] = '1e31'
      np.savetxt(tmpAscFilePth, astMapStr, fmt='%s', delimiter='   ')
  
      cmd = asc2mapcmd + ' --clone ' + pcrPrototype + ' ' + tmpAscFilePth + ' ' + mapFlPth
      exst = os.system(cmd)
      if exst != 0:
        raise Exception('something wrong. Quitting')
      
    print
    print
    print('All done! Quitting')
  finally:
    try:
      shutil.rmtree(tmpdir1)
    except:
      pass
  
    ncds.close()



def main():
  args = parseArguments()
  netcdf2pcraster(args.ncfile, args.ncvar, args.clone, args.destination_dir, 
                  asc2mapcmd=args.asc2mapcmd, tmpdir=args.tmpdir, 
                  nctimevar=args.nctimevar, ncxvar=args.ncxvar, ncyvar=args.ncyvar,
                  recovery=args.recovery, pcrVarName=args.pcrvar)



if __name__ == '__main__':
  main()
  


