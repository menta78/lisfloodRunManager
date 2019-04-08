function dt = lfStationaryEva(lon, lat, vls, tmstmp, returnPeriodsInYears, varargin)
  minPeakDistanceInDays = 31;

  args.parObj = [];
  args.nWorker = 12;
  args.gevType = 'GEV';
  args = easyParseNamedArgs(varargin, args);
  parObj = args.parObj;
  nWorker = args.nWorker;
  gevType = args.gevType;
  
  ownsParObj = isempty(parObj);
  if ownsParObj
    parObj = parpool(nWorker);
  end
  try
    
    
    
    nlon = length(lon);
    nlat = length(lat);
    npt = nlon*nlat;
    yrs = unique(tsYear(tmstmp));
    nyr = length(yrs);

    nretper = length(returnPeriodsInYears);

    retLevGEV_ = ones(npt, nretper)*nan;
    retLevErrGEV_ = ones(npt, nretper)*nan;
    shapeGEV_ = ones(npt, 1)*nan;
    shapeGEVErr_ = ones(npt, 1)*nan;
    scaleGEV_ = ones(npt, 1)*nan;
    scaleGEVErr_ = ones(npt, 1)*nan;
    locationGEV_ = ones(npt, 1)*nan;
    locationGEVErr_ = ones(npt, 1)*nan;
    le_ = ones(npt, nyr)*nan;
    frq_ = ones(npt, nyr)*nan;
    time_ = ones(npt, nyr)*nan;
    rp_ = ones(npt, nyr)*nan;
    se_rp_sup_ = ones(npt, nyr)*nan;
    se_rp_inf_ = ones(npt, nyr)*nan;
    
    tic;
    parfor ipt = 1:npt
    %for ipt = 1:npt
      try
        disp(ipt);
        disp(['  done ' num2str(ipt/npt*100) '%']);
        ilat = ceil(ipt/nlon);
        ilon = ipt - (ilat - 1)*nlon;

        ptlon = lon(ilon);
        ptlat = lat(ilat);

        vli = squeeze(vls(:, ilon, ilat));
        if all(isnan(vli)) || all(vli == 0)
          % this point is in the sea
          continue;
        end

        timeAndSeries = [tmstmp vli];

