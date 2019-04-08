function lfEvaEstimRetPerForYearMinima(ncFlPathIn, ncFlPathOut)

bslnYear = 1995;
yrEva = ncread(ncFlPathIn, 'year');
yr = ncread(ncFlPathIn, 'year_all');
nyr = length(yr);
x = ncread(ncFlPathIn, 'x');
y = ncread(ncFlPathIn, 'y');
ibsln = find(yrEva == bslnYear);

ymin = -ncread(ncFlPathIn, 'year_min');

shp = ncread(ncFlPathIn, 'shape_fit_min');
scale = ncread(ncFlPathIn, 'scale_fit_min', [1, 1, ibsln], [size(shp, 1) size(shp, 2) 1]);
loc = -ncread(ncFlPathIn, 'location_fit_min', [1, 1, ibsln], [size(shp, 1) size(shp, 2) 1]);

nx = length(x);
ny = length(y);
npt = nx*ny;

%retPer_ = zeros([npt, nyr])*nan;
%freq_ = zeros([npt, nyr])*nan;

rp = ones(ny, nx, nyr)*nan;
frq = ones(ny, nx, nyr)*nan;

for ipt = 1:npt
%for ipt = 1:100000
  if mod(ipt, 100000) == 0 
    disp(['  ipt == ' num2str(ipt)]);
    disp(['  done ' num2str(ipt/npt*100) '%']);
  end
  iy = ceil(ipt/nx);
  ix = ipt - (iy - 1)*nx;

%   ptx = x(ilon);
%   pty = y(ilat);

  vlsymax = squeeze(ymin(iy, ix, :));
  shpi = shp(iy, ix);
  scli = scale(iy, ix, :);
  loci = loc(iy, ix, :);
  
  if ~all(isnan(vlsymax))
    dbstop 49;
  end
  
% if all(isnan(vlsymax)) || all(vlsymax == 0)
  if all(isnan(vlsymax)) || (max(vlsymax(1:30)) > -.5)
    continue;
  end
 
  [ymxRetPer, ymxExcP] = tsEvaGetReturnPeriodOfLevelGEV(shpi, scli, loci, vlsymax);
  ymxRetPer(imag(ymxRetPer) ~= 0) = 100; % these points are outside the dist domain (should happen rarely) choosing a high value
%   retPer_(ipt, :) = ymxRetPer;
%   freq_(ipt, :) = ymxExcP;
  rp(iy, ix, :) = ymxRetPer;
  frq(iy, ix, :) = ymxExcP;
end

% for ipt = 1:npt
%   if rem(ipt, 500) == 0
%     disp(['  done ' num2str(ipt/npt*100) '%']);
%   end
%   iy = ceil(ipt/nx);
%   ix = ipt - (iy - 1)*nx;
% 
%   rp(iy, ix, :) = retPer_(ipt, :);
%   frq(iy, ix, :) = freq_(ipt, :);
% end

disp('  writing the output file ...');

if exist(ncFlPathOut, 'file')
  delete(ncFlPathOut);
end

nccreate(ncFlPathOut, 'rp', 'dimensions', {'y', ny, 'x', nx, 'year', nyr});
ncwrite(ncFlPathOut, 'rp', rp);

nccreate(ncFlPathOut, 'frq', 'dimensions', {'y', ny, 'x', nx, 'year', nyr});
ncwrite(ncFlPathOut, 'frq', frq);

nccreate(ncFlPathOut, 'x', 'dimensions', {'ix', nx});
ncwrite(ncFlPathOut, 'x', x);

nccreate(ncFlPathOut, 'y', 'dimensions', {'iy', ny});
ncwrite(ncFlPathOut, 'y', y);

nccreate(ncFlPathOut, 'year', 'dimensions', {'iyear', nyr});
ncwrite(ncFlPathOut, 'year', yr);

