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

import os

import ConfigParser

class Config(object):
    
    @classmethod
    def setUp(cls):
        config = ConfigParser.RawConfigParser()
        if config.read('functional_creds.conf'):
            # the OR pattern means the environment is preferred for
            # override
            cls.admin_user = config.get('admin', 'user')
            cls.admin_passwd = config.get('admin', 'pass')
            cls.admin_tenant = config.get('admin', 'tenant')

            cls.user = config.get('auth', 'username')
            cls.passwd = config.get('auth', 'password')
            cls.tenant = config.get('auth', 'tenant_name')
            cls.domain_name = config.get('auth', 'domain_name')
            cls.auth_url = config.get('auth', 'auth_url')
            cls.auth_v3_url = config.get('auth', 'auth_v3_url')
            cls.magnum_url = config.get('auth', 'magnum_url')
            cls.auth_version = config.get('auth', 'auth_version')
            cls.region = config.get('auth', 'region')
            
            cls.image_id = config.get('magnum', 'image_id')
            cls.nic_id = config.get('magnum', 'nic_id')

            cls.use_noauth = config.get('noauth', 'use_noauth')
            cls.tenant_id = config.get('noauth', 'tenant_id')
            cls.admin_tenant = config.get('noauth', 'admin_tenant_id')
            cls.magnum_endpoint = config.get('noauth', 'magnum_endpoint')
