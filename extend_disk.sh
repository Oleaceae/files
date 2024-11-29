# extend /var
sudo mv /var /var_old
sudo mkdir /var
sudo /usr/local/etc/emulab/mkextrafs.pl /var
sudo rsync -aHAXP /var_old/*  /var

# extend /tmp
sudo rm -rf /tmp
sudo mkdir /var/my_tmp
sudo chmod 777 /var/my_tmp
sudo ln -s /var/my_tmp /tmp
