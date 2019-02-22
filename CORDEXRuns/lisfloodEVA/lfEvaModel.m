function lfEvaModel(scenario, model, wuChanging, outDir, varargin)

args.nparworker = 12;
args.skipExistingFiles = true;
args.varname = 'dis';
args = lfEasyParseNamedArgs(varargin, args);
nparworker = args.nparworker;
skipExistingFiles = args.skipExistingFiles;
varname = args.varname;

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
%dx = 250;
%dy = 190;
%dx = 250;
%dy = 320;
dx = 250;
dy = 249;

% if nparworker > 1
%   parObj = parpool(nparworker);
% else
%   parObj = -1;
% end

try
    
  if exist(retLevNcOutFilePath, 'file')
    if skipExistingFiles
      disp(['          file ' retLevNcOutFilePath ' already exists. Skipping']);
      return;
    else
      delete(retLevNcOutFilePath);
    end
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

  nsubx = ceil(nx/dx);
  nsuby = ceil(ny/dy);
  xx = ones(nx, 1)*nan;
  yy = ones(ny, 1)*nan;
  
  wholeTicToc = tic;
  
  for isubx = 1:nsubx
    for isuby = 1:nsuby
% for isubx = 1:1
%   for isuby = 1:1
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
      evaData = lfExecuteTsEva( tmstmp, xx_, yy_, vls, outYears, returnPeriodsInYears, channelMap_, 'nWorker', nparworker, varargin{:} );
      
      fprintf('\n');
      toc;
      disp('eva on chunk complete. Assigning results to the final output')
      retLevGPD(iLatStart:iLatEnd, iLonStart:iLonEnd, :, :) = evaData.retLevGPD;

      retLevErrGPD(iLatStart:iLatEnd, iLonStart:iLonEnd, :, :) = evaData.retLevErrGPD;
      shapeGPD(iLatStart:iLatEnd, iLonStart:iLonEnd) = evaData.shapeGPD;
      shapeGPDErr(iLatStart:iLatEnd, iLonStart:iLonEnd, :) = evaData.shapeGPDErr;
      scaleGPD(iLatStart:iLatEnd, iLonStart:iLonEnd, :) = evaData.scaleGPD;
      scaleGPDErr(iLatStart:iLatEnd, iLonStart:iLonEnd, :) = evaData.scaleGPDErr;
      thresholdGPD(iLatStart:iLatEnd, iLonStart:iLonEnd, :) = evaData.thresholdGPD;
      thresholdGPDErr(iLatStart:iLatEnd, iLonStart:iLonEnd, :) = evaData.thresholdGPDErr;
      yMax(iLatStart:iLatEnd, iLonStart:iLonEnd, :) = evaData.yMax;
      
      xx(iLonStart:iLonEnd) = xx_;
      yy(iLatStart:iLatEnd) = yy_;
    end
  end
  
  toc(wholeTicToc);
  fprintf('\n');
  disp('all done! Saving the output');

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
  
  
  nccreate(retLevNcOutFilePath, 'eva_type', 'datatype', 'char', 'dimensions', {'nchar', 10});
  ncwrite(retLevNcOutFilePath, 'eva_type', 'GPD');


  
  
catch exc
  disp(['Exception raised. Last processed isubx, isuby: ' num2str(isubx) ', ' num2str(isuby)]);
%  delete(parObj);
  rethrow(exc);
end
%delete(parObj);


