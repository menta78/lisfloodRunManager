#!/bin/bash

srcRootDir=/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/lisflood/input/LAEAETRS89_BIAS_CORDEX
destRootDir=/DATA/ClimateData/cordexEurope/prMonthMax/
cdoexe=/STORAGE/usr/cdo/1.7.2/bin/cdo.sh

scenarios='historical  rcp45  rcp85'

function elabFile() {
  flSrc=$1
  flDest=$2
  if [ -f $flDest ];
  then
    echo '    output file already exists, skipping: '$flDest
    return
  fi
  cmd="$cdoexe -monmax $flSrc $flDest"
  echo $cmd
  $cmd
}

function elabScenario() {
  mdl=$1
  scen=$2
  echo '  elabroating '$mdl', '$scen

  f=$scen/pr.nc
 #ls $f

  destdir=$destRootDir/$mdl/$scen/
  mkdir -p $destdir
  destfl=$destdir/pr_monthlyMax.nc
  elabFile $f $destfl
}

cd $srcRootDir
for mdl in *;
do
  pth=$PWD
  if [ -d $mdl ];
  then
    echo 'processing model '$mdl
    cd $mdl
    for scen in $scenarios;
    do
      elabScenario $mdl $scen &
    done
    wait
    cd $pth
    sleep 1
    echo
    echo
  fi
done

