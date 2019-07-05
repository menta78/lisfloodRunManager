function [dt, allStationsMsrs] = lfEvaLoadDisWlObservations(allStationsMsrs)


stationMsrsJsFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/waterLevel/allStationMeasurements.json';
stationSpecJsFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/waterLevel/statWlAndDis.json';

ss = strjoin(strsplit(fileread(stationSpecJsFile), '\n'), ',\n');
statSpec = jsondecode(['[' ss(1:length(ss)-2) ']']);
stid = string(cellfun(@(s) s.EfasID, statSpec));
stlon = cellfun(@(s) s.LongitudeWgs84, statSpec);
stlat = cellfun(@(s) s.LatitudeWgs84, statSpec);

% if ~exist('allStationsMsrs', 'var')
if isempty(allStationsMsrs)
  disp('Loading all the measurements. Might take a while ...');
  allStationsMsrs = jsondecode(fileread(stationMsrsJsFile));
end
stdMsrId = string({allStationsMsrs(:).StationID}');

outSt = cell(size(stid));
outLon = zeros(size(stid))*nan;
outLat = zeros(size(stid))*nan;
outDis = cell(size(stid));
outWl = cell(size(stid));
outTimeStamp = cell(size(stid));

istout = 0;
for ist = 1:length(stid)
  statId = stid{ist};
  stationCnd = strcmpi(stdMsrId, statId);
  statMsrs = allStationsMsrs(stationCnd);
  if isempty(statMsrs)
    continue;
  end
  msrVrbl = string({statMsrs(:).Variable}');
  msrDis = [statMsrs(strcmpi(msrVrbl, "D")).AvgValue]';
  msrWl = [statMsrs(strcmpi(msrVrbl, "W")).AvgValue]';
  if (length(msrDis) < 2) || (length(msrWl) < 2)
    continue;
  end
  
  msrDisTStr = string({statMsrs(strcmpi(msrVrbl, "D")).Timestamp}');
  msrDisTm = datenum(datetime(msrDisTStr, 'inputformat', 'yyyy-MM-dd HH:mm:ss'));
  msrWlTStr = string({statMsrs(strcmpi(msrVrbl, "W")).Timestamp}');
  msrWlTm = datenum(datetime(msrWlTStr, 'inputformat', 'yyyy-MM-dd HH:mm:ss'));
  
  [~, iiDis, iiWl] = intersect(msrDisTm, msrWlTm);
  msrDisTm = msrDisTm(iiDis);
  msrDis = msrDis(iiDis);
  msrWlTm = msrWlTm(iiWl);
  msrWl = msrWl(iiWl);  
  
  istout = istout + 1;
  outSt{istout} = statId;
  outLon(istout) = stlon(ist);
  outLat(istout) = stlat(ist);
  outDis{istout} = msrDis;
  outWl{istout} = msrWl;
  outTimeStamp{istout} = msrDisTm;
end

dt.StID = {outSt{1:istout}};
dt.Lon = outLon(1:istout);
dt.Lat = outLat(1:istout);
dt.Dis = {outDis{1:istout}};
dt.Wl = {outWl{1:istout}};
dt.timeStamp = {outTimeStamp{1:istout}};
