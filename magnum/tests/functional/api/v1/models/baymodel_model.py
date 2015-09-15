# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
# Author: Endre Karlson <endre.karlson@hp.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from magnum.tests.functional.common.models import BaseModel


class BayModelModel(BaseModel):

    def __init__(self, acl_ref=None, read=None):
        super(BayModelModel, self).__init__()
        # figure out which values are needed here
        self.uuid='27e3153e-d5bf-4b7e-b517-fb518e17f34c'
        self.name='example'
        self.image_id='Fedora-k8s'
        self.flavor_id='m1.small'
        self.master_flavor_id='m1.small'
        self.dns_nameserver='8.8.1.1'
        self.keypair_id='keypair1'
        self.external_network_id='ffc44e4a-2319-4062-bce0-9ae1c38b05ba'
        self.fixed_network='private'
        self.apiserver_port=8080
        self.docker_volume_size=25
        self.cluster_distro='fedora-atomic'
        self.ssh_authorized_key='ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAB'
        self.coe='kubernetes'
        self.http_proxy='http://proxy.com:123'
        self.https_proxy='https://proxy.com:123'
        self.no_proxy='192.168.0.1,192.168.0.2,192.168.0.3'
        
class BayModelListModel(BaseModel):

    def __init__(self, acl_ref=None, read=None):
        super(BayModelListModel, self).__init__()
        # figure out which values are needed here
        self.acl_ref = acl_ref
        self.read = read
