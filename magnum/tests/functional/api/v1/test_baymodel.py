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


from tempest_lib import exceptions
import testtools

from magnum.tests.functional.common import base
from magnum.tests.functional.common import datagen


class BayModelTest(base.BaseMagnumTest):

    """Tests for baymodel CRUD."""

    def __init__(self, *args, **kwargs):
        super(BayModelTest, self).__init__(*args, **kwargs)
        self.baymodels = []
        self.baymodel_client = None
        self.keypairs_client = None

    def setUp(self):
        super(BayModelTest, self).setUp()
        (self.baymodel_client,
         self.keypairs_client) = self.get_clients_with_isolated_creds(
             type_of_creds='default',
             request_type='baymodel')

    def tearDown(self):
        super(BayModelTest, self).tearDown()
        for baymodel_id in self.baymodels:
            self._delete_baymodel(baymodel_id)
            self.baymodels.remove(baymodel_id)

    def _create_baymodel(self, baymodel_model):
        resp, model = self.baymodel_client.post_baymodel(baymodel_model)
        self.assertEqual(201, resp.status)
        self.baymodels.append(model.uuid)
        return resp, model

    def _delete_baymodel(self, baymodel_id):
        resp, model = self.baymodel_client.delete_baymodel(baymodel_id)
        self.assertEqual(204, resp.status)
        return resp, model

    @testtools.testcase.attr('positive')
    def test_list_baymodels(self):
        self.keypairs_client.create_keypair(name='default')
        gen_model = datagen.random_baymodel_data_w_valid_keypair_and_image_id()
        _, temp_model = self._create_baymodel(gen_model)
        resp, model = self.baymodel_client.list_baymodels()
        self.assertEqual(200, resp.status)
        self.assertGreater(len(model.baymodels), 0)
        self.assertIn(
            temp_model.uuid, list([x['uuid'] for x in model.baymodels]))

    @testtools.testcase.attr('positive')
    def test_create_baymodel(self):
        self.keypairs_client.create_keypair(name='default')
        gen_model = datagen.random_baymodel_data_w_valid_keypair_and_image_id()
        resp, model = self._create_baymodel(gen_model)

    @testtools.testcase.attr('positive')
    def test_update_baymodel_by_uuid(self):
        self.keypairs_client.create_keypair(name='default')
        gen_model = datagen.random_baymodel_data_w_valid_keypair_and_image_id()
        resp, old_model = self._create_baymodel(gen_model)

        patch_model = datagen.random_baymodel_name_patch_data()
        resp, new_model = self.baymodel_client.patch_baymodel(
            old_model.uuid, patch_model)
        self.assertEqual(200, resp.status)

        resp, model = self.baymodel_client.get_baymodel(new_model.uuid)
        self.assertEqual(200, resp.status)
        self.assertEqual(old_model.uuid, new_model.uuid)
        self.assertEqual(model.name, new_model.name)

    @testtools.testcase.attr('positive')
    def test_delete_baymodel_by_uuid(self):
        self.keypairs_client.create_keypair(name='default')
        gen_model = datagen.random_baymodel_data_w_valid_keypair_and_image_id()
        resp, model = self._create_baymodel(gen_model)
        resp, _ = self.baymodel_client.delete_baymodel(model.uuid)
        self.assertEqual(204, resp.status)
        self.baymodels.remove(model.uuid)

    @testtools.testcase.attr('positive')
    def test_delete_baymodel_by_name(self):
        self.keypairs_client.create_keypair(name='default')
        gen_model = datagen.random_baymodel_data_w_valid_keypair_and_image_id()
        resp, model = self._create_baymodel(gen_model)
        resp, _ = self.baymodel_client.delete_baymodel(model.name)
        self.assertEqual(204, resp.status)
        self.baymodels.remove(model.uuid)

    @testtools.testcase.attr('negative')
    def test_get_baymodel_by_uuid_404(self):
        self.assertRaises(
            exceptions.NotFound,
            self.baymodel_client.get_baymodel, datagen.random_uuid())

    @testtools.testcase.attr('negative')
    def test_update_baymodel_404(self):
        patch_model = datagen.random_baymodel_name_patch_data()

        self.assertRaises(
            exceptions.NotFound,
            self.baymodel_client.patch_baymodel,
            datagen.random_uuid(), patch_model)

    @testtools.testcase.attr('negative')
    def test_delete_baymodel_404(self):
        self.assertRaises(
            exceptions.NotFound,
            self.baymodel_client.delete_baymodel, datagen.random_uuid())

    @testtools.testcase.attr('negative')
    def test_get_baymodel_by_name_404(self):
        self.assertRaises(
            exceptions.NotFound,
            self.baymodel_client.get_baymodel, 'fooo')

    @testtools.testcase.attr('negative')
    def test_update_baymodel_name_not_found(self):
        patch_model = datagen.random_baymodel_name_patch_data()

        self.assertRaises(
            exceptions.NotFound,
            self.baymodel_client.patch_baymodel, 'fooo', patch_model)

    @testtools.testcase.attr('negative')
    def test_delete_baymodel_by_name_404(self):
        self.assertRaises(
            exceptions.NotFound,
            self.baymodel_client.get_baymodel, 'fooo')

    @testtools.testcase.attr('negative')
    def test_create_baymodel_missing_image(self):
        self.keypairs_client.create_keypair(name='default')
        gen_model = datagen.random_baymodel_data_w_valid_keypair()
        self.assertRaises(
            exceptions.NotFound,
            self.baymodel_client.post_baymodel, gen_model)

    @testtools.testcase.attr('negative')
    def test_create_baymodel_missing_keypair(self):
        gen_model = datagen.random_baymodel_data_w_valid_image_id()
        self.assertRaises(
            exceptions.NotFound,
            self.baymodel_client.post_baymodel, gen_model)

    @testtools.testcase.attr('negative')
    def test_update_baymodel_invalid_patch(self):
        # get json object
        self.keypairs_client.create_keypair(name='default')
        gen_model = datagen.random_baymodel_data_w_valid_keypair_and_image_id()
        resp, old_model = self._create_baymodel(gen_model)

        self.assertRaises(
            exceptions.BadRequest,
            self.baymodel_client.patch_baymodel, datagen.random_uuid(),
            gen_model)

    @testtools.testcase.attr('negative')
    def test_create_baymodel_invalid_network_driver(self):
        self.keypairs_client.create_keypair(name='default')
        gen_model = datagen.random_baymodel_data_w_valid_keypair_and_image_id()
        gen_model.network_driver = 'invalid_network_driver'
        self.assertRaises(
            exceptions.BadRequest,
            self.baymodel_client.post_baymodel, gen_model)
