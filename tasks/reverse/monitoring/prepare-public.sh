#!/bin/bash
set -e

curdir=$(pwd)
pubtemp=$(mktemp -d)

cp deploy/monitoring $pubtemp
cd $pubtemp

zip -9 monitoring.zip monitoring

cd $curdir
mv $pubtemp/monitoring.zip public
rm -rf $pubtemp
