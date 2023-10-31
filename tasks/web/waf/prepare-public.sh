#!/bin/bash
set -e

curdir=$(pwd)
pubtemp=$(mktemp -d)

cp -R deploy $pubtemp/web-waf
cp public-sql.db $pubtemp/web-waf/sql.db

cd $pubtemp

sed -i '' '/image:/d' web-waf/docker-compose.yml

zip -9 -r web-waf.zip web-waf

cd $curdir
mv $pubtemp/web-waf.zip public
rm -rf $pubtemp
