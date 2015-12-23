#!/bin/sh

echo "start time for remove-docker-key: `date`" >> /var/log/swarm.log
echo "removing docker key"
rm -f /etc/docker/key.json
echo "stop time for remove-docker-key: `date`" >> /var/log/swarm.log
