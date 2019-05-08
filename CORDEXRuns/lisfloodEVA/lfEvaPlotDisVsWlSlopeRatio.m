outPlotDir = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/lisfloodEVA/plots';

outPng = fullfile(outPlotDir, ['wlVsDisSlopeMap.png']);

ncfileDis = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/lisfloodEVA/test/projection_dis_rcp85_CLMcom-CCLM4-8-17_BC_MPI-M-MPI-ESM-LR_wuConst_statistics.nc';
ncfileWl = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/lisfloodEVA/test/projection_wl_rcp85_CLMcom-CCLM4-8-17_BC_MPI-M-MPI-ESM-LR_wuConst_statistics.nc';

plotFigure = false;

stationMsrsJsOpFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/waterLevel/allStationMeasurements_operational.json';
stationMsrsJsOpCacheFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/waterLevel/allStationMeasurements_operational.mat';
msrsop = loadMsrsFromFile(stationMsrsJsOpFile, stationMsrsJsOpCacheFile);

stationMsrsJsHistFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/waterLevel/allStationMeasurements_historical.json';
stationMsrsJsHistCacheFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/waterLevel/allStationMeasurements_historical.mat';
msrshist = loadMsrsFromFile(stationMsrsJsHistFile, stationMsrsJsHistCacheFile);

msrs.StID = cat(2, msrsop.StID, msrshist.StID);
msrs.Lon = cat(1, msrsop.Lon, msrshist.Lon);
msrs.Lat = cat(1, msrsop.Lat, msrshist.Lat);
msrs.Dis = cat(2, msrsop.Dis, msrshist.Dis);
msrs.Wl = cat(2, msrsop.Wl, msrshist.Wl);
msrs.timeStamp = cat(2, msrsop.timeStamp, msrshist.timeStamp);


lonlatncfile = './lonlat.nc';
lon = ncread(lonlatncfile, 'lon')';
lat = ncread(lonlatncfile, 'lat')';

rlDis = ncread(ncfileDis, 'rl');
rlWl = ncread(ncfileWl, 'rl');
annualMaxDis = ncread(ncfileDis, 'year_max');
annualMaxWl = ncread(ncfileWl, 'year_max');

nst = length(msrs.StID);

xst = zeros([nst 1])*nan;
yst = zeros([nst 1])*nan;
slopeMsrs = zeros([nst 1])*nan;
slopeMdl = zeros([nst 1])*nan;
for ist = 1:nst
  disp(['ipt=' num2str(ist) ', ' num2str(ist/nst*100) '%']);
  st = msrs.StID{ist};
  ptx = msrs.Lon(ist);
  pty = msrs.Lat(ist);
  dis = msrs.Dis{ist};
  wl = msrs.Wl{ist};
  timeStamp = msrs.timeStamp;
  
  [iptx, ipty] = locateLisfloodPixel(ptx, pty, lon, lat, annualMaxDis);

%   rlDisI = squeeze(ncread(ncfileDis, 'rl', [ipty, iptx, 1, 1], [1, 1, 25, 21]));
%   rlWlI = squeeze(ncread(ncfileWl, 'rl', [ipty, iptx, 1, 1], [1, 1, 25, 21]));
  rlDisI = squeeze(rlDis(ipty, iptx, :, :));  
  rlWlI = squeeze(rlWl(ipty, iptx, :, :));  
  
  ymxDis = squeeze(annualMaxDis(ipty, iptx, :));
  ymxWl = squeeze(annualMaxWl(ipty, iptx, :));
  
  cnd = dis > percentile(ymxDis, .10);
  dis = dis(cnd);
  wl = wl(cnd);

  if length(dis) < 5
    continue;
  end
  
  fitRl = polyfit(ymxDis, ymxWl, 1);
  fitMsrs = polyfit(dis, wl, 1);
  
  xst(ist) = ptx;
  yst(ist) = pty;
  slopeMsrs(ist) = fitMsrs(1);
  slopeMdl(ist) = fitRl(1);
  
  ratio = slopeMdl(ist)/slopeMsrs(ist);
  
  if plotFigure
    figmax = figure('position', [100, 100, 600, 600]);
    pyrl = scatter(rlDisI(:), rlWlI(:));
    hold on;
    pym = plot(ymxDis, ymxWl, 'o');
    pmsr = plot(dis, wl, 'o');
    %pmsrYmax = plot(msrDisYM, msrWlYM, 'ok', 'markerfacecolor', 'k');
    grid on;
    legend([pyrl pym pmsr], {'EVA fit', 'cordex y maxima', 'measure'}, 'location', 'se');
    xlabel('discharge (m^3)');
    ylabel('water level (m)');
    placeStrId = ['station_' num2str(st) '_x=' num2str(ptx) '_y=' num2str(pty)];    
    title(strrep(placeStrId, '_', ' '));

    if ratio < .5
      filePrefix = 'low';
    elseif (.5 <= ratio) && (ratio <= 1.5)
      filePrefix = 'ok';
    else
      filePrefix = 'high';
    end
    
    plotFlPath = fullfile(outPlotDir, [filePrefix '_wlVsDis_' placeStrId '.png']);
    saveas(figmax, plotFlPath);
    close(figmax);
  end
