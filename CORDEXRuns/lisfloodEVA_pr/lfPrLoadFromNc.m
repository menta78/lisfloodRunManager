function [ tmstmp, xx, yy, vls ] = lfPrLoadFromNc( xxyyStartIndx, xxyyEndIndx, scenario, model, varargin )

args.ncRootDir = '/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/ClimateRuns/LisfloodEuroCordex/';
args.varname = 'dis';
args.ncvarname = 'dis';
args.historicalScen = 'historical';
args.cacheResults = false;
args = lfEasyParseNamedArgs(varargin, args);
ncRootDir = args.ncRootDir;
historicalScen = args.historicalScen;
cacheResults = args.cacheResults;
varname = args.varname;
ncvarname = args.ncvarname;

cachedir = 'cache';
if cacheResults && ~exist(cachedir, 'dir')
  mkdir(cachedir);
end

cacheFlNm = [model '_' scenario '_' replace(num2str(xxyyStartIndx),' ','_') '_' replace(num2str(xxyyEndIndx),' ','_') '.mat'];
cacheFlPth = fullfile(cachedir, cacheFlNm);
if exist(cacheFlPth, 'file')
  dt = load(cacheFlPth);
  tmstmp = dt.tmstmp;
  xx = dt.xx;
  yy = dt.yy;
  vls = dt.vls;
else

  disp(['  loading model ' scenario ', ' model]);
  
  disp( '    loading historical' );
  histFlPtrn = fullfile(ncRootDir, model, historicalScen, [varname '_*.nc']);
  [ htmstp, xx, yy, hvls ] = lfPrLoadFromNcOneScen(histFlPtrn, xxyyStartIndx, xxyyEndIndx, 'ncvarname', ncvarname);

  
  
  disp(['    loading ' scenario]);
  rcpFlPtrn = fullfile(ncRootDir, model, scenario, [varname '_*.nc']);
  [ rtmstp, xx, yy, rvls ] = lfPrLoadFromNcOneScen(rcpFlPtrn, xxyyStartIndx, xxyyEndIndx, 'ncvarname', ncvarname);
  
  tmstmp = cat(1, htmstp, rtmstp);
  vls = cat(3, hvls, rvls);
 %tmstmp = htmstp;
 %vls = hvls;

  if cacheResults
    disp('     serializing cache file');
    save(cacheFlPth, 'tmstmp', 'xx', 'yy', 'vls', '-v7.3');
  end

end
