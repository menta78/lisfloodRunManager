function [ tmstmp, xx, yy, vls ] = lfDisLoadFromNcOneScen( ncFilePattern, xxyyStartIndx, xxyyEndIndx, varargin )
  args.ncvarname = 'dis';
  args = lfEasyParseNamedArgs(varargin, args);
  ncvarname = args.ncvarname;
  
  fls = strsplit(strtrim(ls(ncFilePattern)));
  fls = sort(fls);

  nfl = length(fls);
  
  szxx = ( xxyyEndIndx(1) - xxyyStartIndx(1) ) + 1;
  szyy = ( xxyyEndIndx(2) - xxyyStartIndx(2) ) + 1;
  guessNTime = nfl*366;
  vls = zeros([szxx szyy guessNTime]);
  tmstmp = zeros([guessNTime 1]);

  cnt = xxyyEndIndx - xxyyStartIndx + 1;
  
  flnm = fls{1};
  xx = lfEosNcRead(flnm, 'x', xxyyStartIndx(1), cnt(1));
  yy = lfEosNcRead(flnm, 'y', xxyyStartIndx(2), cnt(2));
  
  totNTime = 0;
  for ifl = 1:nfl
    flnm = fls{ifl};
    tks = regexp(flnm, '(.*)_([0-9]{4})([0-9]{2})([0-9]*).nc', 'tokens');
    yrstr = tks{1}{2};
    disp(['      loading year ' yrstr]);
    disp(['        file ' flnm]);
    yr = str2double(yrstr);
    
    tm = lfEosNcRead(flnm, 'time');
    tmstmpii = datenum(yr, 1, 1) + tm - min(tm);
    tmStrtIndx = totNTime + 1;
    ntime = length(tm);
    totNTime = totNTime + ntime;
    tmEndIndx = totNTime;

    tmstmp(tmStrtIndx:tmEndIndx) = tmstmpii;
    
    vlsii = lfEosNcRead(flnm, ncvarname, [xxyyStartIndx(:); 1], [cnt(:); ntime]);
    vls(:, :, tmStrtIndx:tmEndIndx) = vlsii;
  end
  
  tmstmp = tmstmp(1:totNTime);
  vls = vls(:, :, 1:totNTime);
   
end

