# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
test_magnum
----------------------------------

Tests for `magnum` module baymodel and bay crud.
"""

import uuid

from tempest_lib import exceptions

from magnum.tests.functional.common import datagen
from magnum.tests.functional.api.base import MagnumV1Test
from magnum.tests.functional.api.v1.clients.baymodel_client import BayModelClient


class BayModelTest(MagnumV1Test):
    def _create_baymodel(self, baymodel_model, user='admin'):
        resp, model = BayModelClient.as_user(user).post_baymodel(
            baymodel_model)
        self.assertEqual(resp.status, 201)
        return resp, model

    def test_list_baymodels(self):
        self._create_baymodel(datagen.random_baymodel_data())
        resp, model = BayModelClient.as_user('admin').list_baymodels()
        self.assertEqual(resp.status, 200)
        self.assertGreater(len(model.baymodels), 0)

    def test_create_baymodel(self):
        self._create_baymodel(datagen.random_baymodel_data(), user='admin')

    def test_update_baymodel(self):
        post_model = datagen.random_baymodel_data()
        resp, old_model = self._create_baymodel(post_model)

        patch_model = datagen.random_baymodel_data()
        resp, new_model = BayModelClient.as_user('admin').patch_baymodel(
            old_model.id, patch_model)
        self.assertEqual(resp.status, 200)

        resp, model = BayModelClient.as_user('admin').get_baymodel(
            new_model.id)
        self.assertEqual(resp.status, 200)
        self.assertEqual(new_model.id, old_model.id)
        self.assertEqual(new_model.pattern, model.pattern)

    def test_delete_baymodel(self):
        resp, model = self._create_baymodel(datagen.random_baymodel_data())
        resp, model = BayModelClient.as_user('admin').delete_baymodel(
            model.id)
        self.assertEqual(resp.status, 204)

    def test_get_baymodel_404(self):
        client = BayModelClient.as_user('admin')
        self._assert_exception(
            exceptions.NotFound,
            'baymodel_not_found',
            404, client.get_baymodel,
            str(uuid.uuid4()))

    def test_update_baymodel_404(self):
        model = datagen.random_baymodel_data()

        client = BayModelClient.as_user('admin')
        self._assert_exception(
            exceptions.NotFound,
            'baymodel_not_found',
            404,
            client.patch_baymodel,
            str(uuid.uuid4()), model)

    def test_delete_baymodel_404(self):
        client = BayModelClient.as_user('admin')
        self._assert_exception(
            exceptions.NotFound,
            'baymodel_not_found',
            404,
            client.delete_baymodel,
            str(uuid.uuid4()))

    def test_get_baymodel_invalid_uuid(self):
        client = BayModelClient.as_user('admin')
        self._assert_invalid_uuid(client.get_baymodel, 'fooo')

    def test_update_baymodel_invalid_uuid(self):
        model = datagen.random_baymodel_data()

        client = BayModelClient.as_user('admin')
        self._assert_invalid_uuid(client.patch_baymodel, 'fooo', model)

    def test_delete_baymodel_invalid_uuid(self):
        client = BayModelClient.as_user('admin')
        self._assert_invalid_uuid(client.get_baymodel, 'fooo')
