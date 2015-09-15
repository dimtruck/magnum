"""
Copyright 2015 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import uuid
import random

from magnum.tests.functional.api.v1.models.baymodel_model import BayModelModel
from magnum.tests.functional.api.v1.models.baymodelpatch_model import BayModelPatchListModel


def random_uuid():
    return uuid.uuid4()


def random_string(prefix='rand', n=8, suffix=''):
    """Return a string containing random digits

    :param prefix: the exact text to start the string. Defaults to "rand"
    :param n: the number of random digits to generate
    :param suffix: the exact text to end the string
    """
    digits = "".join(str(random.randrange(0, 10)) for _ in range(n))
    return prefix + digits + suffix


def random_baymodel_data(keypair_id=random_string(), image_id=random_string()):
    data = {
        "name": random_string(),
        "image_id": image_id,
        "flavor_id": random_string(),
        "master_flavor_id": random_string(),
        "dns_nameserver": "8.8.1.1",
        "keypair_id": keypair_id,
        "external_network_id": str(random_uuid()),
        "fixed_network": "private",
        "apiserver_port": 8080,
        "docker_volume_size": 25,
        "cluster_distro": random_string(),
        "ssh_authorized_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAB",
        "coe": "kubernetes",
        "http_proxy": "http://proxy.com:123",
        "https_proxy": "https://proxy.com:123",
        "no_proxy": "192.168.0.1,192.168.0.2,192.168.0.3"
    }
    model = BayModelModel.from_dict(data)

    print "return baymodelmodel %s " % model
    return model


def random_baymodel_patch_data(name=random_string()):
    data = [{
        "path": "/name",
        "value": name,
        "op": "replace"
    }]
    return BayModelPatchListModel.from_dict(data)
