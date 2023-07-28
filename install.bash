#!/bin/bash

#
# Install Potnanny application onto Raspberry Pi.
# This should be run as user 'pi', or another admin/superuser account.
#
# PATIENCE!
# There are a lot of additional packages, and things that need to be compiled.
# The python cryptography package in particular, takes a very long time.
# On an original 1st gen Raspberry Pi Zero W this may take 2 HOURS, or more.

# version 1.0  02/2023
#

echo ""
echo "=============================="
echo "POTNANNY INSTALLER        v1.0"
echo "=============================="
echo ""

echo "Installing requirements..."
echo "------------------------------"
sudo apt-get update -y
sudo apt-get install build-essential libssl-dev python3-dev python3-pip python3-venv sqlite3 git ufw nginx -y
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
sudo pip3 install --upgrade pip


echo "Creating groups..."
echo "------------------------------"
sudo groupadd -f potnanny
sudo usermod -G potnanny -a $USER
sudo usermod -G bluetooth -a $USER


echo "Creating virtualenv..."
echo "------------------------------"
cd $HOME
python3 -m venv venv


echo "Creating user directories..."
echo "------------------------------"
mkdir $HOME/potnanny


echo "Cloning plugin repository..."
echo "------------------------------"
cd $HOME/potnanny
git clone https://github.com/potnanny/plugins.git


echo "Installing application..."
echo "------------------------------"
bash -c "source '$HOME/.cargo/env'; source $HOME/venv/bin/activate; pip3 install potnanny;"


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
    (crontab -l; echo '@reboot * * * * source $HOME/.profile; source $HOME/venv/bin/activate; potnanny start 2>&1') | crontab
fi


echo "Generating self-signed certificate for the web server..."
echo "------------------------------"
sudo mkdir /etc/ssl/potnanny
sudo chmod 750 /etc/ssl/potnanny
sudo chgrp potnanny /etc/ssl/potnanny

sudo openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout /etc/ssl/potnanny/private.key -out /etc/ssl/potnanny/certificate.crt

sudo chgrp potnanny /etc/ssl/potnanny/private.key
sudo chmod 640 /etc/ssl/potnanny/private.key


echo "Configuring firewall..."
echo "------------------------------"
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 8080
sudo ufw allow 443
sudo ufw allow 8443
sudo ufw enable


echo "Configuring NGINX proxy..."
echo "------------------------------"
printf "user www-data;\nworker_processes auto;\npid /run/nginx.pid;\ninclude /etc/nginx/modules-enabled/*.conf;\n\nevents {\n\tworker_connections 768;\n}\n\nhttp {\n\tserver {\n\t\tlisten 80\tdefault;\n\t\treturn 301\thttps://\$host\$request_uri;\n\t}\n\n\tserver {\n\t\tlisten\t443 ssl default_server;\n\t\tlisten\t[::]:443 ssl default_server;\n\t\tserver_name\tpotnanny;\n\t\tclient_max_body_size\t200M;\n\t\tssl_certificate\t\t/etc/ssl/potnanny/certificate.crt;\n\t\tssl_certificate_key\t\t/etc/ssl/potnanny/private.key;\n\t\tlocation / {\n\t\t\tproxy_pass\t\thttp://potnanny:8443;\n\t\t\tproxy_set_header\t\tHost \$host;\n\t\t}\n\t}\n}\n" | sudo tee /etc/nginx/nginx.conf >/dev/null
sudo service nginx restart


echo "Finishing setup and then reboot! Please be patient..."
echo ""
echo "(In 5 minutes, open your web browser and enter the url:"
echo "https://potnanny.localhost/ to access the application interface)"
echo ""
echo "Initial login/password is set to 'admin/potnanny!'"

sudo reboot now
