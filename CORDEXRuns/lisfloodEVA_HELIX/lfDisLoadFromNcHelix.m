function [ tmstmp, xx, yy, vls ] = lfDisLoadFromNcHelix( xxyyStartIndx, xxyyEndIndx, model, varargin )

args.ncRootDir = '/ClimateRun4/HELIX/global/dis/output/';
args.cacheResults = false;
args = lfEasyParseNamedArgs(varargin, args);
ncRootDir = args.ncRootDir;
cacheResults = args.cacheResults;

cachedir = 'cache';
if cacheResults && ~exist(cachedir, 'dir')
  mkdir(cachedir);
end

cacheFlNm = [model '_' replace(num2str(xxyyStartIndx),' ','_') '_' replace(num2str(xxyyEndIndx),' ','_') '.mat'];
cacheFlPth = fullfile(cachedir, cacheFlNm);
if exist(cacheFlPth, 'file')
  dt = load(cacheFlPth);
  tmstmp = dt.tmstmp;
  xx = dt.xx;
  yy = dt.yy;
  vls = dt.vls;
else

  disp(['  loading model ' model]);
  
  disp( '    loading historical' );
  histFlPtrn = fullfile(ncRootDir, ['outWorld5_SMHI_' model '_hist_SSP3_7105'], 'dis.nc');
  [ htmstp, xx, yy, hvls ] = lfDisLoadFromNcOneScenHelix(histFlPtrn, xxyyStartIndx, xxyyEndIndx);
  
  
  disp(['    loading rcp85']);
  rcpFlPtrn = fullfile(ncRootDir, ['outWorld5_SMHI_' model '_hist_0620'], 'dis.nc');
  [ rtmstp, xx, yy, rvls ] = lfDisLoadFromNcOneScenHelix(rcpFlPtrn, xxyyStartIndx, xxyyEndIndx);
  
  tmstmp = cat(1, htmstp, rtmstp);
  vls = cat(3, hvls, rvls);
 %tmstmp = htmstp;
 %vls = hvls;

  if cacheResults
    disp('     serializing cache file');
    save(cacheFlPth, 'tmstmp', 'xx', 'yy', 'vls', '-v7.3');
  end

end
