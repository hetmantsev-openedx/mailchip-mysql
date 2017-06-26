read -s -p "Enter password: " PASSWD

echo $PASSWD | sudo -S apt-get update
sudo apt-get -y install python-pip  &&  
sudo pip install sqlsoup requests mailchimp3 pyyaml trafaret trafaret-config
exit 1

echo "All packages are installed."

#test
