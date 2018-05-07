function vls = lfEosNcRead(varargin)

  maxntest = 100;
  
  for itest = 1:maxntest
    try
      vls = ncread(varargin{:});
      return;
    catch
    end
  end
  vls = ncread(varargin{:});

end
