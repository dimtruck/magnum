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
import testtools
from tempest_lib import exceptions

from magnum.tests.functional.common import datagen
from magnum.tests.functional.api.base import MagnumV1Test
from magnum.tests.functional.api.v1.clients.baymodel_client import BayModelClient


class BayModelTest(MagnumV1Test):
    
    def __init__(self, *args, **kwargs):
        super(BayModelTest, self).__init__(*args, **kwargs)
        self.uuid_to_delete = None

    def setUp(self):
        super(BayModelTest, self).setUp()

    def tearDown(self):
        super(BayModelTest, self).tearDown()
        if self.uuid_to_delete is not None:
            self._delete_baymodel(self.uuid_to_delete)
            self.uuid_to_delete = None

    def _create_baymodel(self, baymodel_model, user='admin'):
        resp, model = BayModelClient.as_user(user).post_baymodel(
            baymodel_model)
        self.assertEqual(resp.status, 201)
        return resp, model

    def _delete_baymodel(self, baymodel_id, user='admin'):
        resp, model = BayModelClient.as_user(user).delete_baymodel(
            baymodel_id)
        self.assertEqual(resp.status, 204)
        return resp, model

    @testtools.testcase.attr('positive')
    def test_list_baymodels(self):
        temp_resp, temp_model = self._create_baymodel(datagen.random_baymodel_data(keypair_id='default', image_id='146a074c-5833-4b1b-924c-c9d0a25e094e'))
        self.uuid_to_delete = temp_model.uuid
        resp, model = BayModelClient.as_user('admin').list_baymodels()
        self.assertEqual(resp.status, 200)
        self.assertGreater(len(model.baymodels), 0)

    @testtools.testcase.attr('positive')
    def test_create_baymodel(self):
        client = BayModelClient.as_user('admin')
        temp_model = datagen.random_baymodel_data(image_id='146a074c-5833-4b1b-924c-c9d0a25e094e', keypair_id='default')
        resp, model = self._create_baymodel(temp_model, user='admin')
        self.uuid_to_delete = model.uuid

    @testtools.testcase.attr('positive')
    def test_update_baymodel(self):
        # get json object
        post_model = datagen.random_baymodel_data(image_id='146a074c-5833-4b1b-924c-c9d0a25e094e', keypair_id='default')
        resp, old_model = self._create_baymodel(post_model)
        self.uuid_to_delete = old_model.uuid

        patch_model = datagen.random_baymodel_patch_data()
        resp, new_model = BayModelClient.as_user('admin').patch_baymodel(
            old_model.uuid, patch_model)
        self.assertEqual(resp.status, 200)

        resp, model = BayModelClient.as_user('admin').get_baymodel(
            new_model.uuid)
        self.assertEqual(resp.status, 200)
        self.assertEqual(new_model.uuid, old_model.uuid)
        self.assertEqual(new_model.name, model.name)

    @testtools.testcase.attr('positive')
    def test_delete_baymodel(self):
        temp_model = datagen.random_baymodel_data(image_id='146a074c-5833-4b1b-924c-c9d0a25e094e', keypair_id='default')
        resp, model = self._create_baymodel(temp_model)
        resp, model = BayModelClient.as_user('admin').delete_baymodel(
            model.uuid)
        self.assertEqual(resp.status, 204)

    @testtools.testcase.attr('negative')
    def test_get_baymodel_404(self):
        client = BayModelClient.as_user('admin')
        random_uuid = str(uuid.uuid4())
        self._assert_exception(
            exceptions.NotFound,
            "Baymodel %s could not be found." % random_uuid,
            404, client.get_baymodel,
            random_uuid)

    @testtools.testcase.attr('negative')
    def test_update_baymodel_404(self):
        patch_model = datagen.random_baymodel_patch_data()

        client = BayModelClient.as_user('admin')
        random_uuid = str(uuid.uuid4())
        self._assert_exception(
            exceptions.NotFound,
            "Baymodel %s could not be found." % random_uuid,
            404, client.patch_baymodel,
            random_uuid, patch_model)

    @testtools.testcase.attr('negative')
    def test_delete_baymodel_404(self):
        client = BayModelClient.as_user('admin')
        random_uuid = str(uuid.uuid4())
        self._assert_exception(
            exceptions.NotFound,
            "Baymodel %s could not be found." % random_uuid,
            404,
            client.delete_baymodel,
            random_uuid)

    @testtools.testcase.attr('negative')
    def test_get_baymodel_invalid_uuid(self):
        client = BayModelClient.as_user('admin')
        self._assert_exception(
            exceptions.NotFound,
            "Baymodel fooo could not be found.",
            404,
            client.get_baymodel,
            'fooo')

    @testtools.testcase.attr('negative')
    def test_update_baymodel_invalid_uuid(self):
        patch_model = datagen.random_baymodel_patch_data()

        client = BayModelClient.as_user('admin')
        self._assert_invalid_uuid(client.patch_baymodel, 'fooo', patch_model)

    @testtools.testcase.attr('negative')
    def test_delete_baymodel_invalid_uuid(self):
        client = BayModelClient.as_user('admin')
        self._assert_exception(
            exceptions.NotFound,
            "Baymodel fooo could not be found.",
            404,
            client.get_baymodel,
            'fooo')

    @testtools.testcase.attr('negative')
    def test_create_baymodel_missing_image(self):
        client = BayModelClient.as_user('admin')
        model = datagen.random_baymodel_data(keypair_id='default')
        self._assert_exception(
            exceptions.NotFound,
            "The images resource %s could not be found." % model.image_id,
            404,
            client.post_baymodel,
            model)

    @testtools.testcase.attr('negative')
    def test_create_baymodel_missing_keypair(self):
        client = BayModelClient.as_user('admin')
        model = datagen.random_baymodel_data(image_id='146a074c-5833-4b1b-924c-c9d0a25e094e')
        self._assert_exception(
            exceptions.NotFound,
            "Unable to find keypair %s." % model.keypair_id,
            404,
            client.post_baymodel,
            model)

    @testtools.testcase.attr('negative')
    def test_update_baymodel_invalid_patch(self):
        # get json object
        post_model = datagen.random_baymodel_data(image_id='146a074c-5833-4b1b-924c-c9d0a25e094e', keypair_id='default')
        resp, old_model = self._create_baymodel(post_model)
        self.uuid_to_delete = old_model.uuid
        
        client = BayModelClient.as_user('admin')
        self._assert_exception(
            exceptions.BadRequest,
            'Invalid input for field/attribute patch',
            400,
            client.patch_baymodel,
            str(uuid.uuid4()), post_model)

