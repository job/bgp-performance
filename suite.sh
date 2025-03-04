#!/bin/sh

set -ev

./bgperf2.py update gobgp
./bgperf2.py update bird

for i in 88 87 86; do
        ./bgperf2.py update openbgp$i &
done

./bgperf2.py batch -c big-tests.yaml
