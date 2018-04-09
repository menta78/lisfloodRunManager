#!/bin/bash

bashsrcdir=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)

py=/eos/jeodpp/data/projects/CRITECH/ADAPTATION/usr/anaconda_LISFLOOD/bin/python
asc2map=/eos/jeodpp/data/projects/CRITECH/ADAPTATION/usr/anaconda_LISFLOOD/bin/asc2map
nc2pcr=/eos/jeodpp/data/projects/CRITECH/ADAPTATION/src/git/lisfloodRunManager/CORDEXRuns/util/netcdf2pcraster/netcdf2pcraster.py
nc2pcrTrgtMap=/eos/jeodpp/data/projects/CRITECH/ADAPTATION/src/git/lisfloodRunManager/CORDEXRuns/util/netcdf2pcraster/prototype.map
outdir=$bashsrcdir/pcraster

mkdir $outdir

set -e

#huss: specific humidity
#rlds: surface downwelling longwave radiation
#rlus: surface upwelling longwave radiation
#rsds: surface downwelling shortwave radiation
#rsus: surface upwelling shortwave radiation

#converting specific humidity to vapour pressure
hussFl=huss_BCed_1981-2010_1981-2010.nc
psFl=psl_BCed_1981-2010_1981-2010.nc
avpFl=avp_BCed_1981-2010_1981-2010.nc
if [ ! -f $avpFl ]; then
  cdo mul $hussFl $psFl tmpPrs.nc
  cdo -expr,'avp=huss/62.2' tmpPrs.nc $avpFl
  rm tmpPrs.nc
else
  echo 'file '$avpFl' already exists'
fi

#converting downwelling solar radiation to J/m^2/Day, from J/m^2/s
radFl=rsds_BCed_1981-2010_1981-2010.nc
radFlConv=rsds_JM2Day_BCed_1981-2010_1981-2010.nc
if [ ! -f $radFlConv ]; then
  cdo mulc,86400 $radFl $radFlConv
else
  echo 'file '$radFlConv' already exists'
fi

filenames='avp_BCed_1981-2010_1981-2010.nc
rsds_JM2Day_BCed_1981-2010_1981-2010.nc
sfcWind_BCed_1981-2010_1981-2010.nc
Tmax_BCed_1981-2010_1981-2010.nc
Tmin_BCed_1981-2010_1981-2010.nc'

ncvarnames='avp
rsds
sfcWind
tasmaxAdjust
tasminAdjust'

prcvarnames='vp
rg
ws
tx
tn'

i=1
for f in $filenames
do
  echo
  ncvar=`echo $ncvarnames | cut -d ' ' -f $i`
  pcrvar=`echo $prcvarnames | cut -d ' ' -f $i`
  nc2pcrCmd=$py' '$nc2pcr' --asc2mapcmd '$asc2map' --clone '$nc2pcrTrgtMap' --ncvar '$ncvar' -pcrvar '$pcrvar' -r '$f' '$outdir
  echo '  elaborating '$f', nc variable '$ncvar', prcvar '$prcvar'. Command:'
  echo $nc2pcrCmd
  $nc2pcrCmd
  i=$(($i+1))
  echo
done

