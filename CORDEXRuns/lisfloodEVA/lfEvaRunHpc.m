function lfEvaRunHpc(models, nParWorker)

distcomp.feature( 'LocalUseMpiexec', false );

models = strsplit(models, ':');
if ischar(nParWorker)
  nParWorker = str2double(nParWorker);
end
scenarios = {'rcp85', 'rcp45'};
%wuChangingSet = {true, false};
wuChangingSet = {true};

tsEvaTimeWindow = 30*365.25; % 30 years

ncRootDir = fullfile('/ADAPTATION/mentalo/ClimateRuns/LisfloodEuroCordex/');

nmdl = length(models);
nscen = length(scenarios);
nwuchng = length(wuChangingSet);

parObj = parpool(nParWorker);
try
  for iwuchng = 1:nwuchng
    for imdl = 1:nmdl
      for iscen = 1:nscen
        model = models{imdl};
        scenario = scenarios{iscen};
        wuChanging = wuChangingSet{iwuchng};
        disp('#####################################');
        disp('#####################################');
        disp('#####################################');
        disp('#####################################');
        disp(['PROCESSING MODEL, SCENARIO, WUCHANG ' model ', ' scenario ', ' num2str(wuChanging)]);
        outDir = './output';
        lfEvaModel(scenario, model, wuChanging, outDir, 'ncRootDir', ncRootDir, 'nParWorker', nParWorker, 'tsEvaTimeWindow', tsEvaTimeWindow, 'parObj', parObj);
        disp('#####################################');
        disp('#####################################');
        disp('#####################################');
      end
    end
  end
catch exc
  delete(parObj);
  rethrow(exc);
end
delete(parObj);
