function lfEvaModel(scenario, model, wuChanging, outDir, varargin)

returnPeriodsInYears = [5 10 20 50 100 250 500 1000 2000];
channelMapFl = './maps/channels_5km.nc';
nparworker = 1;

if wuChanging
  wustr = 'wuChang';
else
  wustr = 'wuConst';
end

channelMap = ncread(channelMapFl, 'channels');
channelMap(isnan(channelMap)) = false;

retLevNcFlName = [strjoin({scenario, model, wustr, 'dis', 'statistics'}, '_') '.nc'];
retLevNcOutFilePath = fullfile(outDir, retLevNcFlName);

nx = 1000;
ny = 950; 
nretper = length(returnPeriodsInYears);
nyrall = 120;
nyrout = round(nyrall/5);

% this procedure will analyze 120x60 windows, to avoid using too much
% memory
%dlon = 120;
%dlat = 60;
dx = 250;
dy = 190;

if nparworker > 1
  parObj = parpool(nparworker);
else
  parObj = -1;
end

%try
  disp('allocating output ...');
  retLevGPD = ones(ny, nx, nyrout, nretper)*nan;
  retLevErrGPD = ones(ny, nx, nyrout, nretper)*nan;
  shapeGPD = ones(ny, nx)*nan;
  shapeGPDErr = ones(ny, nx)*nan;
  scaleGPD = ones(ny, nx, nyrout)*nan;
  scaleGPDErr = ones(ny, nx, nyrout)*nan;
  thresholdGPD = ones(ny, nx, nyrout)*nan;
  thresholdGPDErr = ones(ny, nx, nyrout)*nan;

  nsubx = ceil(nx/dx);
  nsuby = ceil(ny/dy);
  
  outYears = (1985:5:2100)';
  outYears = cat(1, [1981, outYears]);
  xx = ones(nx, 1)*nan;
  yy = ones(ny, 1)*nan;
  
  wholeTicToc = tic;
  
  for isublon = 1:nsubx
    for isublat = 1:nsuby
      fprintf('\n');
      disp(['elaborating sub area ' num2str(isubx) ', ' num2str(isuby)]);
      iLonStart = (isublon - 1)*dx + 1;
      iLonEnd = min(isublon*dx, nx);
      iLatStart = (isublat - 1)*dy + 1;
      iLatEnd = min(isublat*dy, ny);
      disp(['iLonStart, iLonEnd = ' num2str(iLonStart) ', ' num2str(iLonEnd)]);
      disp(['iLatStart, iLatEnd = ' num2str(iLatStart) ', ' num2str(iLatEnd)]);
      
      tic;
      channelMap_ = channelMap(iLatStart:iLatEnd, iLonStart:iLonEnd);
      [ tmstmp, xx_, yy_, vls ] = lfDisLoadFromNc( [iLonStart iLatStart], [iLonEnd iLatEnd], scenario, model, wuChanging, varargin{:} );
      evaData = lfExecuteTsEva( tmstmp, xx_, yy_, vls, outYears, returnPeriodsInYears, channelMap_, 'parObj', parObj );
      
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

  nccreate(retLevNcOutFilePath, 'x', 'dimensions', {'ix', nx});
  ncwrite(retLevNcOutFilePath, 'x', xx);

  nccreate(retLevNcOutFilePath, 'y', 'dimensions', {'iy', ny});
  ncwrite(retLevNcOutFilePath, 'y', yy);

  nccreate(retLevNcOutFilePath, 'year', 'dimensions', {'iyear', nyrout});
  ncwrite(retLevNcOutFilePath, 'y', outYears);

  nccreate(retLevNcOutFilePath, 'return_period', 'dimensions', {'nretper', nretper});
  ncwrite(retLevNcOutFilePath, 'return_period', returnPeriodsInYears);
  
  
  
  nccreate(retLevNcOutFilePath, 'eva_type', 'datatype', 'char', 'dimensions', {'nchar', 10});
  ncwrite(retLevNcOutFilePath, 'eva_type', 'GPD');


  
  
%catch exc
%  disp(['Exception raised. Last processed isublon, isublat: ' num2str(isublon) ', ' num2str(isublat)]);
%  delete(parObj);
%  rethrow(exc);
%end
delete(parObj);


