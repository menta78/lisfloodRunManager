ncfile1 = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/lisfloodEVA/test/dis_rcp85_CLMcom-CCLM4-8-17_BC_ICHEC-EC-EARTH_wuConst_statistics.nc';
ncfile1 = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/lisfloodEVA/test/projection_dis_rcp85_IPSL-INERIS-WRF331F_BC_wuChang_statistics.nc';
ncfile1 = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/lisfloodEVA/test/projection_dis_rcp85_CLMcom-CCLM4-8-17_BC_MPI-M-MPI-ESM-LR_wuConst_statistics.nc';
ncfile2 = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/lisfloodEVA/test/projection_wl_rcp85_CLMcom-CCLM4-8-17_BC_MPI-M-MPI-ESM-LR_wuConst_statistics.nc';

figPath = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/lisfloodEVA/test/fig';

lonlatncfile = './lonlat.nc';

stationMsrsJsFile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/verifyOutput/waterLevel/allStationMeasurements_operational.json';


testRp0 = 10;
testRp1 = 20;
testRp2 = 50;
testRp3 = 100;

xx1 = ncread(ncfile1, 'x');
yy1 = ncread(ncfile1, 'y');

%%% SELECTION OF KNOWN POINTS X, Y
%placeStrId = 'test';

%danube
%ptx = 5003849;
%pty = 2477241;
%ptx = 5164312;
%pty = 2565903;

%gb
%ptx = 3494535;
%pty = 3510292;

%po
%ptx = 4324807;
%pty = 2440070;

%finland
%ptx = 5144028;
%pty = 4435352;

% iptx = knnsearch(xx1, ptx);
% ipty = knnsearch(yy1, pty);
%%%%%%%%%%%%%%%%%


%%% SELECTION OF KNOWN POINTS lon, lat
%placeStrId = 'efas 2, Danube Hofkirchen';
%statId = '2';
%ptx = 13.115212;
%pty = 48.676627;

% placeStrId = 'efas 10, Elbe Wittenberg / Lutherstadt';
% statId = '10';
% ptx = 12.259913;
% pty = 53.456704;

placeStrId = 'efas 109, Rhine Sauer';
statId = '109';
ptx = 6.3591708756;
pty = 49.8509211736;

% placeStrId = 'efas 99, Danube Medno';
% statId = '99';
% ptx = 14.4405;
% pty = 46.1225;

% placeStrId = 'efas 110, Rhine Boos';
% statId = '110';
% ptx = 7.7200274261;
% pty = 49.780141099;

%placeStrId = 'efas 153, Rhine Lobith'; % this has observiations of wl from 2009
%statId = '153';
%ptx = 6.1083333333;
%pty = 51.8444444444;

% placeStrId = 'efas 181, Danube Kajetansbrücke';
% statId = '181';
% ptx = 10.5116378567;
% pty = 46.951978561;

% placeStrId = 'efas 245, Danube Korvingrad';
% statId = '245';
% ptx = 21.838303;
% pty = 43.219521;

% placeStrId = 'efas 334, Ticino (Po) Bellinzona';
% statId = '334';
% ptx = 9.009292605;
% pty = 46.19375997;

lon = ncread(lonlatncfile, 'lon')';
lat = ncread(lonlatncfile, 'lat')';
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
    vl = ncread(ncfile1, 'rl', [iy, ix, 1, 1], [1, 1, 1, 1]);
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

if ~exist('allStationsMsrs', 'var')
  disp('Loading all the measurements. Might take a while ...');
  allStationsMsrs = jsondecode(fileread(stationMsrsJsFile));
