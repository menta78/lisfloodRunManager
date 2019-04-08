function lfMinDisStatEVA

gevType = 'gev';
returnPeriodsInYears = [1.5 2 3 4 5 7 10 15 20 30 50 70 100 150 250 350 500 700 1000 1500 2000];
nParWorker = 12;
%nParWorker = 1;

%flPathHindcast = '/DATA/lisfloodHindcast/dis_monmin.nc';
%flPathHindcast = '/DATA/lisfloodHindcast/dis_monmean.nc';
%flPathHindcast = '/DATA/lisfloodHindcast/dis_mon7dmin.nc';
flPathHindcast = '/DATA/lisfloodHindcast/dis_mon14dmin.nc';

lonlatfile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/lonlat.nc';

lon = ncread(lonlatfile, 'lon');
lat = ncread(lonlatfile, 'lat');

outDir = '/ClimateRun4/multi-hazard/eva/';
mkdir(outDir);
%ncYearEvaFilePath = fullfile(outDir, 'historical_dis_min_NCEP_year_statistics.nc');
%ncYearEvaFilePath = fullfile(outDir, 'historical_dis_monMeanMin_NCEP_year_statistics.nc');
%ncYearEvaFilePath = fullfile(outDir, 'historical_dis_mon7dMeanMin_NCEP_year_statistics.nc');
ncYearEvaFilePath = fullfile(outDir, 'historical_dis_mon14dMeanMin_NCEP_year_statistics.nc');

disp('loading the data ...');
xx = ncread(flPathHindcast, 'x');
yy = ncread(flPathHindcast, 'y');
tm = jrc_ncreadtime(flPathHindcast, 'time');
vlsall = ncread(flPathHindcast, 'dis');
vlsall = permute(vlsall, [3,1,2]);
vlsymin = -tsEvaComputeAnnualMaximaMtx(tm, -vlsall);
yyrs = unique(tsYear(tm));
ydtm = datenum([yyrs ones(size(yyrs)) ones(size(yyrs))]);
disp('done');

if nParWorker > 1
  parObj = parpool(nParWorker);
else
  parObj = -1;
end
try
 % evaDataYr = lfStationaryEva(lon, lat, -vlsall, tm, returnPeriodsInYears, 'parObj', parObj, 'gevType', gevType);
  evaDataYr = lfStationaryEva(xx, yy, -vlsymin, ydtm, returnPeriodsInYears, 'parObj', parObj, 'gevType', gevType);
  evaDataYr.retLevGEV = -evaDataYr.retLevGEV;
  evaDataYr.le = -evaDataYr.le;
  lfStatEvaWriteOutNcFile(xx, yy, returnPeriodsInYears, yyrs, evaDataYr, lon, lat, ncYearEvaFilePath);
catch err
  if parObj ~= -1
    delete(parObj);
  end
  rethrow(err);
end
if parObj ~= -1
  delete(parObj);
end






