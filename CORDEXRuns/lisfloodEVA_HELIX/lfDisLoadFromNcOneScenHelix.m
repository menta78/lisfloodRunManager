function [ tmstmp, xx, yy, vls ] = lfDisLoadFromNcOneScenHelix( ncFilePath, xxyyStartIndx, xxyyEndIndx )  
  cnt = xxyyEndIndx - xxyyStartIndx + 1;
  
  xx = ncread(ncFilePath, 'lon', xxyyStartIndx(1), cnt(1));
  yy = ncread(ncFilePath, 'lat', xxyyStartIndx(2), cnt(2));
  tmstmp = jrc_ncreadtime(ncFilePath, 'time');
  ntime = length(tmstmp);
  vls = ncread(ncFilePath, 'dis', [xxyyStartIndx(:); 1], [cnt(:); ntime]);
   
end

