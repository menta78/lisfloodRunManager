function [ tmstmp, xx, yy, vls ] = lfDisLoadFromNcOneScen( ncFilePattern, xxyyStartIndx, xxyyEndIndx, varargin )
  args.ncvarname = 'dis';
  args = lfEasyParseNamedArgs(varargin, args);
  ncvarname = args.ncvarname;

  cnt = xxyyEndIndx - xxyyStartIndx + 1;
  
  fls = strsplit(strtrim(ls(ncFilePattern)));
  fls = sort(fls);

  flnm = fls{1};
  tmstmp = double(jrc_ncreadtime(flnm, 'time'));
  ntime = length(tmstmp);
  try
    vls = ncread(flnm, ncvarname, [xxyyStartIndx(:); 1], [cnt(:); ntime]);
  catch
    vls = ncread(flnm, [ncvarname, 'Adjust'], [xxyyStartIndx(:); 1], [cnt(:); ntime]);
  end
  xx = ncread(flnm, 'x', xxyyStartIndx(1), cnt(1));
  yy = ncread(flnm, 'y', xxyyStartIndx(2), cnt(2));
   
end

