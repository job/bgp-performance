#!/bin/sh

set -ev

./bgperf2.py update gobgp
./bgperf2.py update bird

for i in 86 85 84 83 82 81 80 79 78 77 76 75 74 73 72 71; do
        ./bgperf2.py update openbgp$i &
done

./bgperf2.py batch -c big-tests.yaml
