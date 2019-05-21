function lfEvaModel(scenario, model, wuChanging, outDir, varargin)

args.nparworker = 12;
args.skipExistingFiles = true;
args.varname = 'dis';
args.dx = 250;
args.dy = 320;
args = lfEasyParseNamedArgs(varargin, args);
nparworker = args.nparworker;
skipExistingFiles = args.skipExistingFiles;
varname = args.varname;
dx = args.dx;
dy = args.dy;

returnPeriodsInYears = [1.5 2 3 4 5 7 10 15 20 30 50 70 100 150 250 350 500 700 1000 1500 2000];  
outYears = (1985:5:2095)';
outYears = cat(1, 1981, outYears);
outYears = cat(1, outYears, 2099);
% outYears = (1981:1:2100)';
allYears = (min(outYears):max(outYears))';

channelMapFl = './maps/channels_5km.nc';

if wuChanging
  wustr = 'wuChang';
else
  wustr = 'wuConst';
end

channelMap = ncread(channelMapFl, 'channels');
%channelMap = channelMap';
channelMap(isnan(channelMap)) = false;

retLevNcFlName = [strjoin({'projection', varname, scenario, model, wustr, 'statistics'}, '_') '.nc'];
retLevNcOutFilePath = fullfile(outDir, retLevNcFlName);

[nx, ny] = size(channelMap);
nretper = length(returnPeriodsInYears);
nyrout = size(outYears, 1);
nyrall = size(allYears, 1);

% this procedure will analyze 120x60 windows, to avoid using too much
% memory
%  dx = 100;
%  dy = 100;
% dx = 250;
% dy = 320;
%dx = 250;
%dy = 249;

% if nparworker > 1
%   parObj = parpool(nparworker);
% else
%   parObj = -1;
% end

try
    
  if exist(retLevNcOutFilePath, 'file') && skipExistingFiles
    disp(['          file ' retLevNcOutFilePath ' already exists. Skipping']);
    return;
  end

  disp('allocating output ...');
  retLevGPD = ones(ny, nx, nyrout, nretper)*nan;
  retLevErrGPD = ones(ny, nx, nyrout, nretper)*nan;
  shapeGPD = ones(ny, nx)*nan;
  shapeGPDErr = ones(ny, nx)*nan;
  scaleGPD = ones(ny, nx, nyrout)*nan;
  scaleGPDErr = ones(ny, nx, nyrout)*nan;
  thresholdGPD = ones(ny, nx, nyrout)*nan;
  thresholdGPDErr = ones(ny, nx, nyrout)*nan;
  yMax = ones(ny, nx, nyrall)*nan;

  retLevGEVMin = ones(ny, nx, nyrout, nretper)*nan;
  retLevErrGEVMin = ones(ny, nx, nyrout, nretper)*nan;
  shapeGEVMin = ones(ny, nx)*nan;
  shapeGEVErrMin = ones(ny, nx)*nan;
  scaleGEVMin = ones(ny, nx, nyrout)*nan;
  scaleGEVErrMin = ones(ny, nx, nyrout)*nan;
  locationGEVMin = ones(ny, nx, nyrout)*nan;
  locationGEVErrMin = ones(ny, nx, nyrout)*nan;
  yMin = ones(ny, nx, nyrall)*nan;
  
  yMean = ones(ny, nx, nyrall)*nan;

  nsubx = ceil(nx/dx);
  nsuby = ceil(ny/dy);
  xx = ones(nx, 1)*nan;
  yy = ones(ny, 1)*nan;
  
  wholeTicToc = tic;
  
  for isubx = 1:nsubx
    for isuby = 1:nsuby
