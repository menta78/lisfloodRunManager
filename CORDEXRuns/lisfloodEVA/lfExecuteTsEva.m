function dt = lfExecuteTsEva(tmstmp, lonAll, latAll, vlsAll, outYears, returnPeriodsInYears, channelMap, varargin)
  minPeakDistanceInDays = 1.5;

  args.parObj = [];
  args.nWorker = 12;
  args = easyParseNamedArgs(varargin, args);
  parObj = args.parObj;
  nWorker = args.nWorker;
  timeWindow = 365.25*30; % 30 years
  minPeakDistanceInDays = 30;
  
  ownsParObj = isempty(parObj);
  if ownsParObj
    parObj = parpool(nWorker);
  end
  try

    nlon = length(lon);
    nlat = length(lat);
    [lonMtx, latMtx] = meshgrid(lon, lat);
    [ilonMtx, ilatMtx] = meshgrid(1:nlon, 1:nlat);
    lon = lonMtx(channelMap);
    lat = latMtx(channelMap);
    ilon = ilonMtx(channelMap);
    ilat = ilatMtx(channelMap);
    vls = vlsAll(channelMap);
    
    outDtVc = [outYears, ones(size(outYears)), ones(size(outYears))];
    outDt = datenum(outDtVc);
    outDtIndx = knnsearch(tmstmp, outDt);
    
    npt = length(vls);
    nyr = length(outYears);

    nretper = length(returnPeriodsInYears);

    retLevGPD_ = ones(npt, nyr, nretper)*nan;
    retLevErrGPD_ = ones(npt, nyr, nretper)*nan;
    shapeGPD_ = ones(npt, 1)*nan;
    shapeGPDErr_ = ones(npt, 1)*nan;
    scaleGPD_ = ones(npt, nyr)*nan;
    scaleGPDErr_ = ones(npt, nyr)*nan;
    thresholdGPD_ = ones(npt, nyr)*nan;
    thresholdGPDErr_ = ones(npt, nyr)*nan;

    tic;
    parfor ipt = 1:npt
    %for ipt = 7270:7290
      try
        disp(ipt);
        disp(['  done ' num2str(ipt/npt*100) '%']);

        ptlon = lon(ilon);
        ptlat = lat(ilat);

        vli = squeeze(vls(ipt, :));
        if all(isnan(vli))
          % this point is in the sea
          continue;
        end

        if isempty(evaTimeLimits)
          timeAndSeries = [tmstmp vli];
        else
          cnd = tmstmp >= evaTimeLimits(1) & tmstmp < evaTimeLimits(2);
          tmstmp0 = tmstmp(cnd);
          vli0 = vli(cnd);
          timeAndSeries = [tmstmp0 vli0];
        end

        fracNan = sum(isnan(timeAndSeries(:,2)))/size(timeAndSeries, 1);
        if fracNan >= .5
          continue;
        end

        [nonStatEvaParams, statTransfData, isValid] = tsEvaNonStationary(timeAndSeries, timeWindow, 'transfType', 'trendCiPercentile',...
  'ciPercentile', ciPercentile, 'minPeakDistanceInDays', minPeakDistanceInDays);


        if ~isValid
          disp(['     in point ' num2str(ptlon) ', ' num2str(ptlat) ' analysis result invalid. Skipping']);
          continue;
        end

        [ptReturnLevels, ptReturnLevelsErr, ~, ~] = tsEvaComputeReturnLevelsGPDFromAnalysisObj(nonStatEvaParams, returnPeriodsInYears, 'timeindex', outDtIndx);

        retLevGPD_(ipt, :, :) = ptReturnLevels;
        retLevErrGPD_(ipt, :, :) = ptReturnLevelsErr;
        shapeGPD_(ipt) = nonStatEvaParams(2).parameters.epsilon;
        shapeGPDErr_(ipt) = nonStatEvaParams(2).paramErr.epsilonErr;
        scaleGPD_(ipt, :) = nonStatEvaParams(2).parameters.sigma;
        scaleGPDErr_(ipt, :) = nonStatEvaParams(2).paramErr.sigmaErr;
        thresholdGPD_(ipt, :) = nonStatEvaParams(2).parameters.threshold;
        thresholdGPDErr_(ipt, :) = 0;
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
  end
  
  
  
end
