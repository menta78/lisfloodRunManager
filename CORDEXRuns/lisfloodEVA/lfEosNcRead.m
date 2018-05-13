function vls = lfEosNcRead(varargin)

  maxntest = 200;
  
  for itest = 1:maxntest
    try
      vls = ncread(varargin{:});
      return;
    catch
      disp('          problems reading files, retrying again in 1 second');
      pause(1);
    end
  end
  vls = ncread(varargin{:});

end
