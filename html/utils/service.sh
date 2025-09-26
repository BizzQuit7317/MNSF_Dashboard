#!/bin/bash

# Function to start services
start_services() {
    echo "Starting services..."
    sudo systemctl start monitor.service
    sudo systemctl start fireBlocks.service
    sudo systemctl start check.service
    sudo systemctl start checkMonitor.service
    sudo systemctl start test.service
    echo "Services started."
}

# Function to stop services
stop_services() {
    echo "Stopping services..."
    sudo systemctl stop monitor.service
    sudo systemctl stop fireBlocks.service
    sudo systemctl stop check.service
    sudo systemctl stop checkMonitor.service
    sudo systemctl stop test.service
    echo "Services stopped."
}

# Function to status check services
check_services() {
    echo "Checking services..."
    sudo systemctl status monitor.service
    sudo systemctl status fireBlocks.service
    sudo systemctl status check.service
    sudo systemctl status checkMonitor.service
    sudo systemctl status test.service
    echo "Services checked."
}


# Check the script argument
if [ "$1" == "start" ]; then
    start_services
elif [ "$1" == "stop" ]; then
    stop_services
elif [ "$1" == "check" ]; then
    check_services
elif [ "$1" == "restart" ]; then
    stop_services
    start_services
else
    echo "Usage: $0 [start|stop]"
    exit 1
fi

exit 0

