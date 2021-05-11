#!/bin/bash

srcRootDir=/DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/lisflood/input/LAEAETRS89_BIAS_CORDEX/
destRootDir=/DATA/ClimateData/cordexEurope/yearlymeans/rawData
cdoexe=/STORAGE/usr/cdo/1.7.2/bin/cdo.sh

scenarios='historical rcp45 rcp85'
varname='ta'

function elabScenario() {
  mdl=$1
  scen=$2
  echo '  elabroating '$mdl', '$scen
  cd $scen
 #sleep 1
 #echo '    '`ls "$PWD/$varname".nc`
  flnm=$varname".nc"
  destdir=$destRootDir/$mdl/$scen
  destflpth=$destdir/$flnm
  if [ -f $destflpth ];
  then
    echo '    output file already exists, skipping: '$destflpth
    return
  fi
  mkdir -p $destdir
  cmd="$cdoexe -yearmean $flnm $destflpth"
  echo '      cdo command: '$cmd
  $cmd
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

