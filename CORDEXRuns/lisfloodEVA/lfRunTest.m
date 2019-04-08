eosDir = '/DATA/JEODPP/eos/projects/CRITECH/';
%eosDir = '/mnt/cidstorage_mentalo_eos/projects/CRITECH/';
%ncRootDir = fullfile(eosDir, 'ADAPTATION/ClimateRuns/LisfloodEuroCordex/');
ncRootDir = fullfile('/DATA/ClimateRuns/lisflood_eva_test');

nParWorker = 1;
dx = 250;
dy = 300;
%dx = 100;
%dy = 100;

if nParWorker > 1
  parObj = parpool(nParWorker);
  parObj.IdleTimeout = 120;
else
  parObj = -1;
end

%model = 'CLMcom-CCLM4-8-17_BC_ICHEC-EC-EARTH';
%model = 'CLMcom-CCLM4-8-17_BC_MPI-M-MPI-ESM-LR';
%model = 'IPSL-INERIS-WRF331F_BC';
model = 'SMHI-RCA4_BC_MOHC-HadGEM2-ES';
scenario = 'rcp85';
varname = 'dis';
ncvarname = 'dis';
%varname = 'wl';
%ncvarname = 'wl';

%scenario = 'rcp45';
%wuChanging = false;
wuChanging = true;
outDir = './test';
lfEvaModel(scenario, model, wuChanging, outDir, 'ncRootDir', ncRootDir, 'nParWorker', nParWorker, 'varname', varname, 'ncvarname', ncvarname, 'parObj', parObj, 'dx', dx, 'dy', dy);

delete(parObj);