%  for isubx = 7:7
%    for isuby = 5:5
      fprintf('\n');
      disp(['elaborating sub area ' num2str(isubx) ', ' num2str(isuby)]);
      iLonStart = (isubx - 1)*dx + 1;
      iLonEnd = min(isubx*dx, nx);
      iLatStart = (isuby - 1)*dy + 1;
      iLatEnd = min(isuby*dy, ny);
      disp(['iLonStart, iLonEnd = ' num2str(iLonStart) ', ' num2str(iLonEnd)]);
      disp(['iLatStart, iLatEnd = ' num2str(iLatStart) ', ' num2str(iLatEnd)]);
      
      tic;
      channelMap_ = channelMap(iLonStart:iLonEnd, iLatStart:iLatEnd);
      [ tmstmp, xx_, yy_, vls ] = lfDisLoadFromNc( [iLonStart iLatStart], [iLonEnd iLatEnd], scenario, model, wuChanging, varargin{:} );
     %evaData = lfExecuteTsEva( tmstmp, xx_, yy_, vls, outYears, returnPeriodsInYears, channelMap_, 'parObj', parObj );
      evaDataMax = lfExecuteTsEva( tmstmp, xx_, yy_, vls, outYears, returnPeriodsInYears, channelMap_, 'nWorker', nparworker, varargin{:} );

      vlsmn = movmean(vls, 30, 3);
      vlsmnmin_ = permute(tsEvaComputeAnnualMaximaMtx(tmstmp, permute(-vlsmn, [3,1,2])), [2,3,1]);
      yys = unique(tsYear(tmstmp));
      yydt = datenum([yys, ones(size(yys)), ones(size(yys))]);
      evaDataMin = lfExecuteTsEvaGEV( yydt, xx_, yy_, vlsmnmin_, outYears, returnPeriodsInYears, channelMap_, 'nWorker', nparworker, 'maxFracNan', .1, varargin{:} );
      retLevGEVMin_ = -evaDataMin.retLevGEV;
      cnd0 = retLevGEVMin_ < 0;
      retLevGEVMin_(cnd0) = 0;
      evaDataMin.retLevErrGEV(cnd0) = 0;
      
      vlsYMean = tsEvaComputeAnnualMeanMtx(tmstmp, permute(vls, [3, 1, 2]));
      vlsYMean = permute(vlsYMean, [3, 2, 1]);
      
      fprintf('\n');
      toc;
      disp('eva on chunk complete. Assigning results to the final output')
      retLevGPD(iLatStart:iLatEnd, iLonStart:iLonEnd, :, :) = evaDataMax.retLevGPD;
      retLevErrGPD(iLatStart:iLatEnd, iLonStart:iLonEnd, :, :) = evaDataMax.retLevErrGPD;
      shapeGPD(iLatStart:iLatEnd, iLonStart:iLonEnd) = evaDataMax.shapeGPD;
      shapeGPDErr(iLatStart:iLatEnd, iLonStart:iLonEnd, :) = evaDataMax.shapeGPDErr;
      scaleGPD(iLatStart:iLatEnd, iLonStart:iLonEnd, :) = evaDataMax.scaleGPD;
      scaleGPDErr(iLatStart:iLatEnd, iLonStart:iLonEnd, :) = evaDataMax.scaleGPDErr;
      thresholdGPD(iLatStart:iLatEnd, iLonStart:iLonEnd, :) = evaDataMax.thresholdGPD;
      thresholdGPDErr(iLatStart:iLatEnd, iLonStart:iLonEnd, :) = evaDataMax.thresholdGPDErr;
      yMax(iLatStart:iLatEnd, iLonStart:iLonEnd, :) = evaDataMax.yMax;
      clear('evaDataMax');

      retLevGEVMin(iLatStart:iLatEnd, iLonStart:iLonEnd, :, :) = retLevGEVMin_;
      retLevErrGEVMin(iLatStart:iLatEnd, iLonStart:iLonEnd, :, :) = evaDataMin.retLevErrGEV;
      shapeGEVMin(iLatStart:iLatEnd, iLonStart:iLonEnd) = evaDataMin.shapeGEV;
      shapeGEVErrMin(iLatStart:iLatEnd, iLonStart:iLonEnd, :) = evaDataMin.shapeGEVErr;
      scaleGEVMin(iLatStart:iLatEnd, iLonStart:iLonEnd, :) = evaDataMin.scaleGEV;
      scaleGEVErrMin(iLatStart:iLatEnd, iLonStart:iLonEnd, :) = evaDataMin.scaleGEVErr;
      locationGEVMin(iLatStart:iLatEnd, iLonStart:iLonEnd, :) = -evaDataMin.locationGEV;
      locationGEVErrMin(iLatStart:iLatEnd, iLonStart:iLonEnd, :) = evaDataMin.locationGEVErr;
      yMin(iLatStart:iLatEnd, iLonStart:iLonEnd, :) = -evaDataMin.yMax;
      
      if size(yMean, 3) > size(vlsYMean, 3)
        yMean(iLatStart:iLatEnd, iLonStart:iLonEnd, 1:size(vlsYMean, 3)) = vlsYMean;
      elseif size(yMean, 3) < size(vlsYMean, 3)
        yMean(iLatStart:iLatEnd, iLonStart:iLonEnd, :) = vlsYMean(:,:,1:size(yMean));
      else
        yMean(iLatStart:iLatEnd, iLonStart:iLonEnd, :) = vlsYMean;
      end
      
      xx(iLonStart:iLonEnd) = xx_;
      yy(iLatStart:iLatEnd) = yy_;
    end
  end
  
  toc(wholeTicToc);
  fprintf('\n');
  disp('all done! Saving the output');
    
  if exist(retLevNcOutFilePath, 'file')
    delete(retLevNcOutFilePath);
  end

  % max
  nccreate(retLevNcOutFilePath, 'rl', 'dimensions', {'y', ny, 'x', nx, 'year', nyrout, 'return_period', nretper});
  ncwrite(retLevNcOutFilePath, 'rl', retLevGPD);

  nccreate(retLevNcOutFilePath, 'se_rl', 'dimensions', {'y', ny, 'x', nx, 'year', nyrout, 'return_period', nretper});
  ncwrite(retLevNcOutFilePath, 'se_rl', retLevErrGPD);

  nccreate(retLevNcOutFilePath, 'shape_fit', 'dimensions', {'y', ny, 'x', nx});
  ncwrite(retLevNcOutFilePath, 'shape_fit', shapeGPD);

  nccreate(retLevNcOutFilePath, 'se_shape', 'dimensions', {'y', ny, 'x', nx});
  ncwrite(retLevNcOutFilePath, 'se_shape', shapeGPDErr);

  nccreate(retLevNcOutFilePath, 'scale_fit', 'dimensions', {'y', ny, 'x', nx, 'year', nyrout});
  ncwrite(retLevNcOutFilePath, 'scale_fit', scaleGPD);

  nccreate(retLevNcOutFilePath, 'se_scale', 'dimensions', {'y', ny, 'x', nx, 'year', nyrout});
  ncwrite(retLevNcOutFilePath, 'se_scale', scaleGPDErr);

  nccreate(retLevNcOutFilePath, 'threshold_fit', 'dimensions', {'y', ny, 'x', nx, 'year', nyrout});
  ncwrite(retLevNcOutFilePath, 'threshold_fit', thresholdGPD);

  nccreate(retLevNcOutFilePath, 'se_threshold', 'dimensions', {'y', ny, 'x', nx, 'year', nyrout});
  ncwrite(retLevNcOutFilePath, 'se_threshold', thresholdGPDErr);
  
  nccreate(retLevNcOutFilePath, 'year_max', 'dimensions', {'y', ny, 'x', nx, 'year_all', nyrall});
  ncwrite(retLevNcOutFilePath, 'year_max', yMax);

  % min
  nccreate(retLevNcOutFilePath, 'rl_min', 'dimensions', {'y', ny, 'x', nx, 'year', nyrout, 'return_period', nretper});
  ncwrite(retLevNcOutFilePath, 'rl_min', retLevGEVMin);

  nccreate(retLevNcOutFilePath, 'se_rl_min', 'dimensions', {'y', ny, 'x', nx, 'year', nyrout, 'return_period', nretper});
  ncwrite(retLevNcOutFilePath, 'se_rl_min', retLevErrGEVMin);

  nccreate(retLevNcOutFilePath, 'shape_fit_min', 'dimensions', {'y', ny, 'x', nx});
  ncwrite(retLevNcOutFilePath, 'shape_fit_min', shapeGEVMin);

  nccreate(retLevNcOutFilePath, 'se_shape_min', 'dimensions', {'y', ny, 'x', nx});
  ncwrite(retLevNcOutFilePath, 'se_shape', shapeGEVErrMin);

  nccreate(retLevNcOutFilePath, 'scale_fit_min', 'dimensions', {'y', ny, 'x', nx, 'year', nyrout});
  ncwrite(retLevNcOutFilePath, 'scale_fit_min', scaleGEVMin);

  nccreate(retLevNcOutFilePath, 'se_scale_min', 'dimensions', {'y', ny, 'x', nx, 'year', nyrout});
  ncwrite(retLevNcOutFilePath, 'se_scale_min', scaleGEVErrMin);

  nccreate(retLevNcOutFilePath, 'location_fit_min', 'dimensions', {'y', ny, 'x', nx, 'year', nyrout});
  ncwrite(retLevNcOutFilePath, 'location_fit_min', locationGEVMin);

  nccreate(retLevNcOutFilePath, 'se_location_min', 'dimensions', {'y', ny, 'x', nx, 'year', nyrout});
  ncwrite(retLevNcOutFilePath, 'se_location_min', locationGEVErrMin);
  
  nccreate(retLevNcOutFilePath, 'year_min', 'dimensions', {'y', ny, 'x', nx, 'year_all', nyrall});
  ncwrite(retLevNcOutFilePath, 'year_min', yMin);

  
  % mean
  nccreate(retLevNcOutFilePath, 'year_mean', 'dimensions', {'y', ny, 'x', nx, 'year_all', nyrall});
  ncwrite(retLevNcOutFilePath, 'year_mean', yMean);

  
  
  nccreate(retLevNcOutFilePath, 'x', 'dimensions', {'ix', nx});
  ncwrite(retLevNcOutFilePath, 'x', xx);

  nccreate(retLevNcOutFilePath, 'y', 'dimensions', {'iy', ny});
  ncwrite(retLevNcOutFilePath, 'y', yy);

  nccreate(retLevNcOutFilePath, 'year', 'dimensions', {'iyear', nyrout});
  ncwrite(retLevNcOutFilePath, 'year', outYears);

  nccreate(retLevNcOutFilePath, 'year_all', 'dimensions', {'iyear_all', nyrall});
  ncwrite(retLevNcOutFilePath, 'year_all', allYears);

  nccreate(retLevNcOutFilePath, 'return_period', 'dimensions', {'nretper', nretper});
  ncwrite(retLevNcOutFilePath, 'return_period', returnPeriodsInYears);
  
  
  nccreate(retLevNcOutFilePath, 'eva_type_max', 'datatype', 'char', 'dimensions', {'nchar', 10});
  ncwrite(retLevNcOutFilePath, 'eva_type_max', 'GPD');

  nccreate(retLevNcOutFilePath, 'eva_type_min', 'datatype', 'char', 'dimensions', {'nchar', 10});
  ncwrite(retLevNcOutFilePath, 'eva_type_min', 'GEV');

  
  
catch exc
  disp(['Exception raised. Last processed isubx, isuby: ' num2str(isubx) ', ' num2str(isuby)]);
%  delete(parObj);
  rethrow(exc);
end
%delete(parObj);


