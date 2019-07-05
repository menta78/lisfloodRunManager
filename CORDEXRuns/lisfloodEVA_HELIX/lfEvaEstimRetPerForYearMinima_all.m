%function lfEvaEstimRetPerForYearMinima_all

inputDir = '/ClimateRun4/multi-hazard/eva/';
inputFlPattern = 'projection_dis_rcp*_*_wuChang_statistics.nc';
%inputFlPattern = 'projection_dis_rcp*_SMHI-RCA4_BC_MOHC-HadGEM2-ES_wuChang_statistics.nc';
outputDir = '/ClimateRun4/multi-hazard/eva/minDischargeExtremesRetPer/';
outputDir = '/ClimateRun/menta/xCarmelo/minDischargeExtremesRetPer/';

fls = strsplit(strtrim(ls(fullfile(inputDir, inputFlPattern))));
nfls = length(fls);

%pl = parpool(min(nfls, 4));

%parfor ifl = 1:nfls
for ifl = 1:nfls
  fl = fls{ifl};
  re = regexp(fl, '(.*)/projection_dis_rcp([48])5_(.*)_wuChang_statistics.nc', 'tokens');
  scen = ['rcp' re{1}{2} '5'];
  mdl = re{1}{3};
  disp(['elaborating file ' fl]);
  disp(['scenario = ' scen]);
  disp(['model = ' mdl]);
  
  outFl = fullfile(outputDir, ['projection_disMinRp_' scen '_' mdl '_wuChang_statistics.nc']);
  disp(['  out file: ' outFl]);
  
  lfEvaEstimRetPerForYearMinima(fl, outFl);
end

delete(pl);
