#!/usr/bin/env bash
set -e
export DEBIAN_FRONTEND=noninteractive

echo "Running post create commands"

echo "Generating the ssl certificate"
openssl req -x509 -nodes -newkey rsa:3072 -keyout novnc.pem -out novnc.pem -days 3650 -subj "/C=US/ST=New Sweden/L=Stockholm/O=.../OU=.../CN=.../emailAddress=..."
echo "Done"

echo "Web socketifying"
websockify -D --web=/usr/share/novnc/ --cert=/home/ubuntu/novnc.pem 6080 localhost:5901
echo "Done"

echo "Starting vncserver"
export USER=codespace
vncserver
echo "Done"