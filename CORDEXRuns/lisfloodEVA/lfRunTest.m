eosDir = 'DATA/JEODPP/eos/projects';
eosDir = '/ADAPTATION/mentalo/JEODPP/EOS/projects';

addpath('/STORAGE/src1/git/tsEva/');
model = 'CLMcom-CCLM4-8-17_BC_ICHEC-EC-EARTH';
scenario = 'rcp85';
%scenario = 'rcp45';
wuChanging = false;
outDir = './test';
ncRootDir = fullfile(eosDir, '/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/ClimateRuns/LisfloodEuroCordex/');
lfEvaModel(scenario, model, wuChanging, outDir, 'ncRootDir', ncRootDir);
