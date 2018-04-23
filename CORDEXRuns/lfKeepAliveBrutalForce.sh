#!/bin/bash

curdir=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)
echo "current directory: "$curdir

py=/eos/jeodpp/data/projects/CRITECH/ADAPTATION/usr/anaconda_LISFLOOD/bin/python

while true
do
  date
  echo 'removing possible hang jobs'
  condor_q | grep lf | grep ' H ' | awk '{print $1}' | xargs condor_rm
  echo 'sleeping for some minutes'
  sleep 120
  echo 'resubmitting dead jobs'
  $py lfLaunchAllCORDEX.py
  date
  echo 'sleeping for 20 minutes'
  sleep 1200
done

