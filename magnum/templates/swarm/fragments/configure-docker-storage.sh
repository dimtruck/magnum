#!/bin/sh
echo "start time for configure-docker-storage: `date`" >> /var/log/swarm.log

. /etc/sysconfig/heat-params
echo "sourced heat-params: `date`" >> /var/log/swarm.log

attempts=60
while [ ${attempts} -gt 0 ]; do
    device_name=$(ls /dev/disk/by-id | grep ${DOCKER_VOLUME:0:20}$)
    if [ -n "${device_name}" ]; then
        break
    fi
    echo "waiting for disk device"
    sleep 0.5
    udevadm trigger
    let attempts--
done
echo "added disk device: `date`" >> /var/log/swarm.log


if [ -z "${device_name}" ]; then
    echo "ERROR: disk device does not exist" >&2
    exit 1
fi

device_path=/dev/disk/by-id/${device_name}
pvcreate ${device_path}
echo "pvcreated ${device_path}: `date`" >> /var/log/swarm.log
vgcreate docker ${device_path}
echo "vgcreated docker ${device_path}: `date`" >> /var/log/swarm.log

cat > /etc/sysconfig/docker-storage-setup << EOF
VG=docker
EOF

sed -i '/^DOCKER_STORAGE_OPTIONS=/ s/=.*/=--storage-driver devicemapper --storage-opt dm.fs=xfs --storage-opt dm.thinpooldev=\/dev\/mapper\/docker-docker--pool --storage-opt dm.use_deferred_removal=true/' /etc/sysconfig/docker-storage
echo "stop time for configure-docker-storage: `date`" >> /var/log/swarm.log
