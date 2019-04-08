function lfStatEvaWriteOutNcFile( xx, yy, returnPeriodsInYears, years, evaData, lon, lat, retLevNcOutFilePath )

  nxx = length(xx);
  nyy = length(yy);
  nretper = length(returnPeriodsInYears);
  nyr = length(years);
  
  if exist(retLevNcOutFilePath, 'file')
    delete(retLevNcOutFilePath);
  end
  
  nccreate(retLevNcOutFilePath, 'rl', 'dimensions', {'x', nxx, 'y', nyy, 'return_period', nretper});
  ncwrite(retLevNcOutFilePath, 'rl', evaData.retLevGEV);

  nccreate(retLevNcOutFilePath, 'se_rl', 'dimensions', {'x', nxx, 'y', nyy, 'return_period', nretper});
  ncwrite(retLevNcOutFilePath, 'se_rl', evaData.retLevErrGEV);

  nccreate(retLevNcOutFilePath, 'shape_fit', 'dimensions', {'x', nxx, 'y', nyy});
  ncwrite(retLevNcOutFilePath, 'shape_fit', evaData.shapeGEV);

  nccreate(retLevNcOutFilePath, 'se_shape', 'dimensions', {'x', nxx, 'y', nyy});
  ncwrite(retLevNcOutFilePath, 'se_shape', evaData.shapeGEVErr);

  nccreate(retLevNcOutFilePath, 'scale_fit', 'dimensions', {'x', nxx, 'y', nyy});
  ncwrite(retLevNcOutFilePath, 'scale_fit', evaData.scaleGEV);

  nccreate(retLevNcOutFilePath, 'se_scale', 'dimensions', {'x', nxx, 'y', nyy});
  ncwrite(retLevNcOutFilePath, 'se_scale', evaData.scaleGEVErr);

  nccreate(retLevNcOutFilePath, 'location_fit', 'dimensions', {'x', nxx, 'y', nyy});
  ncwrite(retLevNcOutFilePath, 'location_fit', evaData.locationGEV);

  nccreate(retLevNcOutFilePath, 'se_location', 'dimensions', {'x', nxx, 'y', nyy});
  ncwrite(retLevNcOutFilePath, 'se_location', evaData.locationGEVErr);

  nccreate(retLevNcOutFilePath, 'x', 'dimensions', {'ix', nxx});
  ncwrite(retLevNcOutFilePath, 'x', xx);

  nccreate(retLevNcOutFilePath, 'y', 'dimensions', {'iy', nyy});
  ncwrite(retLevNcOutFilePath, 'y', yy);

  nccreate(retLevNcOutFilePath, 'return_period', 'dimensions', {'nretper', nretper});
  ncwrite(retLevNcOutFilePath, 'return_period', returnPeriodsInYears);

  
  nccreate(retLevNcOutFilePath, 'lon', 'dimensions', {'x', nxx, 'y', nyy});
  ncwrite(retLevNcOutFilePath, 'lon', lon);

  nccreate(retLevNcOutFilePath, 'lat', 'dimensions', {'x', nxx, 'y', nyy});
  ncwrite(retLevNcOutFilePath, 'lat', lat);

    
  nccreate(retLevNcOutFilePath, 'le', 'dimensions', {'x', nxx, 'y', nyy, 'year', nyr});
  ncwrite(retLevNcOutFilePath, 'le', evaData.le);

  nccreate(retLevNcOutFilePath, 'rp', 'dimensions', {'x', nxx, 'y', nyy, 'year', nyr});
  ncwrite(retLevNcOutFilePath, 'rp', evaData.rp);

  nccreate(retLevNcOutFilePath, 'se_rp_sup', 'dimensions', {'x', nxx, 'y', nyy, 'year', nyr});
  ncwrite(retLevNcOutFilePath, 'se_rp_sup', evaData.se_rp_sup);

  nccreate(retLevNcOutFilePath, 'se_rp_inf', 'dimensions', {'x', nxx, 'y', nyy, 'year', nyr});
  ncwrite(retLevNcOutFilePath, 'se_rp_inf', evaData.se_rp_inf);
    
  nccreate(retLevNcOutFilePath, 'frq', 'dimensions', {'x', nxx, 'y', nyy, 'year', nyr});
  ncwrite(retLevNcOutFilePath, 'frq', evaData.frq);
  

  nccreate(retLevNcOutFilePath, 'year', 'dimensions', {'iyear', nyr});
  ncwrite(retLevNcOutFilePath, 'year', years);
  
end

