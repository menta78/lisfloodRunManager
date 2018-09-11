ncfile = '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/lisfloodEVA/test/dis_rcp85_CLMcom-CCLM4-8-17_BC_ICHEC-EC-EARTH_wuConst_statistics.nc';

placeStrId = 'test';

%danube
ptx = 5003849;
pty = 2477241;
%ptx = 5164312;
%pty = 2565903;

%gb
%ptx = 3494535;
%pty = 3510292;

%po
%ptx = 4324807;
%pty = 2440070;

%finland
ptx = 5144028;
pty = 4435352;

figPath = '/ClimateRun4/LISCOAST2/Dropbox/LISCOAST_Team_Folder/Data_GlobalErosionAssessmentDatasets_EVA_EROSIONdissipative/fig';

testRp0 = 10;
testRp1 = 20;
testRp2 = 50;
testRp3 = 100;

xx = ncread(ncfile, 'x');
yy = ncread(ncfile, 'y');

iptx = knnsearch(xx, ptx);
ipty = knnsearch(yy, pty);


outPngFl = fullfile(figPath, [placeStrId '.png']);

yrs = ncread(ncfile, 'year_all');
annualMax = squeeze(ncread(ncfile, 'year_max', [ipty, iptx, 1], [1, 1, length(yrs)]));

returnPeriod = ncread(ncfile, 'return_period');
irp0 = find(returnPeriod == testRp0);
irp1 = find(returnPeriod == testRp1);
irp2 = find(returnPeriod == testRp2);
irp3 = find(returnPeriod == testRp3);

rl0 = squeeze(ncread(ncfile, 'rl', [ipty, iptx, 1, irp0], [1, 1, 25, 1]));
rl1 = squeeze(ncread(ncfile, 'rl', [ipty, iptx, 1, irp1], [1, 1, 25, 1]));
rl2 = squeeze(ncread(ncfile, 'rl', [ipty, iptx, 1, irp2], [1, 1, 25, 1]));
rl3 = squeeze(ncread(ncfile, 'rl', [ipty, iptx, 1, irp3], [1, 1, 25, 1]));
rlyear = ncread(ncfile, 'year');


fig = figure('position', [100, 100, 1000, 500]);
pym = plot(yrs, annualMax, 'o');
hold on;
prl0 = plot(rlyear, rl0);
prl1 = plot(rlyear, rl1);
prl2 = plot(rlyear, rl2);
prl3 = plot(rlyear, rl3);

ax = gca;
ax.FontSize = 13;
grid on;

legend([pym, prl0, prl1, prl2, prl3], {'Annual Maxima', '10-year r.l.', '20-year r.l.', '50-year r.l.', '100-year r.l.'}, 'location', 'southwest', 'box', 'off', 'fontsize', 13);

title(placeStrId);

saveas(fig, outPngFl);



