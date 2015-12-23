#!/bin/sh
echo "start time for enabling services: `date`" >> /var/log/swarm.log

echo "starting services"
systemctl daemon-reload
for service in $NODE_SERVICES; do
    echo "activating service $service"
    systemctl enable $service
    systemctl --no-block start $service
done
echo "stop time for enabling services: `date`" >> /var/log/swarm.log
