import os, sys, shutil, time
import pickle
import netCDF4
libpath = os.path.join( os.path.dirname(os.path.abspath(__file__)), '..' )
sys.path.append(libpath)
from datetime import datetime
from dateutil.relativedelta import relativedelta
from lfLaunchOneCORDEX import _iniObj
import lfJeodppLogFileParser


generateColdSettingsFileAndQuit = False



runDirRoot = '/eos/jeodpp/data/projects/CRITECH/ADAPTATION/lisflood/run'
outDir = '/eos/jeodpp/data/projects/CRITECH/ADAPTATION/ClimateRuns/LisfloodEuroCordex'
coldInitDir = '/eos/jeodpp/data/projects/CRITECH/ADAPTATION/lisflood/coldInit'
rootConfDir = '/eos/jeodpp/data/projects/CRITECH/ADAPTATION/lisflood/lisfloodRun/LisfloodEurope'
py = '/eos/jeodpp/data/projects/CRITECH/miniconda3/envs/LISFLOOD/bin/python'
lisfloodpy = '/eos/jeodpp/data/projects/CRITECH/ADAPTATION/src/git/lisflood/Lisflood/lisf1.py'
lisfloodcmd = '{python} {lisflood}'.format(python=py, lisflood=lisfloodpy)

scenarios = ['historical', 'rcp85', 'rcp45']  

dtReWarmUp = relativedelta(months = 1)

