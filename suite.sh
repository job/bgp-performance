#!/bin/sh

set -ev

./bgperf2.py update gobgp
./bgperf2.py update bird
./bgperf2.py update bird3

for i in dev 89 88 87; do
        ./bgperf2.py update openbgp$i &
done

./bgperf2.py batch -c big-tests.yaml