%         fracNan = sum(isnan(timeAndSeries(:,2)))/size(timeAndSeries, 1);
%         if fracNan >= .5
%           continue;
%         end
% 
        %[nonStatEvaParams, isValid] = tsEvaStationary(timeAndSeries, 'minPeakDistanceInDays', minPeakDistanceInDays, 'evdType', 'GEV', 'potPercentiles', [98.5 99. 99.5]);
        [nonStatEvaParams, isValid] = tsEvaStationary(timeAndSeries, 'minPeakDistanceInDays', minPeakDistanceInDays,...
                  'evdType', 'GEV', 'gevType', gevType);

        if ~isValid
          disp(['     in point ' num2str(ptlon) ', ' num2str(ptlat) ' analysis result invalid. Skipping']);
          continue;
        end

        [ptReturnLevels, ptReturnLevelsErr, ~, ~] = tsEvaComputeReturnLevelsGEVFromAnalysisObj(nonStatEvaParams, returnPeriodsInYears);
 %       [ptReturnLevels, ptReturnLevelsErr, ~, ~] = tsEvaComputeReturnLevelsGPDFromAnalysisObj(nonStatEvaParams, returnPeriodsInYears);
        ptReturnLevels(returnPeriodsInYears == 1) = percentile(vli, .5);

        ptReturnLevelsErr(isnan(ptReturnLevelsErr)) = ptReturnLevels(isnan(ptReturnLevelsErr));
        
        [vlsymax, ~, ~] = tsEvaComputeAnnualMaxima([tmstmp vli]);
        [largest1PtRp_, largest1PtRpCISup, largest1PtRpCIInf] = tsGetReturnPeriodOfLevel(returnPeriodsInYears', ptReturnLevels', ptReturnLevelsErr', vlsymax, 'linExtrap', true);
        largest1PtRpErrSup = largest1PtRpCISup - largest1PtRp_;
        largest1PtRpErrInf = largest1PtRp_ - largest1PtRpCIInf;
        [largest1PtRp, largest1PtExceedProb] = tsEvaGetReturnPeriodOfLevelGEV(nonStatEvaParams(1).parameters.epsilon, nonStatEvaParams(1).parameters.sigma, nonStatEvaParams(1).parameters.mu, vlsymax);

        retLevGEV_(ipt, :) = ptReturnLevels;
        retLevErrGEV_(ipt, :) = ptReturnLevelsErr;
        shapeGEV_(ipt) = nonStatEvaParams(1).parameters.epsilon;
        shapeGEVErr_(ipt) = nonStatEvaParams(1).paramErr.epsilonErr;
        scaleGEV_(ipt) = nonStatEvaParams(1).parameters.sigma;
        scaleGEVErr_(ipt) = nonStatEvaParams(1).paramErr.sigmaErr;
        locationGEV_(ipt) = nonStatEvaParams(1).parameters.mu;
        locationGEVErr_(ipt) = nonStatEvaParams(1).paramErr.muErr;

        le_(ipt, :) = vli;
        rp_(ipt, :) = largest1PtRp;
        se_rp_sup_(ipt, :) = largest1PtRpErrSup;
        se_rp_inf_(ipt, :) = largest1PtRpErrInf;
        frq_(ipt, :) = largest1PtExceedProb;
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
  dt.retLevGEV = ones(nlon, nlat, nretper)*nan;
  dt.retLevErrGEV = ones(nlon, nlat, nretper)*nan;
  dt.shapeGEV = ones(nlon, nlat)*nan;
  dt.shapeGEVErr = ones(nlon, nlat)*nan;
  dt.scaleGEV = ones(nlon, nlat)*nan;
  dt.scaleGEVErr = ones(nlon, nlat)*nan;
  dt.locationGEV = ones(nlon, nlat)*nan;
  dt.locationGEVErr = ones(nlon, nlat)*nan;

  dt.le = ones(nlon, nlat, nyr)*nan;
  dt.rp = ones(nlon, nlat, nyr)*nan;
  dt.se_rp_sup = ones(nlon, nlat, nyr)*nan;
  dt.se_rp_inf = ones(nlon, nlat, nyr)*nan;
  dt.frq = ones(nlon, nlat, nyr)*nan;


  for ipt = 1:npt
    if rem(ipt, 500) == 0
      disp(['  done ' num2str(ipt/npt*100) '%']);
    end
    ilat = ceil(ipt/nlon);
    ilon = ipt - (ilat - 1)*nlon;

    dt.retLevGEV(ilon, ilat, :) = retLevGEV_(ipt, :);
    dt.retLevErrGEV(ilon, ilat, :) = retLevErrGEV_(ipt, :);
    dt.shapeGEV(ilon, ilat) = shapeGEV_(ipt);
    dt.shapeGEVErr(ilon, ilat) = shapeGEVErr_(ipt);
    dt.scaleGEV(ilon, ilat) = scaleGEV_(ipt);
    dt.scaleGEVErr(ilon, ilat) = scaleGEVErr_(ipt);
    dt.locationGEV(ilon, ilat) = locationGEV_(ipt);
    dt.locationGEVErr(ilon, ilat) = locationGEVErr_(ipt);

    dt.le(ilon, ilat, :) = le_(ipt, :);
    dt.time(ilon, ilat, :) = time_(ipt, :);
    dt.rp(ilon, ilat, :) = rp_(ipt, :);
    dt.se_rp_sup(ilon, ilat, :) = se_rp_sup_(ipt, :);
    dt.se_rp_inf(ilon, ilat, :) = se_rp_inf_(ipt, :);
    dt.frq(ilon, ilat, :) = frq_(ipt, :);
  end
  
  
  
end