def launchAll(scenarios=scenarios, outDir=outDir, runDirRoot=runDirRoot, dtReWarmUp=dtReWarmUp, preliminaryRun=False):
  meteoDataDirectory = '/eos/jeodpp/data/projects/CRITECH/ADAPTATION/lisflood/input/LAEAETRS89_BIAS_CORDEX'
  runDir = os.path.join(runDirRoot, 'conf')
  initDir = os.path.join(runDirRoot, 'init')
  tmpOutDir = os.path.join(runDirRoot, 'tmpout')

  models = """
IPSL-INERIS-WRF331F_BC
SMHI-RCA4_BC_CNRM-CERFACS-CNRM-CM5
SMHI-RCA4_BC_ICHEC-EC-EARTH
SMHI-RCA4_BC_IPSL-IPSL-CM5A-MR
SMHI-RCA4_BC_MOHC-HadGEM2-ES
SMHI-RCA4_BC_MPI-M-MPI-ESM-LR
CLMcom-CCLM4-8-17_BC_CNRM-CERFACS-CNRM-CM5
CLMcom-CCLM4-8-17_BC_ICHEC-EC-EARTH
CLMcom-CCLM4-8-17_BC_MPI-M-MPI-ESM-LR
DMI-HIRHAM5-ICHEC-EC-EARTH_BC
KNMI-RACMO22E-ICHEC-EC-EARTH_BC
"""
  models = [m.strip(' \n\t\r') for m in models.strip(' \n\t\r').split('\n') if m.strip(' \n\t\r')]
 # READ THE CALENDARS DIRECTLY FROM THE FILES

  calendarDayStartByScen = {
    'historical': datetime(1981, 1, 1),
    'rcp85': datetime(2011, 1, 1),
    'rcp45': datetime(2011, 1, 1)
    }
  calendarDayEndByScen = {
    'historical': datetime(2010, 12, 31),
    'rcp85': datetime(2099, 12, 31),
    'rcp45': datetime(2099, 12, 31)
    }

  wuChang = [True, False]
  wuChangDataPathRoot = '/eos/jeodpp/data/projects/CRITECH/ADAPTATION/lisflood/input/waterdemandCordex/cordex'
  wuChangDataPath = {
    ('historical', False): os.path.join(wuChangDataPathRoot, 'hist/waterdemand2010'),
    ('rcp85', True): os.path.join(wuChangDataPathRoot, 'rcp/dynamic'),
    ('rcp85', False): os.path.join(wuChangDataPathRoot, 'rcp/static/waterdemand2010'),
    ('rcp45', True): os.path.join(wuChangDataPathRoot, 'rcp/dynamic'),
    ('rcp45', False): os.path.join(wuChangDataPathRoot, 'rcp/static/waterdemand2010'),
    }
  landUseDataPathRoot = '/eos/jeodpp/data/projects/CRITECH/ADAPTATION/lisflood/lisfloodRun/LisfloodEurope/maps_netcdf/landuse/cordex'
  staticLandUseDir = os.path.join(landUseDataPathRoot, 'hist/landuse2010')
  landUseDataPath = {
    ('historical', False): staticLandUseDir,
    ('rcp85', True): os.path.join(landUseDataPathRoot, 'rcp'),
    ('rcp85', False): staticLandUseDir,
    ('rcp45', True): os.path.join(landUseDataPathRoot, 'rcp'),
    ('rcp45', False): staticLandUseDir,
    }
  directRunoffFractionMaps = {
    ('historical', False): os.path.join(landUseDataPath[('historical', False)], 'fracsealed'),
    ('rcp85', False): os.path.join(landUseDataPath[('rcp85', False)], 'fracsealed'),
    ('rcp85', True, 'proleptic_gregorian'): os.path.join(landUseDataPath[('rcp85', True)], 'fracsealed/frsealed_2011_2099'),
    ('rcp85', True, '360_day'): os.path.join(landUseDataPath[('rcp85', True)], 'fracsealed_360Day/frsealed_2011_2099_360day'),
    ('rcp85', True, '365_day'): os.path.join(landUseDataPath[('rcp85', True)], 'fracsealed_365Day/frsealed_2011_2099_365day'),
    ('rcp45', False): os.path.join(landUseDataPath[('rcp45', False)], 'fracsealed'),
    ('rcp45', True, 'proleptic_gregorian'): os.path.join(landUseDataPath[('rcp45', True)], 'fracsealed/frsealed_2011_2099'),
    ('rcp45', True, '360_day'): os.path.join(landUseDataPath[('rcp45', True)], 'fracsealed_360Day/frsealed_2011_2099_360day'),
    ('rcp45', True, '365_day'): os.path.join(landUseDataPath[('rcp45', True)], 'fracsealed_365Day/frsealed_2011_2099_365day'),
    }
  forestFractionMaps = {
    ('historical', False): os.path.join(landUseDataPath[('historical', False)], 'fracforest'),
    ('rcp85', False): os.path.join(landUseDataPath[('rcp85', False)], 'fracforest'),
    ('rcp85', True, 'proleptic_gregorian'): os.path.join(landUseDataPath[('rcp85', True)], 'fracforest/frforet_2011_2099'),
    ('rcp85', True, '360_day'): os.path.join(landUseDataPath[('rcp85', True)], 'fracforest_360Day/frforet_2011_2099_360day'),
    ('rcp85', True, '365_day'): os.path.join(landUseDataPath[('rcp85', True)], 'fracforest_365Day/frforet_2011_2099_365day'),
    ('rcp45', False): os.path.join(landUseDataPath[('rcp45', False)], 'fracforest'),
    ('rcp45', True, 'proleptic_gregorian'): os.path.join(landUseDataPath[('rcp45', True)], 'fracforest/frforet_2011_2099'),
    ('rcp45', True, '360_day'): os.path.join(landUseDataPath[('rcp45', True)], 'fracforest_360Day/frforet_2011_2099_360day'),
    ('rcp45', True, '365_day'): os.path.join(landUseDataPath[('rcp45', True)], 'fracforest_365Day/frforet_2011_2099_365day'),
    }
  waterFractionMaps = {
    ('historical', False): os.path.join(landUseDataPath[('historical', False)], 'fracwater'),
    ('rcp85', False): os.path.join(landUseDataPath[('rcp85', False)], 'fracwater'),
    ('rcp85', True): os.path.join(landUseDataPath[('rcp85', True)], 'fracwater/frwater_2011_2099'),
    ('rcp45', False): os.path.join(landUseDataPath[('rcp45', False)], 'fracwater'),
    ('rcp45', True): os.path.join(landUseDataPath[('rcp45', True)], 'fracwater/frwater_2011_2099'),
    }
  otherFractionMaps = {
    ('historical', False): os.path.join(landUseDataPath[('historical', False)], 'fracother'),
    ('rcp85', False): os.path.join(landUseDataPath[('rcp85', False)], 'fracother'),
    ('rcp85', True, 'proleptic_gregorian'): os.path.join(landUseDataPath[('rcp85', True)], 'fracother/frother_2011_2099'),
    ('rcp85', True, '360_day'): os.path.join(landUseDataPath[('rcp85', True)], 'fracother_360Day/frother_2011_2099_360day'),
    ('rcp85', True, '365_day'): os.path.join(landUseDataPath[('rcp85', True)], 'fracother_365Day/frother_2011_2099_365day'),
    ('rcp45', False): os.path.join(landUseDataPath[('rcp45', False)], 'fracother'),
    ('rcp45', True, 'proleptic_gregorian'): os.path.join(landUseDataPath[('rcp45', True)], 'fracother/frother_2011_2099'),
    ('rcp45', True, '360_day'): os.path.join(landUseDataPath[('rcp45', True)], 'fracother_360Day/frother_2011_2099_360day'),
    ('rcp45', True, '365_day'): os.path.join(landUseDataPath[('rcp45', True)], 'fracother_365Day/frother_2011_2099_365day'),
    }
  irrigationFractionMaps = {
    ('historical', False): os.path.join(landUseDataPath[('historical', False)], 'fracirrigated'),
    ('rcp85', False): os.path.join(landUseDataPath[('rcp85', False)], 'fracirrigated'),
    ('rcp85', True): os.path.join(landUseDataPath[('rcp85', True)], 'fracirrigated/frirrig_2011_2099'),
    ('rcp45', False): os.path.join(landUseDataPath[('rcp45', False)], 'fracirrigated'),
    ('rcp45', True): os.path.join(landUseDataPath[('rcp45', True)], 'fracirrigated/frirrig_2011_2099'),
    }
  riceFractionMaps = {
    ('historical', False): os.path.join(landUseDataPath[('historical', False)], 'fracrice'),
    ('rcp85', False): os.path.join(landUseDataPath[('rcp85', False)], 'fracrice'),
    ('rcp85', True): os.path.join(landUseDataPath[('rcp85', True)], 'fracrice/fracrice_2011_2099'),
    ('rcp45', False): os.path.join(landUseDataPath[('rcp45', False)], 'fracrice'),
    ('rcp45', True): os.path.join(landUseDataPath[('rcp45', True)], 'fracrice/fracrice_2011_2099'),
    }

  prefixWaterUseDomestic = {
    'proleptic_gregorian': 'dom',
    '360_day': 'dom_360Day',
    '365_day': 'dom_365Day'
    }
  prefixWaterUseLivestock = {
    'proleptic_gregorian': 'liv',
    '360_day': 'liv_360Day',
    '365_day': 'liv_365Day'
    }
  prefixWaterUseEnergy = {
    'proleptic_gregorian': 'ene',
    '360_day': 'ene_360Day',
    '365_day': 'ene_365Day'
    }
  prefixWaterUseIndustry = {
    'proleptic_gregorian': 'ind',
    '360_day': 'ind_360Day',
    '365_day': 'ind_365Day'
    }
  

  def getCalendar(meteoDataPath):
    testNcFile = os.path.join(meteoDataPath, 'pr.nc')
    ds = netCDF4.Dataset(testNcFile)
    try:
      calendar = ds.variables['time'].calendar
    except:
      calendar = 'proleptic_gregorian'  
    ds.close() 
    return calendar
 

  def getMapPath(dctnr, scen, useWater, calendar):
    key1 = (scen, useWater, calendar)
    key2 = (scen, useWater)
    return dctnr.get(key1, dctnr.get(key2, ''))


 #import pdb; pdb.set_trace()
  for scen in scenarios:
    for currWuChang in wuChang:
      for mdl in models:
        if scen == 'historical' and currWuChang:
          print('')
          continue
        calendarDayStart = calendarDayStartByScen[scen]
        calendarDayEnd = calendarDayEndByScen[scen]
        meteoDataPath = os.path.join(meteoDataDirectory, mdl, scen)

        # checking meteo input
        e0FlPth = os.path.join(meteoDataPath, 'e0.nc')
        etFlPth = os.path.join(meteoDataPath, 'et.nc')
        if not (os.path.isfile(e0FlPth) and os.path.isfile(etFlPth)):
          print('        METEO FILES NOT READY. SKIPPING')
          continue

        calendar = getCalendar(meteoDataPath)
        curWaterDataPath = wuChangDataPath[(scen, currWuChang)]
        curLandUseDataPath = landUseDataPath[(scen, currWuChang)]
        cDirectRunoffFractionMaps = getMapPath(directRunoffFractionMaps, scen, currWuChang, calendar)
        cForestFractionMaps = getMapPath(forestFractionMaps, scen, currWuChang, calendar)
        cWaterFractionMaps = getMapPath(waterFractionMaps, scen, currWuChang, calendar)
        cOtherFractionMaps = getMapPath(otherFractionMaps, scen, currWuChang, calendar)
        cIrrigationFractionMaps = getMapPath(irrigationFractionMaps, scen, currWuChang, calendar)
        cRiceFractionMaps = getMapPath(riceFractionMaps, scen, currWuChang, calendar)
        cPoulationMap = os.path.join(curWaterDataPath, 'pop')
        cPrefixWaterUseDomestic = prefixWaterUseDomestic[calendar]
        cPrefixWaterUseLivestock = prefixWaterUseLivestock[calendar]
        cPrefixWaterUseEnergy = prefixWaterUseEnergy[calendar]
        cPrefixWaterUseIndustry = prefixWaterUseIndustry[calendar]

        miscVars = {
          'preliminaryRun': preliminaryRun,
          'dtReWarmUp': dtReWarmUp,
          'meteoDir': meteoDataPath,
          'waterUsDir': curWaterDataPath,
          'landUseDir': curLandUseDataPath,
          'directRunoffFractionMaps': cDirectRunoffFractionMaps,
          'forestFractionMaps': cForestFractionMaps,
          'waterFractionMaps': cWaterFractionMaps,
          'otherFractionMaps': cOtherFractionMaps,
          'irrigationFractionMaps': cIrrigationFractionMaps,
          'riceFractionMaps': cRiceFractionMaps,
          'populationMaps': cPoulationMap,
          'prefixWaterUseDomestic': cPrefixWaterUseDomestic,
          'prefixWaterUseLivestock': cPrefixWaterUseLivestock,
          'prefixWaterUseEnergy': cPrefixWaterUseEnergy,
          'prefixWaterUseIndustry': cPrefixWaterUseIndustry
          }
        launchSingleModel(scen, mdl, calendarDayStart, calendarDayEnd, calendar, currWuChang, miscVars,
                         outDir=outDir, runDirRoot=runDirRoot)
        pass



