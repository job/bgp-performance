#!/bin/sh

set -v

docker ps -q | xargs -r docker kill
docker ps -aq | xargs -r docker rm
docker image ls | awk ' {print $3 }' | grep -v IMAGE | xargs -r docker image rm
