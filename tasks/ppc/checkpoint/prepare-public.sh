#!/bin/bash
set -e

curdir=$(pwd)
pubtemp=$(mktemp -d)

cp -R deploy $pubtemp/checkpoint
cd $pubtemp

rm -rf checkpoint/voices
zip -9 -r checkpoint.zip checkpoint

cd $curdir
mv $pubtemp/checkpoint.zip public
rm -rf $pubtemp
