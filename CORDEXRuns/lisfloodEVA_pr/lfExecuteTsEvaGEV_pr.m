function dt = lfExecuteTsEvaGEV(tmstmp, lonAll, latAll, vlsAll, outYears, returnPeriodsInYears, varargin)
  args.parObj = [];
  args.nWorker = 12;
  args.tsEvaTimeWindow = 365.25*30; % 30 years
  args.maxFracNan = .5;
  args = lfEasyParseNamedArgs(varargin, args);
  parObj = args.parObj;
  nWorker = args.nWorker;
  maxFracNan = args.maxFracNan;
  timeWindow = args.tsEvaTimeWindow;
  minPeakDistanceInDays = 30;
  
  nlon = length(lonAll);
  nlat = length(latAll);
 %[lonMtx, latMtx] = meshgrid(lonAll, latAll);
 %[ilonMtx, ilatMtx] = meshgrid(1:nlon, 1:nlat);
  [latMtx, lonMtx] = meshgrid(latAll, lonAll);
  [ilatMtx, ilonMtx] = meshgrid(1:nlat, 1:nlon);

 % making the matrices flat (in other versions of the code, cm2d is got from the channelmap)
  lon = lonMtx(:);
  lat = latMtx(:);
  ilon = ilonMtx(:);
  ilat = ilatMtx(:);
  vls = reshape(vlsAll, size(ilon, 1), size(vlsAll, 3));
  clear vlsAll;

  outDtVc = [outYears, ones(size(outYears)), ones(size(outYears))];
  outDt = datenum(outDtVc);
  %outDtIndx = knnsearch(tmstmp, outDt);

  npt = size(vls, 1);
  nyr = length(outYears);
  
  %allYears = unique(tsYear(tmstmp));
  allYears = (min(outYears):max(outYears))';
  nyrAll = length(allYears);

  nretper = length(returnPeriodsInYears);

  retLevGEV_ = ones(npt, nyr, nretper)*nan;
  retLevErrGEV_ = ones(npt, nyr, nretper)*nan;
  shapeGEV_ = ones(npt, 1)*nan;
  shapeGEVErr_ = ones(npt, 1)*nan;
  scaleGEV_ = ones(npt, nyr)*nan;
  scaleGEVErr_ = ones(npt, nyr)*nan;
  locationGEV_ = ones(npt, nyr)*nan;
  locationGEVErr_ = ones(npt, nyr)*nan;
  yMax_ = ones(npt, nyrAll)*nan;
  
  ownsParObj = isempty(parObj) & (nWorker > 1);
  if ownsParObj
    parObj = parpool(nWorker);
  end
  try

    tic;
    parfor ipt = 1:npt
    %for ipt = 400:401
      try
        disp(ipt);
        disp(['  done ' num2str(ipt/npt*100) '%']);

        ptlon = lon(ipt);
        ptlat = lat(ipt);

        vli = squeeze(vls(ipt, :))';
        if all(isnan(vli))
          % this point is in the sea
          continue;
        end

        timeAndSeries = double([tmstmp vli]);

        fracNan = sum(isnan(timeAndSeries(:,2)))/size(timeAndSeries, 1);
        if fracNan >= maxFracNan
          continue;
        end

        [nonStatEvaParams, statTransfData, isValid] = tsEvaNonStationary(timeAndSeries, timeWindow,...
             'evdType', 'GEV', 'minPeakDistanceInDays', minPeakDistanceInDays, 'potEventsPerYear', 2);


        if ~isValid
          disp(['     in point ' num2str(ptlon) ', ' num2str(ptlat) ' analysis result invalid. Skipping']);
          continue;
        end

        [ nonStatEvaParams, statTransfData ] = tsEvaReduceOutputObjSize( nonStatEvaParams, statTransfData, outDt );

        [ptReturnLevels, ptReturnLevelsErr, ~, ~] = tsEvaComputeReturnLevelsGEVFromAnalysisObj(nonStatEvaParams, returnPeriodsInYears);

        [ptYMax, ptDt, ~] = tsEvaComputeAnnualMaxima(timeAndSeries);
        cndYmax = (ptDt >= datenum(min(outYears), 1, 1)) & (ptDt <= datenum(max(outYears) + 1, 1, 1));
        ptYMax = ptYMax(cndYmax);
        
        retLevGEV_(ipt, :, :) = ptReturnLevels;
        retLevErrGEV_(ipt, :, :) = ptReturnLevelsErr;
        shapeGEV_(ipt) = nonStatEvaParams(1).parameters.epsilon;
        shapeGEVErr_(ipt) = nonStatEvaParams(1).paramErr.epsilonErr;
        scaleGEV_(ipt, :) = nonStatEvaParams(1).parameters.sigma;
        scaleGEVErr_(ipt, :) = nonStatEvaParams(1).paramErr.sigmaErr;
        locationGEV_(ipt, :) = nonStatEvaParams(1).parameters.mu;
        locationGEVErr_(ipt, :) = nonStatEvaParams(1).paramErr.muErr;

        % for some reason the sizes of ptYMax and yMax_ may differ here
        lPtYMax = length(ptYMax);
        if lPtYMax >= nyrAll
          yMax_(ipt, :) = ptYMax(1:nyrAll);
        else
          ptYMax_ = ones([nyrAll, 1])*nan;
          ptYMax_(1:lPtYMax) = ptYMax;
          yMax_(ipt, :) = ptYMax_;
        end
      catch exc
        disp(['exception raised processing point ' num2str(ipt)]);
        disp(getReport(exc,'extended','hyperlinks','off'));
      end
    end  
    
    
    
  catch exc
    if ownsParObj
      delete(parObj);
    end
    rethrow(exc);
  end
  if ownsParObj
    delete(parObj);
  end

  
  disp('assigning gridded output ...');
  dt.retLevGEV = ones(nlat, nlon, nyr, nretper)*nan;
  dt.retLevErrGEV = ones(nlat, nlon, nyr, nretper)*nan;
  dt.shapeGEV = ones(nlat, nlon)*nan;
  dt.shapeGEVErr = ones(nlat, nlon)*nan;
  dt.scaleGEV = ones(nlat, nlon, nyr)*nan;
  dt.scaleGEVErr = ones(nlat, nlon, nyr)*nan;
  dt.locationGEV = ones(nlat, nlon, nyr)*nan;
  dt.locationGEVErr = ones(nlat, nlon, nyr)*nan;
  dt.yMax = ones(nlat, nlon, nyrAll)*nan;

  for ipt = 1:npt
    if rem(ipt, 500) == 0
      disp(['  done ' num2str(ipt/npt*100) '%']);
    end
    iilat = ilat(ipt);
    iilon = ilon(ipt);

    dt.retLevGEV(iilat, iilon, :) = retLevGEV_(ipt, :);
    dt.retLevErrGEV(iilat, iilon, :) = retLevErrGEV_(ipt, :);
    dt.shapeGEV(iilat, iilon) = shapeGEV_(ipt);
    dt.shapeGEVErr(iilat, iilon) = shapeGEVErr_(ipt);
    dt.scaleGEV(iilat, iilon, :) = scaleGEV_(ipt, :);
    dt.scaleGEVErr(iilat, iilon, :) = scaleGEVErr_(ipt, :);
    dt.locationGEV(iilat, iilon, :) = locationGEV_(ipt, :);
    dt.locationGEVErr(iilat, iilon, :) = locationGEVErr_(ipt, :);
    dt.yMax(iilat, iilon, :) = yMax_(ipt, :);
  end
  
  
  
end
