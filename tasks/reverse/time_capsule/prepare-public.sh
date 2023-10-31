#!/bin/sh
set -e

curdir="$PWD"
pubtemp="$(mktemp -d)"

mkdir "$pubtemp/time_capsule"
cp dev/time_capsule "$pubtemp/time_capsule/"
cp dev/flag.txt.enc "$pubtemp/time_capsule"

cd "$pubtemp"

zip -9 -r time_capsule.zip time_capsule

cd "$curdir"
mv "$pubtemp/time_capsule.zip" public

rm -rf "$pubtemp"
