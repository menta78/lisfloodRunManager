addpath('/STORAGE/src1/git/tsEva/');
model = 'CLMcom-CCLM4-8-17_BC_ICHEC-EC-EARTH';
scenario = 'rcp85';
wuChanging = false;
outDir = './test';
ncRootDir = '/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/ClimateRuns/LisfloodEuroCordex/';
lfEvaModel(scenario, model, wuChanging, outDir, 'ncRootDir', ncRootDir);