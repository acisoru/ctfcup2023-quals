#!/bin/bash
set -e

curdir=$(pwd)
pubtemp=$(mktemp -d)

cp -R deploy $pubtemp/spy
cd $pubtemp

sed -i '/image:/d' spy/docker-compose.yml

zip -9 -r spy.zip spy

cd $curdir
mv $pubtemp/spy.zip public
rm -rf $pubtemp
