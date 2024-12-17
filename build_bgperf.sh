#!/bin/bash

echo 16384 | sudo tee /proc/sys/net/ipv4/neigh/default/gc_thresh3
sudo swapoff -a

for i in openbgp87 openbgp86 bird gobgp; do
	python3 bgperf2.py update $i &
done
