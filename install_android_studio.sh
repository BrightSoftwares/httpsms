#!/bin/bash
set -e
# export DEBIAN_FRONTEND=noninteractive
#androidstudio_download_url = "https://redirector.gvt1.com/edgedl/android/studio/ide-zips/2024.2.1.10/android-studio-2024.2.1.10-linux.tar.gz"


echo "Checking current architecture = it should be amd64"
sudo dpkg --print-architecture 

echo "Checking foreign architecture = you shouldn't see anything"
sudo dpkg --print-foreign-architectures 

echo "Add the 32bit architecture"
sudo dpkg --add-architecture i386

echo "Checking foreign architecture - now you should see the i386 in the list"
sudo dpkg --print-foreign-architectures 


sudo apt-get update -y && sudo apt-get install libc6:i386 libncurses5:i386 libstdc++6:i386 lib32z1 libbz2-1.0:i386 -y

wget "https://redirector.gvt1.com/edgedl/android/studio/ide-zips/2024.2.1.10/android-studio-2024.2.1.10-linux.tar.gz" # $androidstudio_download_url
tar xvfz android-studio-2024.2.1.10-linux.tar.gz
bash android-studio/bin/studio