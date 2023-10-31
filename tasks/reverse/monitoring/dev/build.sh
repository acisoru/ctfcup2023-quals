#!/bin/bash

set -e

docker build -t monitoring-sus:latest -f Dockerfile.sus .
docker run --rm -it -v ./dist:/dist monitoring-sus:latest cp -r /sus/obfuscated.sus /dist

docker build -t monitoring-bun:latest -f Dockerfile.bun .
docker run --rm -it -v ./dist:/dist monitoring-bun:latest cp -r /monitoring/monitoring /dist
