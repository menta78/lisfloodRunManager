import loadTssFile
from datetime import datetime
import numpy as np

modelFlPath = '/DATA/mentalo/Dropbox/notSynced/xCarmelo/hindcast.nc'
msrsFlPath = '/DATA/mentalo/Dropbox/notSynced/xCarmelo/measures.nc'

startDate = datetime(1990, 1, 1)
endDate = datetime(2016, 1, 1)

hindTssFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/efasTss/disWin.tss'
tms, statIds, dis = loadTssFile.loadTssFile(hindTssFile, startDate=startDate)
loadTssFile.saveToNcFile(tms, statIds, dis, modelFlPath)

msrFlPath = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/validationData/newObservationsDb/Daily_Discharge_from_1950.csv'
statIdFlPath = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/validationData/newObservationsDb/EfasToC.xls'
cacheFilePath = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/validationData/newObservationsDb/Daily_Discharge_from_1950.cache'
tmsMsrs, statIdsMsrs, disMsrs = loadTssFile.loadNewObservationDataset(msrFlPath, statIdFlPath, cacheFilePath, timeHorizon=[startDate, endDate], selectStatIds=statIds)
loadTssFile.saveToNcFile(tmsMsrs, statIdsMsrs, disMsrs, msrsFlPath)

