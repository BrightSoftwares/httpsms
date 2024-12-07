#!/bin/bash
set -e
export DEBIAN_FRONTEND=noninteractive

# Upgrade the distribution
echo "Upgrading the operating system"
sudo apt-get update -y && sudo apt-get dist-upgrade -y
sudo DEBIAN_FRONTEND=noninteractive apt-get install xfce4 xfce4-goodies novnc python3-websockify python3-numpy tightvncserver htop nano neofetch -y

echo "Creating the vnc startup file"

echo "Configure the vnc server. Forward to /dev/null so that mv fail silently"
if [ -f /home/codespace/.vnc/xstartup ]; then
    echo "File xstartup found! Renaming"
    mv /home/codespace/.vnc/xstartup /home/codespace/.vnc/xstartup.bak.install
else
    echo "File xstartup does not exist. No renaming"
fi

echo "Creating the vnc startup file"
mkdir -p /home/codespace/.vnc/
cat > /home/codespace/.vnc/xstartup << EOF
#!/bin/bash
xrdb $HOME/.Xresources
startxfce4 &
EOF

sudo chmod +x /home/codespace/.vnc/xstartup