end

fg = figure;
lonlims = [-15 30];
latlims = [35 65];
homedir = '/DATA/mentalo/';
bndDataFilePath = fullfile(homedir, 'Dropbox/LISCOAST Team Folder/Data/World_land_boundaries.mat');
dt = load(bndDataFilePath);
na.X=dt.data.X;
na.Y=dt.data.Y;
handls=make_land_patch(na,lonlims,latlims);
xlim(lonlims);
ylim(latlims);
hold on;
ratio = slopeMdl./slopeMsrs;
pltval = zeros(size(ratio))*nan;
pltval(ratio < .5) = 0;
pltval((ratio >= .5) & (ratio < 2)) = 1;
pltval((ratio >= 2) & (ratio < 3)) = 2;
pltval(ratio >= 3) = 3;
cmap = [[1 .5 .5]; [1 1 1]; [.5 .5 1]; [.2 .2 1]];
scatter(xst, yst, 30, pltval, 'filled'); cb = colorbar;
set(gca,'clim',[0 3]);
colormap(cmap);
cb.Ticks = [.4 1.1 1.9 2.6];
cb.TickLabels = {'< 0.5', '[0.5 2]', '[2 3]', '> 3'};
%ylabel(cb, 'm_{mdl}/m_{obs}');
text(-13, 63, ['Slope level - discharge,' newline 'ratio model/observations'], 'fontsize', 13);
fg.PaperPositionMode = 'auto';
print(fg, outPng, '-dpng', '-r400' );

function msrs = loadMsrsFromFile(stationMsrsJsFile, stationMsrsJsCacheFile)
  if exist(stationMsrsJsCacheFile, 'file')
    dt = load(stationMsrsJsCacheFile);
    %allStationsMsrs = dt.allStationsMsrs;
    msrs = dt.msrs;
  else
  % if isempty(allStationsMsrs)
    disp('Loading all the measurements. Might take a while ...');
    allStationsMsrs = jsondecode(fileread(stationMsrsJsFile));
    msrs = lfEvaLoadDisWlObservations(allStationsMsrs);
    save(stationMsrsJsCacheFile, 'allStationsMsrs', 'msrs');
  end
end

function [iptx, ipty] = locateLisfloodPixel(ptx, pty, lon, lat, testVl)
  dist = sqrt((lon-ptx).^2 + (lat-pty).^2);
  mindist = min(dist(:));
  disp(['mindist = ' num2str(mindist)]);
  ii_ = find(dist==mindist);
  [ipty, iptx] = ind2sub(size(dist), ii_);

  % looking for the right pixel (the one with max discharge)
  ix_ = nan;
  iy_ = nan;
  vl_ = 0;
  for iy = ipty-1:ipty+1
    for ix = iptx-1:iptx+1
      vl = testVl(iy, ix, 1);
      if isnan(vl)
        vl = 0;
      end
      if vl > vl_
        ix_ = ix;
        iy_ = iy;
        vl_ = vl;
      end
    end
  end

  if isnan(ix_)
    error('point not found!!');
  end
  iptx = ix_;
  ipty = iy_;
end
