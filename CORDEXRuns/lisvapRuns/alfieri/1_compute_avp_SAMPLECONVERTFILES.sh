#!/bin/bash
#$ -S /bin/sh

# L.A., 13/06/2014 - Adapted from a script by P.R.
# Calculate actual vapour pressure and prepare variables in units needed by Lisflood and Lisvap 

#usage: qsub -V -j y -N avp -q all.q -p -100 -o /climateRun4/HELIX/work/input/EU_CORDEX/log/1_comp_avp.log /nahaUsers/alfielo/CA/HELIX/script/eurocordex/1_compute_avp.sh

########################################################
homeDir='/climateRun4/HELIX/work/input/EU_CORDEX'


########################################################


cd $homeDir
models=$(ls -d $homeDir/?_*/)

for M in $models
do
  nc3Dir=$M'nc3'
  tempDir=$M'tmp'
  cd $M 
  mkdir $nc3Dir
  mkdir $tempDir
  chmod 755 $nc3Dir
  chmod 755 $tempDir
    
  files=$(ls huss*.nc | cut -c 5-)
  for E in $files
  do
  
  # Calculate actual vapour pressure: avp[mbar]=(huss*ps[Pa])/(0.622*100Pa/mb)
  cdo mul huss$E ps$E $tempDir/PROD$E 
  cdo divc,62.2 $tempDir/PROD$E $tempDir/avp$E 
  nccopy -k classic $tempDir/avp$E $nc3Dir/avp_nc3$E
  
  # Rsds from W*m-2 to J*m-2*d-1 (Used in Lisvap as incoming solar radiation (Rgd)))
  cdo mulc,86400 rsds$E $tempDir/rsds$E
  nccopy -k classic $tempDir/rsds$E $nc3Dir/rsds_nc3$E
  
  #Temperatures from Kelvin to Celsius
  cdo subc,273.15 tas$E $tempDir/tas$E
  cdo subc,273.15 tasmax$E $tempDir/tasmax$E
  cdo subc,273.15 tasmin$E $tempDir/tasmin$E
  nccopy -k classic $tempDir/tas$E $nc3Dir/tas_nc3$E
  nccopy -k classic $tempDir/tasmax$E $nc3Dir/tasmax_nc3$E
  nccopy -k classic $tempDir/tasmin$E $nc3Dir/tasmin_nc3$E
  
  #Precipitation from kg*m-2*s-1 to mm*day-1
  cdo mulc,86400 pr$E $tempDir/pr$E
  nccopy -k classic $tempDir/pr$E $nc3Dir/pr_nc3$E
  
  #Transform the remaining variable(s) from nc4 to nc3
  nccopy -k classic ${M}sfcWind$E $nc3Dir/sfcWind_nc3$E
  done
  
  rm -rf $tempDir
done

