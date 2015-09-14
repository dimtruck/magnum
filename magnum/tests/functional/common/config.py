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

from oslo_config import cfg

cfg.CONF.register_group(cfg.OptGroup(
    name='auth', title="Configuration for Keystone auth"
))

cfg.CONF.register_group(cfg.OptGroup(
    name='noauth', title="Configuration to run tests without Keystone"
))

cfg.CONF.register_opts([
    cfg.StrOpt('magnum_url',
               help="Use this instead of the endpoint in the service catalog"),

    cfg.StrOpt('auth_url', help="The Keystone v2 endpoint"),
    cfg.StrOpt('auth_v3_url', help="The Keystone v3 endpoint"),
    cfg.StrOpt('auth_version', default='v3'),
    cfg.StrOpt('region', default='RegionOne'),

    cfg.StrOpt('username'),
    cfg.StrOpt('tenant_name'),
    cfg.StrOpt('password', secret=True),
    cfg.StrOpt('domain_name'),

    cfg.StrOpt('alt_username'),
    cfg.StrOpt('alt_tenant_name'),
    cfg.StrOpt('alt_password', secret=True),
    cfg.StrOpt('alt_domain_name'),
], group='auth')

cfg.CONF.register_opts([
    cfg.StrOpt('user'),
    cfg.StrOpt('tenant'),
    cfg.StrOpt('pass', secret=True),
], group='admin')

cfg.CONF.register_opts([
    cfg.StrOpt('magnum_endpoint', help="The Magnum API endpoint"),
    cfg.StrOpt('tenant_id', default='noauth-project'),
    cfg.StrOpt('alt_tenant_id', default='alt-project'),
    cfg.StrOpt('admin_tenant_id', default='admin-project'),
    cfg.BoolOpt('use_noauth', default=False),
], group='noauth')


def find_config_file():
    return os.environ.get(
        'TEMPEST_CONFIG', 'functional_creds.conf')


def read_config():
    cfg.CONF(args=[], default_config_files=[find_config_file()])
