#cloud-boothook
#!/bin/sh

setenforce 0
touch /var/log/swarm.log
echo "start time for disable-selenix: `date`" >> /var/log/swarm.log

sed -i '
  /^SELINUX=/ s/=.*/=permissive/
' /etc/selinux/config
echo "stop time for disable-selenix: `date`" >> /var/log/swarm.log
