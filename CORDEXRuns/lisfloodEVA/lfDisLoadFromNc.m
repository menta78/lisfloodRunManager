function [ tmstmp, xx, yy, vls ] = lfDisLoadFromNc( xxyyStartIndx, xxyyEndIndx, scenario, model, wuChanging, varargin )

args.ncRootDir = '/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/ClimateRuns/LisfloodEuroCordex/';
args.historicalScen = 'historical';
args.cacheResults = false;
args = lfEasyParseNamedArgs(varargin, args);
ncRootDir = args.ncRootDir;
historicalScen = args.historicalScen;
cacheResults = args.cacheResults;

if wuChanging
  wustr = 'wuChang';
else
  wustr = 'wuConst';
end

cachedir = 'cache';
if ~exist(cachedir, 'dir')
  mkdir(cachedir);
end

cacheFlNm = [model '_' scenario '_' wustr '_' replace(num2str(xxyyStartIndx),' ','_') '_' replace(num2str(xxyyEndIndx),' ','_') '.mat'];
cacheFlPth = fullfile(cachedir, cacheFlNm);
if exist(cacheFlPth, 'file')
  dt = load(cacheFlPth);
  tmstmp = dt.tmstmp;
  xx = dt.xx;
  yy = dt.yy;
  vls = dt.vls;
else

  disp(['  loading model ' scenario ', ' model ', ' wustr]);
  
  disp( '    loading historical' );
  histFlPtrn = fullfile(ncRootDir, historicalScen, model, 'wuConst', 'dis_*.nc');
  [ htmstp, xx, yy, hvls ] = lfDisLoadFromNcOneScen(histFlPtrn, xxyyStartIndx, xxyyEndIndx);
  
  
  disp(['    loading ' scenario]);
  rcpFlPtrn = fullfile(ncRootDir, scenario, model, wustr, 'dis_*.nc');
  [ rtmstp, xx, yy, rvls ] = lfDisLoadFromNcOneScen(rcpFlPtrn, xxyyStartIndx, xxyyEndIndx);
  
  tmstmp = cat(1, htmstp, rtmstp);
  vls = cat(3, hvls, rvls);

  if cacheResults
    disp('     serializing cache file');
    save(cacheFlPth, 'tmstmp', 'xx', 'yy', 'vls', '-v7.3');
  end

end
