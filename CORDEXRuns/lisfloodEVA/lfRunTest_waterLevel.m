eosDir = '/DATA/JEODPP/eos/projects/CRITECH/';
%eosDir = '/mnt/cidstorage_mentalo_eos/projects/CRITECH/';
ncRootDir = fullfile(eosDir, 'ADAPTATION/ClimateRuns/LisfloodEuroCordex/');
%ncRootDir = fullfile('/ADAPTATION/mentalo/ClimateRuns/LisfloodEuroCordex/');

nParWorker = 6;

model = 'CLMcom-CCLM4-8-17_BC_ICHEC-EC-EARTH';
scenario = 'rcp85';
%scenario = 'rcp45';
wuChanging = false;
outDir = './test';
lfEvaModel(scenario, model, wuChanging, outDir, 'ncRootDir', ncRootDir, 'nParWorker', nParWorker, 'varname', 'wl', 'ncvarname', 'wl');
