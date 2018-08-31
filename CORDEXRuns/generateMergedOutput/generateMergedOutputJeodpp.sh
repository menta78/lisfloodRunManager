#!/bin/bash

var=$1
echo 'generating variable '$var

py=/eos/jeodpp/data/projects/CRITECH/ADAPTATION/usr/anaconda_LISFLOOD/bin/python
while true;
do
  $py generateMergedOutput.py /eos/jeodpp/data/projects/CRITECH/ADAPTATION/ClimateRuns/LisfloodEuroCordex/ /eos/jeodpp/data/projects/WEFE/LISFLOOD-Europe/EuroCordexMerged/ $var
  sleep 5
done
