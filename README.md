# MNSF_Dashboard_Updated

This repository is used for the backend of the MNSF_Dashboard. This dashboard uses multiple source including exchange apis, and direct calls to block chains to gather data. The **Monitor.py** file along with other **.py** files in that directory are used to aggregate and calculate new tables and values which are pushed to a file for permiated storage.
This repo also contains all the running html, css, js and php files used to display the information on simple tables on web pages.

- Page_URL: http://<host address>/html/index.html
- On_Server_Path: /var/www/html
- Test Server URL: http://<host address>/html/index.html

# Important info
ON SERVER IF YOU GET STUCK AND CANT SEE TRACEBACK OR FIND WHERE AN ERROR IS PRINTING FROM JUST IMPORT THE SCRIPT BELOW AT THE TOP OF ANY PYTHON FILE AND IT WILL PRINT THE LOCATION EACH PRINT IS FROM
```
import sys
sys.path.append("/var/www/html")
import force_print_location.py
```

This uses the brython packages to run effectivly however they exceed the file size limit for gitlabs and I am not storing them here, please navigate to this link to find the files: https://github.com/ab7317/RUNNING_BRYTHON/upload

once you have the files please plce them into the following directory on the server
```
/var/www/html/htmldependencies
```

# AWS Information
- Account: 
- Instance_ID: 
- Instance_Name: MNSF_Dashboard
- Instance_IP: 
- Instance_Type: t3.xLarge

# SSH details
- Key_Name: 
- Host_Name: 
- Port: 22
- User_Name: ubuntu

# Restarting
- The server runs on services and cron jobs so you can safley restart the server from the aws console displayed above
- After restarting the instance, ssh into the server
- This run a bigger dashboard and as such uses multiple services
- To restart all the services run the following commands
```
cd /var/www/html/utils
sudo ./service.sh start
```
- If the services dont start then you'll need some more advnaced troubleshooting

# Error with mongo
- If the mongo server is running
- and can connect via compass but still getting connection error
- first check if the tunnel can manually open
```
ssh -i /path/to/private_key -L 27018:localhost:27017 ubuntu@<Server B IP>
```
- if this fails check if any process are on the tunnel port, in this case port 27018
```
netstat -tuln
```
- If you see anything on the tunnel port run this command to get its PID
```
sudo ss -tuln | grep 27018
```
- Then to kill the process run
```
sudo kill -9 [PID]
```
- Now check if the tunnel code and mongo connections are working

## Server setup
- First installed **Apache** for the web server
```
sudo apt-get update
sudo apt-get install apache2
sudo systemctl start apache2
sudo systemctl enable apache2
```
- Next I installed **PHP**
```
sudo apt install php8.1 php8.1-fpm
```
- Finally I installed **pip**
```
sudo apt install python3-pip
```
## Python setup
- The server should have python setup you can check with the below command
```
python3 --version
```
- If for some reason it is not installed run
```
sudo apt install python3
```
- Then we need to install poetry to quickly install all required packages
```
sudo apt install python3-poetry
```
- Once poetry is installed navigate to the following directory and run the command
```
cd /var/www/html
```
- Make sure the file **pyproject.toml** is present before running the below command
```
sudo poetry install
```

