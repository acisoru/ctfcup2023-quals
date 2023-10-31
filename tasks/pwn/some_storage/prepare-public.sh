#!/bin/bash
set -e

curdir=$(pwd)
pubtemp=$(mktemp -d)

cp -R deploy $pubtemp/some_storage
cd $pubtemp

sed -i '/image:/d' some_storage/docker-compose.yml

zip -9 -r some_storage.zip some_storage

cd $curdir
mv $pubtemp/some_storage.zip public
rm -rf $pubtemp