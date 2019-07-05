function dt = lfExecuteTsEvaHelix(tmstmp, lonAll, latAll, vlsAll, outYears, returnPeriodsInYears, varargin)
  args.parObj = [];
  args.nWorker = 12;
  args.tsEvaTimeWindow = 365.25*30; % 30 years
  args.maxFracNan = .5;
  args.ciPercentile = 98.5;
  args = lfEasyParseNamedArgs(varargin, args);
  parObj = args.parObj;
  nWorker = args.nWorker;
  maxFracNan = args.maxFracNan;
  timeWindow = args.tsEvaTimeWindow;
  minPeakDistanceInDays = 30;
  ciPercentile = args.ciPercentile;
  
  nlon = length(lonAll);
  nlat = length(latAll);
 %[lonMtx, latMtx] = meshgrid(lonAll, latAll);
 %[ilonMtx, ilatMtx] = meshgrid(1:nlon, 1:nlat);
  [latMtx, lonMtx] = meshgrid(latAll, lonAll);
  [ilatMtx, ilonMtx] = meshgrid(1:nlat, 1:nlon);
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

  retLevGPD_ = ones(npt, nyr, nretper)*nan;
  retLevErrGPD_ = ones(npt, nyr, nretper)*nan;
  shapeGPD_ = ones(npt, 1)*nan;
  shapeGPDErr_ = ones(npt, 1)*nan;
  scaleGPD_ = ones(npt, nyr)*nan;
  scaleGPDErr_ = ones(npt, nyr)*nan;
  thresholdGPD_ = ones(npt, nyr)*nan;
  thresholdGPDErr_ = ones(npt, nyr)*nan;
  yMax_ = ones(npt, nyrAll)*nan;
  
  ownsParObj = isempty(parObj) & (nWorker > 1);
  if ownsParObj
    parObj = parpool(nWorker);
  end
  try

    tic;
    %for ipt = 1:npt
    parfor ipt = 1:npt
    %for ipt = 139:139
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

        timeAndSeries = [tmstmp vli];

        fracNan = sum(isnan(timeAndSeries(:,2)))/size(timeAndSeries, 1);
        if fracNan >= maxFracNan
          continue;
        end

        [nonStatEvaParams, statTransfData, isValid] = tsEvaNonStationary(timeAndSeries, timeWindow, 'transfType', 'trendCiPercentile',...
             'ciPercentile', ciPercentile, 'minPeakDistanceInDays', minPeakDistanceInDays, 'potEventsPerYear', 2);


        if ~isValid
          disp(['     in point ' num2str(ptlon) ', ' num2str(ptlat) ' analysis result invalid. Skipping']);
          continue;
        end

        [ nonStatEvaParams, statTransfData ] = tsEvaReduceOutputObjSize( nonStatEvaParams, statTransfData, outDt );

        [ptReturnLevels, ptReturnLevelsErr, ~, ~] = tsEvaComputeReturnLevelsGPDFromAnalysisObj(nonStatEvaParams, returnPeriodsInYears);

        [ptYMax, ptDt, ~] = tsEvaComputeAnnualMaxima(timeAndSeries);
        cndYmax = (ptDt >= datenum(min(outYears), 1, 1)) & (ptDt <= datenum(max(outYears) + 1, 1, 1));
        ptYMax = ptYMax(cndYmax);
        
        epsilon = nonStatEvaParams(2).parameters.epsilon;
        if epsilon > .5
          continue;
        end
        
        retLevGPD_(ipt, :, :) = ptReturnLevels;
        retLevErrGPD_(ipt, :, :) = ptReturnLevelsErr;
        shapeGPD_(ipt) = nonStatEvaParams(2).parameters.epsilon;
        shapeGPDErr_(ipt) = nonStatEvaParams(2).paramErr.epsilonErr;
        scaleGPD_(ipt, :) = nonStatEvaParams(2).parameters.sigma;
        scaleGPDErr_(ipt, :) = nonStatEvaParams(2).paramErr.sigmaErr;
        thresholdGPD_(ipt, :) = nonStatEvaParams(2).parameters.threshold;
        thresholdGPDErr_(ipt, :) = 0;

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
  dt.retLevGPD = ones(nlat, nlon, nyr, nretper)*nan;
  dt.retLevErrGPD = ones(nlat, nlon, nyr, nretper)*nan;
  dt.shapeGPD = ones(nlat, nlon)*nan;
  dt.shapeGPDErr = ones(nlat, nlon)*nan;
  dt.scaleGPD = ones(nlat, nlon, nyr)*nan;
  dt.scaleGPDErr = ones(nlat, nlon, nyr)*nan;
  dt.thresholdGPD = ones(nlat, nlon, nyr)*nan;
  dt.thresholdGPDErr = ones(nlat, nlon, nyr)*nan;
  dt.yMax = ones(nlat, nlon, nyrAll)*nan;

  for ipt = 1:npt
    if rem(ipt, 500) == 0
      disp(['  done ' num2str(ipt/npt*100) '%']);
    end
    iilat = ilat(ipt);
    iilon = ilon(ipt);

    dt.retLevGPD(iilat, iilon, :) = retLevGPD_(ipt, :);
    dt.retLevErrGPD(iilat, iilon, :) = retLevErrGPD_(ipt, :);
    dt.shapeGPD(iilat, iilon) = shapeGPD_(ipt);
    dt.shapeGPDErr(iilat, iilon) = shapeGPDErr_(ipt);
    dt.scaleGPD(iilat, iilon, :) = scaleGPD_(ipt, :);
    dt.scaleGPDErr(iilat, iilon, :) = scaleGPDErr_(ipt, :);
    dt.thresholdGPD(iilat, iilon, :) = thresholdGPD_(ipt, :);
    dt.thresholdGPDErr(iilat, iilon, :) = thresholdGPDErr_(ipt, :);
    dt.yMax(iilat, iilon, :) = yMax_(ipt, :);
  end
  
  
  
end
