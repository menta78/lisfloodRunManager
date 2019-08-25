ncRootDir = '/DATA/ClimateData/cordexEurope/prYearlyMax'

nParWorker = 1;
dx = 500;
dy = 475;
%dx = 100;
%dy = 101;

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
varname = 'pr';
ncvarname = 'pr';

%scenario = 'rcp45';
outDir = './test';
lfEvaModel_pr(scenario, model, outDir, 'ncRootDir', ncRootDir, 'nParWorker', nParWorker, 'varname', varname, 'ncvarname', ncvarname, 'parObj', parObj, 'dx', dx, 'dy', dy);

delete(parObj);
