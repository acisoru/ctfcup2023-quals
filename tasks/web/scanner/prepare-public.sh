#!/bin/bash
set -e

curdir=$(pwd)
pubtemp=$(mktemp -d)

cp -R deploy $pubtemp/web-scanner
cd $pubtemp

sed -i '' '/image:/d' web-scanner/docker-compose.yml

zip -9 -r web-scanner.zip web-scanner

cd $curdir
mv $pubtemp/web-scanner.zip public
rm -rf $pubtemp
