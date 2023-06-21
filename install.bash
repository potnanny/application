#!/bin/bash

#
# Install Potnanny application onto Raspberry Pi.
# This should be run as user 'pi', or another admin/superuser account.
#
# version 1.0  02/2023
#

echo "Installing requirements..."
sudo apt update -y
sudo apt install build-essential libffi-dev libssl-dev python3-dev python3-pip sqlite3 git -y
# curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

echo "Creating groups..."
sudo groupadd -f potnanny


echo "Creating directories..."
mkdir $HOME/potnanny
mkdir $HOME/potnanny/plugins


echo "Cloning plugin repository..."
cd $HOME/potnanny/plugins
git clone https://github.com/potnanny/base-plugins.git


echo "Installing application..."
sudo pip3 install potnanny


# create local secret key
cat $HOME/.profile | grep "POTNANNY_SECRET"
if [ $? -ne 0 ]
then
    echo "export POTNANNY_SECRET=`LC_ALL=C tr -dc A-Za-z0-9 </dev/urandom | head -c 24`" >> $HOME/.profile
fi

# install cron, to ensure service runs at startup
crontab -l | grep potnanny
if [ $? -eq 0 ]
then
    (crontab -l; echo '@reboot * * * * source $HOME/.profile; potnanny start 2>&1') | crontab
fi

echo "Finishing setup and then reboot! Please be patient..."
echo ""
echo "(In 5 minutes, open your web browser and enter the url:"
echo "http://potnanny.localhost/ to access the application interface)"
echo ""
echo "Initial login/password is set to 'potnanny/growgreen!'"

sudo systemctl enable ssh
sudo usermod -G potnanny -a $USER
sudo usermod -G bluetooth -a $USER
sudo reboot now
