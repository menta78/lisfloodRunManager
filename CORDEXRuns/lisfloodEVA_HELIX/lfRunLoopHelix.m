ncRootDir = '/ClimateRun4/HELIX/global/dis/output/';

models = {'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7'};
nmdl = length(models);

nParWorker = 6;
%dx = 250;
%dy = 300;
dx = 240;
dy = 120;

try
  if nParWorker > 1
    parObj = parpool(nParWorker);
    parObj.IdleTimeout = 120;
  else
    parObj = -1;
  end
catch
end
scenario = 'rcp85';
outDir = './test';

for imdl = 1:nmdl
  model = models{imdl};
  
  lfEvaModelHelix(scenario, model, outDir, 'ncRootDir', ncRootDir, 'nParWorker', nParWorker, 'parObj', parObj, 'dx', dx, 'dy', dy);
end

delete(parObj);