def launchSingleModel(scen, mdl, calendarDayStart, calendarDayEnd, calendar, wuChang, miscVars, 
                     outDir=outDir, runDirRoot=runDirRoot):
  runDir = os.path.join(runDirRoot, 'conf')
  initDir = os.path.join(runDirRoot, 'init')
  tmpOutDir = os.path.join(runDirRoot, 'tmpout')
  calUnitStr = 'days since ' + calendarDayStart.strftime('%Y-%m-%d')
  try:
    stepEnd = netCDF4.date2num(calendarDayEnd, calUnitStr, calendar)
  except:
    stepEnd = netCDF4.date2num(calendarDayEnd-relativedelta(days=1), calUnitStr, calendar)
  stepEnd = int(stepEnd) + 1

  print('')
  print('  preparing to launch model: {scen} - {mdl} - wuChang=={wuChang} - calendar=={cal}'.format(
          scen=scen, mdl=mdl, wuChang=str(wuChang), cal=calendar))
  print('  stepStart == ' + calendarDayStart.strftime('%Y-%m-%d'))
  print('  stepEnd == ' + str(stepEnd))
  print('  map miscVars:')
  ks = miscVars.keys()
  ks.sort()
  for m in ks:
    print('    ' + m + ': ' + str(miscVars[m]))
  
  wUseStr = 'wuChang' if wuChang else 'wuConst'
  if generateColdSettingsFileAndQuit:
    from lisfloodRunManager import lisfloodRunManager
    runDirDiag = os.path.join(runDir, 'diagnostics')
    mng = lisfloodRunManager(initDir, runDirDiag, tmpOutDir, outDir,
            rootConfDir, wuChang, calendarDayStart, calendarDayEnd, calendar, lisfloodcmd, miscVars, verbose=False)
    flpath = mng.compileTemplate()
    nflpath = flpath + '_' + wUseStr + '_' + scen + '_' + mdl + '.xml'
    shutil.move(flpath, nflpath)
    return
  else:
    runDirMdl = os.path.join(runDir, scen, mdl, wUseStr)
    try:
      os.makedirs(runDirMdl)
    except:
      pass

    initDirMdl = os.path.join(initDir, scen, mdl, wUseStr)
    try:
      os.makedirs(initDirMdl)
    except:
      pass
    
    tmpOutDirMdl = os.path.join(tmpOutDir, scen, mdl, wUseStr)
    try:
      os.makedirs(tmpOutDirMdl)
    except:
      pass

    outDirMdl = os.path.join(outDir, scen, mdl, wUseStr)
    try:
      os.makedirs(outDirMdl)
    except:
      pass

    coldInitDirMdl = os.path.join(coldInitDir, scen, mdl, wUseStr)
    try:
      os.makedirs(coldInitDirMdl)
    except:
      pass
    miscVars['pathInitCold'] = coldInitDirMdl

    rootConfDirMdl = rootConfDir
    logDir = '/eos/jeodpp/htcondor/processing_logs/CRITECH/lisflood/'

    jobAlive, jobId = lfJeodppLogFileParser.jobIsAlive(mdl, scen, wUseStr, logDir)
    if jobAlive:
      print('       Alive run (job id == ' + str(jobId) + '). Skipping')
      return
    
    ii = _iniObj()
    ii.runDirMdl = runDirMdl
    ii.initDirMdl = initDirMdl
    ii.tmpOutDirMdl = tmpOutDirMdl
    ii.outDirMdl = outDirMdl
    ii.rootConfDirMdl = rootConfDirMdl
    ii.wuChang = wuChang
    ii.scen = scen
    ii.mdl = mdl
    ii.calendarDayStart = calendarDayStart
    ii.calendarDayEnd = calendarDayEnd
    ii.calendar = calendar
    ii.miscVars = miscVars
    jobInitFlPth = os.path.join(runDirMdl, 'init.pkl')
    with open(jobInitFlPth, 'w') as ifl:
      pickle.dump(ii, ifl)
      ifl.close()
   
    cdir = os.path.dirname(os.path.abspath(__file__))
    condorJobExecutable = os.path.join(cdir, 'lfLaunchOneCORDEX.sh')
    condorConfDir = runDirMdl
    condorSubTemplateFile = os.path.join(cdir, '../template/lisfloodCondorSubmit.sh')
    with open(condorSubTemplateFile) as ctf:
      condorSubScrptTxt = ctf.read()
    tagstr = '_'.join(['lisflood', wUseStr, scen, mdl])
    condorSubScrptTxt = condorSubScrptTxt.replace('@CONF_DIR@', runDirMdl)
    condorSubScrptTxt = condorSubScrptTxt.replace('@EXECUTABLE@', condorJobExecutable)
    condorSubScrptTxt = condorSubScrptTxt.replace('@JOB_TAG@', tagstr) 
    condorSubScrptFile = os.path.join(runDirMdl, 'run_' + tagstr + '.sh')
    with open(condorSubScrptFile, 'w') as cst:
      cst.write(condorSubScrptTxt)
      cst.close()
    os.system('chmod a+x ' + condorSubScrptFile)
    #CONDOR SUBMIT
    os.system('condor_submit -disable ' + condorSubScrptFile)
   #time.sleep(45)
   #time.sleep(600)
    time.sleep(120)
    


if __name__ == '__main__':
  launchAll()


