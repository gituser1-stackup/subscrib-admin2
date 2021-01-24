#!/bin/bash
clear
cd /usr/local/SuscribBckApp  #After that go to your project directory
echo "Starting Backend Server  $(date)." >> /var/log/inventory_logs.txt
/usr/bin/python3 manage.py runserver 0.0.0.0:8000  & #run django server#!/bin/bash
clear
cd /var/www/SusbscribAppNewVersion  #After that go to your project directory
echo "Starting Frontend Server  $(date)." >> /var/log/inventory_logs.txt
npm start  & #run django server