end
stid = string({allStationsMsrs(:).StationID}');
stationCnd = strcmpi(stid, statId);
statMsrs = allStationsMsrs(stationCnd);
msrVrbl = string({statMsrs(:).Variable}');
msrDis = [statMsrs(strcmpi(msrVrbl, "D")).AvgValue]';
msrDisTStr = string({statMsrs(strcmpi(msrVrbl, "D")).Timestamp}');
msrDisTm = datenum(datetime(msrDisTStr, 'inputformat', 'yyyy-MM-dd HH:mm:ss'));
msrDisYM = tsEvaComputeAnnualMaxima([msrDisTm msrDis]);
msrWl = [statMsrs(strcmpi(msrVrbl, "W")).AvgValue]';
msrWlTStr = string({statMsrs(strcmpi(msrVrbl, "W")).Timestamp}');
msrWlTm = datenum(datetime(msrWlTStr, 'inputformat', 'yyyy-MM-dd HH:mm:ss'));
msrWlYM = tsEvaComputeAnnualMaxima([msrWlTm msrWl]);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% % SELECTION OF RANDOM POINTS
% annualMin_ = squeeze(ncread(ncfile1, 'year_min'));
% xx = ncread(lonlatncfile, 'lon');
% yy = ncread(lonlatncfile, 'lat');
% xx1 = ncread(ncfile1, 'x');
% yy1 = ncread(ncfile1, 'y');
% [xxmtx, yymtx] = meshgrid(xx1, yy1);
% lemean = mean(annualMin_, 3);
% cnd = lemean > 20; % the points where the mean annual min is > 20 m^2/s
% 
% xxgt = xxmtx(cnd);
% yygt = yymtx(cnd);
% 
% % ipt = 10000;
% % ipt = 5000;
% % ipt = 4000;
% % ipt = 2000;
% % ipt = 1000;
% % ipt = 500;
% 
% ptx = xxgt(ipt);
% pty = yygt(ipt);
% placeStrId = ['location_x=' num2str(ptx) '_y=' num2str(pty)];

% iptx = knnsearch(xx1, ptx);
% ipty = knnsearch(yy1, pty);
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


outPngFl = fullfile(figPath, ['disVsWl_' statId '.png']);

yrs = ncread(ncfile1, 'year_all');

returnPeriod = ncread(ncfile1, 'return_period');
irp0 = find(returnPeriod == testRp0);
irp1 = find(returnPeriod == testRp1);
irp2 = find(returnPeriod == testRp2);
irp3 = find(returnPeriod == testRp3);

annualMax1 = squeeze(ncread(ncfile1, 'year_max', [ipty, iptx, 1], [1, 1, length(yrs)]));
rl0_1 = squeeze(ncread(ncfile1, 'rl', [ipty, iptx, 1, irp0], [1, 1, 25, 1]));
rl1_1 = squeeze(ncread(ncfile1, 'rl', [ipty, iptx, 1, irp1], [1, 1, 25, 1]));
rl2_1 = squeeze(ncread(ncfile1, 'rl', [ipty, iptx, 1, irp2], [1, 1, 25, 1]));
rl3_1 = squeeze(ncread(ncfile1, 'rl', [ipty, iptx, 1, irp3], [1, 1, 25, 1]));
rlyear = ncread(ncfile1, 'year');


annualMax2 = squeeze(ncread(ncfile2, 'year_max', [ipty, iptx, 1], [1, 1, length(yrs)]));
rl0_2 = squeeze(ncread(ncfile2, 'rl', [ipty, iptx, 1, irp0], [1, 1, 25, 1]));
rl1_2 = squeeze(ncread(ncfile2, 'rl', [ipty, iptx, 1, irp1], [1, 1, 25, 1]));
rl2_2 = squeeze(ncread(ncfile2, 'rl', [ipty, iptx, 1, irp2], [1, 1, 25, 1]));
rl3_2 = squeeze(ncread(ncfile2, 'rl', [ipty, iptx, 1, irp3], [1, 1, 25, 1]));


% figmax = figure('position', [100, 100, 1000, 500]);
% pym = plot(yrs, annualMax1, 'o');
% hold on;
% prl0 = plot(rlyear, rl0_1);
% prl1 = plot(rlyear, rl1_1);
% prl2 = plot(rlyear, rl2_1);
% prl3 = plot(rlyear, rl3_1);
% 
% ax = gca;
% ax.FontSize = 13;
% grid on;
% 
% legend([pym, prl0, prl1, prl2, prl3], {'Annual Maxima 1', '10-year r.l.', '20-year r.l.', '50-year r.l.', '100-year r.l.'}, 'location', 'southwest', 'box', 'off', 'fontsize', 13);
% 
% title(placeStrId);
% 
% 
% figmax = figure('position', [100, 100, 1000, 500]);
% pym = plot(yrs, annualMax2, 'o');
% hold on;
% prl0 = plot(rlyear, rl0_2);
% prl1 = plot(rlyear, rl1_2);
% prl2 = plot(rlyear, rl2_2);
% prl3 = plot(rlyear, rl3_2);
% 
% ax = gca;
% ax.FontSize = 13;
% grid on;
% 
% legend([pym, prl0, prl1, prl2, prl3], {'Annual Maxima 2', '10-year r.l.', '20-year r.l.', '50-year r.l.', '100-year r.l.'}, 'location', 'southwest', 'box', 'off', 'fontsize', 13);
% 
% title(placeStrId);


rl1 = squeeze(ncread(ncfile1, 'rl', [ipty, iptx, 1, 1], [1, 1, 25, 21]));
rl2 = squeeze(ncread(ncfile2, 'rl', [ipty, iptx, 1, 1], [1, 1, 25, 21]));


figmax = figure('position', [100, 100, 600, 600]);
pyrl = scatter(rl1(:), rl2(:));
hold on;
pym = plot(annualMax1, annualMax2, 'o');
pmsr = plot(msrDis, msrWl, 'o');
pmsrYmax = plot(msrDisYM, msrWlYM, 'ok', 'markerfacecolor', 'k');
grid on;
legend([pyrl pym pmsrYmax pmsr], {'EVA fit', 'cordex y maxima', 'measure y maxima', 'measure'}, 'location', 'se');
xlabel('discharge (m^3)');
ylabel('water level (m)');
title(placeStrId);



saveas(figmax, outPngFl);



