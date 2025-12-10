#!/bin/bash

set -ev

apt update
apt upgrade --yes
apt install docker.io --yes
apt install python3-pip --yes
apt install sysstat --yes

pip3 install --break-system-packages --root-user-action=ignore -r pip-requirements.txt

/sbin/shutdown now -r
