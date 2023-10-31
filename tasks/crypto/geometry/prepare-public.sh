#!/bin/sh
set -e

curdir="$PWD"
pubtemp="$(mktemp -d)"

mkdir "$pubtemp/geometry"

cp dev/geometry/client.py "$pubtemp/geometry"
cp dev/geometry/server.py "$pubtemp/geometry"
cp dev/geometry/geometry.py "$pubtemp/geometry"
cp dev/geometry.pcapng "$pubtemp/geometry"

cd "$pubtemp"

zip -9 -r geometry.zip geometry

cd "$curdir"
mv "$pubtemp/geometry.zip" public

rm -rf "$pubtemp"
