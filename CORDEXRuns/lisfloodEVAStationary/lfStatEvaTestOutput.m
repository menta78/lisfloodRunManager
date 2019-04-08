%ncfile = '/ClimateRun4/multi-hazard/eva/historical_dis_min_NCEP_year_statistics.nc';
ncfile = '/ClimateRun4/multi-hazard/eva/historical_dis_monMeanMin_NCEP_year_statistics.nc';

le = ncread(ncfile, 'le');
rp = ncread(ncfile, 'rp');

% xx = ncread(ncfile, 'lon');
% yy = ncread(ncfile, 'lat');
xx = ncread(ncfile, 'x');
yy = ncread(ncfile, 'y');

%danube
%placeStrId = 'danube';
%ptx = 5003849;
%pty = 2477241;
%placeStrId = 'danube2';
%ptx = 5164312;
%pty = 2565903;

%gb
%placeStrId = 'gb';
%ptx = 3494535;
%pty = 3510292;

%po
%placeStrId = 'po';
%ptx = 4324807;
%pty = 2440070;

%finland
%placeStrId = 'po';
%ptx = 5144028;
%pty = 4435352;


% random choice
[yymtx, xxmtx] = meshgrid(yy, xx);
lemean = mean(le, 3);
cnd = lemean > 20; % the points where the mean annual min is > 20 m^2/s

xxgt = xxmtx(cnd);
yygt = yymtx(cnd);

ipt = 10000;
% ipt = 5000;
% ipt = 4000;
% ipt = 2000;
% ipt = 1000;
% ipt = 500;

ptx = xxgt(ipt);
pty = yygt(ipt);
placeStrId = ['location_x=' num2str(ptx) '_y=' num2str(pty)];



figPath = '/ClimateRun4/multi-hazard/eva/diagnostics/';

testRp0 = 10;
testRp1 = 20;
testRp2 = 50;
testRp3 = 100;

iptx = knnsearch(xx, ptx);
ipty = knnsearch(yy, pty);


outPngFl = fullfile(figPath, [placeStrId '.png']);

yrs = ncread(ncfile, 'year');
annualMax = squeeze(le(iptx, ipty, :));

returnPeriod = ncread(ncfile, 'return_period');
irp0 = find(returnPeriod == testRp0);
irp1 = find(returnPeriod == testRp1);
irp2 = find(returnPeriod == testRp2);
irp3 = find(returnPeriod == testRp3);

rl0 = squeeze(ncread(ncfile, 'rl', [iptx, ipty, irp0], [1, 1, 1]));
rl1 = squeeze(ncread(ncfile, 'rl', [iptx, ipty, irp1], [1, 1, 1]));
rl2 = squeeze(ncread(ncfile, 'rl', [iptx, ipty, irp2], [1, 1, 1]));
rl3 = squeeze(ncread(ncfile, 'rl', [iptx, ipty, irp3], [1, 1, 1]));

rpPt = squeeze(rp(iptx, ipty, :));


fig = figure('position', [100, 100, 1000, 500]);
pym = plot(yrs, annualMax, 'o');
hold on;
prl0 = plot(yrs, rl0*ones(size(yrs)));
prl1 = plot(yrs, rl1*ones(size(yrs)));
prl2 = plot(yrs, rl2*ones(size(yrs)));
prl3 = plot(yrs, rl3*ones(size(yrs)));
ylim([0, max(annualMax)]);

ax = gca;
ax.FontSize = 13;
grid on;

legend([pym, prl0, prl1, prl2, prl3], {'Annual Maxima', '10-year r.l.', '20-year r.l.', '50-year r.l.', '100-year r.l.'}, 'location', 'southwest', 'box', 'off', 'fontsize', 13);

title(placeStrId);

saveas(fig, outPngFl);



