#!/bin/bash
set -e

curdir=$(pwd)
pubtemp=$(mktemp -d)

cp -R deploy $pubtemp/novosti
cd $pubtemp

zip -9 -r novosti.zip novosti

cd $curdir
mv $pubtemp/novosti.zip public
rm -rf $pubtemp
