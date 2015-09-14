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

from tempest_lib import exceptions

from functional.api.v2.clients.quotas_client import QuotasClient
from functional.api.v2.models.quotas_model import QuotasModel
from functional.common.base import BaseMagnumTest


class MagnumV1Test(BaseMagnumTest):

    def __init__(self, *args, **kwargs):
        super(MagnumV1Test, self).__init__(*args, **kwargs)

    def _assert_invalid_uuid(self, method, *args, **kw):
        """
        Test that UUIDs used in the URL is valid.
        """
        self._assert_exception(
            exceptions.BadRequest, 'invalid_uuid', 400, method, *args)

    def _assert_exception(self, exc, type_, status, method, *args, **kwargs):
        """
        Checks the response that a api call with a exception contains the
        wanted data.
        """
        try:
            method(*args, **kwargs)
        except exc as e:
            self.assertEqual(status, e.resp_body['code'])
            self.assertEqual(type_, e.resp_body['type'])