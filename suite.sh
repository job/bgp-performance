#!/bin/sh

./bgperf2.py update gobgp
./bgperf2.py update bird
mkdir -p bird
./bgperf2.py bench -t bird -n 1000 -o bird/output
mv -v *.png bird/

for i in 8.6 8.5 8.4 8.3 8.2 8.1 8.0 7.9 7.8 7.7 7.6 7.5 7.4 7.3 7.2 7.1; do
        mkdir -p $i
	y=$(echo $i | sed "s/\.//")
        ./bgperf2.py update openbgp$y
        ./bgperf2.py bench -t openbgp$y -n 1000 -o $i/output
        mv -v *.png $i/
done

./bgperf2.py batch -c big-tests.yaml
