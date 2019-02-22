function dt = lfExecuteTsEva(tmstmp, lonAll, latAll, vlsAll, outYears, returnPeriodsInYears, channelMap, varargin)
  args.parObj = [];
  args.nWorker = 12;
  args.tsEvaTimeWindow = 365.25*30; % 30 years
  args = lfEasyParseNamedArgs(varargin, args);
  parObj = args.parObj;
  nWorker = args.nWorker;
  timeWindow = args.tsEvaTimeWindow;
  minPeakDistanceInDays = 30;
  ciPercentile = 98.5;
  
  nlon = length(lonAll);
  nlat = length(latAll);
 %[lonMtx, latMtx] = meshgrid(lonAll, latAll);
 %[ilonMtx, ilatMtx] = meshgrid(1:nlon, 1:nlat);
  [latMtx, lonMtx] = meshgrid(latAll, lonAll);
  [ilatMtx, ilonMtx] = meshgrid(1:nlat, 1:nlon);
  cm2d = logical(channelMap);
  cm3d = cm2d(:,:,ones(size(vlsAll, 3), 1));
  lon = lonMtx(cm2d);
  lat = latMtx(cm2d);
  ilon = ilonMtx(cm2d);
  ilat = ilatMtx(cm2d);
  vls = reshape(vlsAll(cm3d), size(ilon, 1), size(vlsAll, 3));
  clear vlsAll cm3d;

  outDtVc = [outYears, ones(size(outYears)), ones(size(outYears))];
  outDt = datenum(outDtVc);
  %outDtIndx = knnsearch(tmstmp, outDt);

  npt = size(vls, 1);
  nyr = length(outYears);
  
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
    parfor ipt = 1:npt
    %for ipt = 1:3
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
        if fracNan >= .5
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
        
        retLevGPD_(ipt, :, :) = ptReturnLevels;
        retLevErrGPD_(ipt, :, :) = ptReturnLevelsErr;
        shapeGPD_(ipt) = nonStatEvaParams(2).parameters.epsilon;
        shapeGPDErr_(ipt) = nonStatEvaParams(2).paramErr.epsilonErr;
        scaleGPD_(ipt, :) = nonStatEvaParams(2).parameters.sigma;
        scaleGPDErr_(ipt, :) = nonStatEvaParams(2).paramErr.sigmaErr;
        thresholdGPD_(ipt, :) = nonStatEvaParams(2).parameters.threshold;
        thresholdGPDErr_(ipt, :) = 0;

        yMax_(ipt, :) = ptYMax;
      catch exc
        disp(['exception raised processing point ' num2str(ipt)]);
        disp(exc);
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
