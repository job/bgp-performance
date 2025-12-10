#!/bin/bash

echo 16384 | sudo tee /proc/sys/net/ipv4/neigh/default/gc_thresh3
sudo swapoff -a

for i in openbgp90 openbgp89 openbgp88 openbgp87 bird bird3 gobgp; do
	python3 bgperf2.py update $i
done
