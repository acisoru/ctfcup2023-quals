#!/bin/bash

set -e

curdir=$(pwd)
pubtemp=$(mktemp -d)

cp -R deploy $pubtemp/crp-murdata
cd $pubtemp

sed -i '' '/image:/d' crp-murdata/docker-compose.yml
sed -i '' 's/ADMIN_PASSWORD=.*/ADMIN_PASSWORD=example/g' crp-murdata/entry.sh

zip -9 -r crp-murdata.zip crp-murdata

cd $curdir
mv $pubtemp/crp-murdata.zip public
rm -rf $pubtemp
