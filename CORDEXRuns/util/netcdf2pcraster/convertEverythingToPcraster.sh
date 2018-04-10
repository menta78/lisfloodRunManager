#!/bin/bash

currdir=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)

cd $currdir
convertScrpt=convertToPcraster.sh
convertLogFl=convertToPcraster.log

drs=`find ./ -maxdepth 3 -type d -name 'other'`

for d in $drs;
do
  echo 'launching for directory '$d
  cp $convertScrpt $d
  cd $d
  ./$convertScrpt > $convertLogFl 2>&1 &
  cd $currdir
  echo '  sleeping for a few seconds ...'
  sleep 5
done


