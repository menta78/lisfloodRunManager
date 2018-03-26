#!/bin/bash

curdir=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)
echo "current directory: "$curdir

while true
do
  date
  echo 'removing possible hang jobs'
  condor_q | grep lf | grep ' H ' | awk '{print $1}' | xargs condor_rm
  echo 'sleeping for a couple of minutes'
  sleep 120
  echo 'resubmitting dead jobs'
  python lfLaunchAllCORDEX.py
  date
  echo 'sleeping for 20 minutes'
  sleep 1200
done

