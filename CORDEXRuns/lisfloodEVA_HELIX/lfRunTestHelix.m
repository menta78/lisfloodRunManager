ncRootDir = '/ClimateRun4/HELIX/global/dis/output/';

nParWorker = 1;
%dx = 250;
%dy = 300;
dx = 100;
dy = 101;

if nParWorker > 1
  parObj = parpool(nParWorker);
  parObj.IdleTimeout = 120;
else
  parObj = -1;
end

%model = 'CLMcom-CCLM4-8-17_BC_ICHEC-EC-EARTH';
%model = 'CLMcom-CCLM4-8-17_BC_MPI-M-MPI-ESM-LR';
%model = 'IPSL-INERIS-WRF331F_BC';
model = 'r1';
scenario = 'rcp85';

outDir = './test';
lfEvaModelHelix(scenario, model, outDir, 'ncRootDir', ncRootDir, 'nParWorker', nParWorker, 'parObj', parObj, 'dx', dx, 'dy', dy);

delete(parObj);
