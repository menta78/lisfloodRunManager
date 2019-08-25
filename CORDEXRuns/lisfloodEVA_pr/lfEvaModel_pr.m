function lfEvaModel(scenario, model, outDir, varargin)

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

retLevNcFlName = [strjoin({'projection', varname, scenario, model, 'statistics'}, '_') '.nc'];
retLevNcOutFilePath = fullfile(outDir, retLevNcFlName);

nx = 1000;
ny = 950;
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
  retLevGEV = ones(ny, nx, nyrout, nretper)*nan;
  retLevErrGEV = ones(ny, nx, nyrout, nretper)*nan;
  shapeGEV = ones(ny, nx)*nan;
  shapeGEVErr = ones(ny, nx)*nan;
  scaleGEV = ones(ny, nx, nyrout)*nan;
  scaleGEVErr = ones(ny, nx, nyrout)*nan;
  yMax = ones(ny, nx, nyrall)*nan;
  
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
      [ tmstmp, xx_, yy_, vls ] = lfPrLoadFromNc( [iLonStart iLatStart], [iLonEnd iLatEnd], scenario, model, varargin{:} );
     %evaData = lfExecuteTsEva( tmstmp, xx_, yy_, vls, outYears, returnPeriodsInYears, channelMap_, 'parObj', parObj );
     %evaDataMax = lfExecuteTsEva( tmstmp, xx_, yy_, vls, outYears, returnPeriodsInYears, channelMap_, 'nWorker', nparworker, varargin{:} );
      evaDataMax = lfExecuteTsEvaGEV_pr( tmstmp, xx_, yy_, vls, outYears, returnPeriodsInYears, 'nWorker', nparworker, 'maxFracNan', .1, varargin{:} );
      
      fprintf('\n');
      toc;
      disp('eva on chunk complete. Assigning results to the final output')
      retLevGEV(iLatStart:iLatEnd, iLonStart:iLonEnd, :, :) = evaDataMax.retLevGEV;
      retLevErrGEV(iLatStart:iLatEnd, iLonStart:iLonEnd, :, :) = evaDataMax.retLevErrGEV;
      shapeGEV(iLatStart:iLatEnd, iLonStart:iLonEnd) = evaDataMax.shapeGEV;
      shapeGEVErr(iLatStart:iLatEnd, iLonStart:iLonEnd, :) = evaDataMax.shapeGEVErr;
      scaleGEV(iLatStart:iLatEnd, iLonStart:iLonEnd, :) = evaDataMax.scaleGEV;
      scaleGEVErr(iLatStart:iLatEnd, iLonStart:iLonEnd, :) = evaDataMax.scaleGEVErr;
      yMax(iLatStart:iLatEnd, iLonStart:iLonEnd, :) = evaDataMax.yMax;
      clear('evaDataMax');
      
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
  ncwrite(retLevNcOutFilePath, 'rl', retLevGEV);

  nccreate(retLevNcOutFilePath, 'se_rl', 'dimensions', {'y', ny, 'x', nx, 'year', nyrout, 'return_period', nretper});
  ncwrite(retLevNcOutFilePath, 'se_rl', retLevErrGEV);

  nccreate(retLevNcOutFilePath, 'shape_fit', 'dimensions', {'y', ny, 'x', nx});
  ncwrite(retLevNcOutFilePath, 'shape_fit', shapeGEV);

  nccreate(retLevNcOutFilePath, 'se_shape', 'dimensions', {'y', ny, 'x', nx});
  ncwrite(retLevNcOutFilePath, 'se_shape', shapeGEVErr);

  nccreate(retLevNcOutFilePath, 'scale_fit', 'dimensions', {'y', ny, 'x', nx, 'year', nyrout});
  ncwrite(retLevNcOutFilePath, 'scale_fit', scaleGEV);

  nccreate(retLevNcOutFilePath, 'se_scale', 'dimensions', {'y', ny, 'x', nx, 'year', nyrout});
  ncwrite(retLevNcOutFilePath, 'se_scale', scaleGEVErr);
  
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
  
  
  nccreate(retLevNcOutFilePath, 'eva_type_max', 'datatype', 'char', 'dimensions', {'nchar', 10});
  ncwrite(retLevNcOutFilePath, 'eva_type_max', 'GEV');

  
  
catch exc
  disp(['Exception raised. Last processed isubx, isuby: ' num2str(isubx) ', ' num2str(isuby)]);
%  delete(parObj);
  rethrow(exc);
end
%delete(parObj);


