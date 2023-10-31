#!/bin/bash
set -e

curdir=$(pwd)
pubtemp=$(mktemp -d)

echo $pubtemp

cp -R deploy $pubtemp/mistakes
cd $pubtemp

sed -r -i '' 's/ctfcup\{[^}]+\}/ctfcup{fake_flag}/g' mistakes/docker-compose.yaml

zip -9 -r web-mistakes.zip mistakes

cd $curdir
mv $pubtemp/web-mistakes.zip public/
rm -rf $pubtemp