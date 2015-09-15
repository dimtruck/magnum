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

import abc

from config import cfg
from noauth import NoAuthAuthProvider
from six import string_types
from six.moves.urllib.parse import quote_plus
from tempest_lib.common.rest_client import RestClient
from tempest_lib.auth import KeystoneV2Credentials
from tempest_lib.auth import KeystoneV2AuthProvider

from magnum.tests.functional.common.utils import memoized
import magnum.tests.functional.common.config


class KeystoneV2AuthProviderWithOverridableUrl(KeystoneV2AuthProvider):

    def base_url(self, *args, **kwargs):
        # use the base url from the config if it was specified
        if Config.magnum_url:
            return Config.magnum_url
        else:
            return super(KeystoneV2AuthProviderWithOverridableUrl, self) \
                .base_url(*args, **kwargs)


class BaseMagnumClient(RestClient):

    def __init__(self):
        super(BaseMagnumClient, self).__init__(
            auth_provider=self.get_auth_provider(),
            service='magnum',
            region=Config.auth.region
        )

    def get_auth_provider(self):
        if Config.noauth.use_noauth:
            return self._get_noauth_auth_provider()
        return self._get_keystone_auth_provider()

    @abc.abstractmethod
    def _get_noauth_auth_provider(self):
        pass

    @abc.abstractmethod
    def _get_keystone_auth_provider(self):
        pass

    def _create_keystone_auth_provider(self, creds):
        auth_provider = KeystoneV2AuthProviderWithOverridableUrl(
            creds, Config.auth.auth_url)
        auth_provider.fill_credentials()
        return auth_provider


class MagnumClient(BaseMagnumClient):
    """Client with default user"""

    def _get_noauth_auth_provider(self):
        creds = KeystoneV2Credentials(
            tenant_id=Config.noauth.tenant_id,
        )
        return NoAuthAuthProvider(creds, Config.noauth.magnum_endpoint)

    def _get_keystone_auth_provider(self):
        creds = KeystoneV2Credentials(
            username=Config.auth.username,
            password=Config.auth.password,
            tenant_name=Config.auth.tenant_name,
        )
        return self._create_keystone_auth_provider(creds)


class MagnumAltClient(BaseMagnumClient):
    """Client with alternate user"""

    def _get_noauth_auth_provider(self):
        creds = KeystoneV2Credentials(
            tenant_id=Config.noauth.alt_tenant_id,
        )
        return NoAuthAuthProvider(creds, Config.noauth.magnum_endpoint)

    def _get_keystone_auth_provider(self):
        creds = KeystoneV2Credentials(
            username=Config.auth.alt_username,
            password=Config.auth.alt_password,
            tenant_name=Config.auth.alt_tenant_name,
        )
        return self._create_keystone_auth_provider(creds)


class MagnumAdminClient(BaseMagnumClient):
    """Client with admin user"""

    def _get_noauth_auth_provider(self):
        creds = KeystoneV2Credentials(
            tenant_id=Config.noauth.tenant_id,
        )
        return NoAuthAuthProvider(creds, Config.noauth.magnum_endpoint)

    def _get_keystone_auth_provider(self):
        creds = KeystoneV2Credentials(
            username=Config.admin.user,
            password=Config.admin['pass'],
            tenant_name=Config.admin.tenant,
        )
        return self._create_keystone_auth_provider(creds)


class ClientMixin(object):

    @classmethod
    @memoized
    def get_clients(cls):
        return {
            'default': MagnumClient(),
            'alt': MagnumAltClient(),
            'admin': MagnumAdminClient(),
        }

    def __init__(self, client):
        self.client = client

    @classmethod
    def deserialize(cls, resp, body, model_type):
        return resp, model_type.from_json(body)

    @classmethod
    def as_user(cls, user):
        """
        :param user: 'default', 'alt', or 'admin'
        """
        return cls(cls.get_clients()[user])

    @property
    def tenant_id(self):
        return self.client.tenant_id

    @classmethod
    def add_filters(cls, url, filters):
        """
        :param url: base URL for the request
        :param filters: dict with var:val pairs to add as parameters to URL
        """
        first = True
        for f in filters:
            if isinstance(filters[f], string_types):
                filters[f] = quote_plus(filters[f].encode('utf-8'))

            url = '{url}{sep}{var}={val}'.format(
                url=url, sep=('?' if first else '&'), var=f, val=filters[f]
            )
            first = False
        return url
