#!/bin/bash

sudo apt update
sudo apt upgrade --yes
sudo apt install docker.io --yes
sudo apt install python3-pip --yes

pip3 install --break-system-packages -r pip-requirements.txt

sudo /sbin/shutdown now -r
