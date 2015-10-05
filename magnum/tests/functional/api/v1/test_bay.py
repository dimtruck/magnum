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

from oslo_log import log as logging
from tempest_lib.common.utils import data_utils
from tempest_lib import decorators
from tempest_lib import exceptions
import testtools

from magnum.tests.functional.api.v1.clients import bay_client as bay_cli
from magnum.tests.functional.api.v1.clients import baymodel_client as bm_cli
from magnum.tests.functional.common import base
from magnum.tests.functional.common import datagen


class BayTest(base.BaseMagnumTest):

    """Tests for bay CRUD."""

    baymodel = None
    LOG = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        super(BayTest, self).__init__(*args, **kwargs)
        self.bays = []

    def setUp(self):
        super(BayTest, self).setUp()

    @classmethod
    def setUpClass(cls):
        super(BayTest, cls).setUpClass()
        model = datagen.valid_swarm_baymodel()
        _, cls.baymodel = cls._create_baymodel(model, user='default')

    def tearDown(self):
        super(BayTest, self).tearDown()
        bay_list = self.bays[:]
        for (bay_id, user) in bay_list:
            self._delete_bay(bay_id, user)
            self.bays.remove((bay_id, user))

    @classmethod
    def tearDownClass(cls):
        super(BayTest, cls).tearDownClass()
        cls._delete_baymodel(cls.baymodel.uuid, 'default')

    @classmethod
    def _create_baymodel(cls, baymodel_model, user='default'):
        resp, model = bm_cli.BayModelClient.as_user(user).post_baymodel(
            baymodel_model)
        return resp, model

    @classmethod
    def _delete_baymodel(cls, baymodel_id, user='default'):
        resp, model = bm_cli.BayModelClient.as_user(user).delete_baymodel(
            baymodel_id)
        return resp, model

    def _create_bay(self, bay_model, user='default'):
        resp, model = bay_cli.BayClient.as_user(user).post_bay(bay_model)
        self.LOG.info('Response: %s' % resp)
        self.LOG.info('Model: %s ' % model)
        self.assertEqual(resp.status, 201)
        self.assertIsNotNone(model.uuid)
        self.assertIsNone(model.status)
        self.assertIsNone(model.status_reason)
        self.assertEqual(model.baymodel_id, BayTest.baymodel.uuid)
        bay_cli.BayClient.as_user('default').wait_for_created_bay(model.uuid)
        self.bays.append((model.uuid, user))
        return resp, model

    def _create_invalid_bay(self, bay_model, user='default'):
        bay_client = bay_cli.BayClient.as_user(user)
        resp, model = bay_client.post_bay(bay_model)
        self.assertEqual(resp.status, 201)
        self.bays.append((model.uuid, user))
        self.assertRaises(
            exceptions.ServerFault,
            bay_client.wait_for_created_bay, model.uuid)

    def _delete_bay(self, bay_id, user='default'):
        resp, model = bay_cli.BayClient.as_user(user).delete_bay(bay_id)
        self.assertEqual(resp.status, 204)
        bay_cli.BayClient.as_user('default').wait_for_bay_to_delete(bay_id)
        return resp, model

    def _get_bay_by_id(self, bay_id, user='default'):
        resp, model = bay_cli.BayClient.as_user(user).get_bay(bay_id)
        self.assertEqual(resp.status, 404)
        return resp, model

    @testtools.testcase.attr('positive')
    def test_list_bays(self):
        gen_model = datagen.valid_bay_data(baymodel_id=BayTest.baymodel.uuid)
        _, temp_model = self._create_bay(gen_model, user='default')
        resp, model = bay_cli.BayClient.as_user('default').list_bays()
        self.assertEqual(resp.status, 200)
        self.assertGreater(len(model.bays), 0)
        self.assertIn(
            temp_model.uuid, list([x['uuid'] for x in model.bays]))

    @testtools.testcase.attr('negative')
    def test_create_bay_for_nonexisting_baymodel(self):
        gen_model = datagen.valid_bay_data(baymodel_id='this-does-not-exist')
        bay_client = bay_cli.BayClient.as_user('default')
        self.assertRaises(
            exceptions.BadRequest,
            bay_client.post_bay, gen_model)

    @testtools.testcase.attr('negative')
    def test_create_bay_with_node_count_0(self):
        gen_model = datagen.valid_bay_data(
            baymodel_id=BayTest.baymodel.uuid, node_count=0)
        bay_client = bay_cli.BayClient.as_user('default')
        self.assertRaises(
            exceptions.BadRequest,
            bay_client.post_bay, gen_model)

    @testtools.testcase.attr('negative')
    def test_create_bay_with_zero_masters(self):
        gen_model = datagen.valid_bay_data(baymodel_id=BayTest.baymodel.uuid,
                                           master_count=0)
        bay_client = bay_cli.BayClient.as_user('default')
        self.assertRaises(
            exceptions.BadRequest,
            bay_client.post_bay, gen_model)

    @testtools.testcase.attr('negative')
    def test_create_bay_with_missing_name(self):
        self.skipTest('This is currently an error! '
                      'Should throw a 400 instead of a 500')
        gen_model = datagen.valid_bay_data(baymodel_id=BayTest.baymodel.uuid,
                                           name=None)
        bay_client = bay_cli.BayClient.as_user('default')
        self.assertRaises(
            exceptions.BadRequest,
            bay_client.post_bay, gen_model)

    @testtools.testcase.attr('negative')
    def test_update_bay_name_for_existing_bay(self):
        first_model = datagen.valid_bay_data(baymodel_id=BayTest.baymodel.uuid,
                                             name='test')
        _, old_model = self._create_bay(first_model, user='default')

        patch_model = datagen.bay_name_patch_data()
        bay_client = bay_cli.BayClient.as_user('default')
        self.assertRaises(
            exceptions.BadRequest,
            bay_client.patch_bay,
            old_model.uuid, patch_model)

    @testtools.testcase.attr('negative')
    def test_update_bay_api_address_for_existing_bay(self):
        first_model = datagen.valid_bay_data(baymodel_id=BayTest.baymodel.uuid,
                                             name='test')
        _, old_model = self._create_bay(first_model, user='default')

        patch_model = datagen.bay_api_addy_patch_data()
        bay_client = bay_cli.BayClient.as_user('default')
        self.assertRaises(
            exceptions.BadRequest,
            bay_client.patch_bay,
            old_model.uuid, patch_model)

    @testtools.testcase.attr('negative')
    def test_update_bay_for_nonexisting_bay(self):
        patch_model = datagen.bay_name_patch_data()

        bay_client = bay_cli.BayClient.as_user('default')
        self.assertRaises(
            exceptions.NotFound,
            bay_client.patch_bay, 'fooo', patch_model)

    @testtools.testcase.attr('positive')
    @decorators.skip_because(bug="1528927")
    def test_update_bay_to_existing_name(self):
        first_model = datagen.valid_bay_data(baymodel_id=BayTest.baymodel.uuid,
                                             name='test')
        _, old_model = self._create_bay(first_model, user='default')

        sec_model = datagen.valid_bay_data(baymodel_id=BayTest.baymodel.uuid,
                                           name='test2')
        _, old2_model = self._create_bay(sec_model, user='default')

        patch_model = datagen.bay_name_patch_data(name=old_model.name)
        bay_client = bay_cli.BayClient.as_user('default')
        resp, new_model = bay_client.patch_bay(
            old2_model.uuid, patch_model)
        self.assertEqual(200, resp.status)
        self.assertNotEqual(old_model.uuid, old2_model.uuid)
        self.assertEqual(old2_model.uuid, new_model.uuid)
        self.assertEqual(old_model.name, new_model.name)

    @testtools.testcase.attr('positive')
    def test_delete_bay_for_existing_bay(self):
        first_model = datagen.valid_bay_data(baymodel_id=BayTest.baymodel.uuid,
                                             name='test')
        _, old_model = self._create_bay(first_model, user='default')
        self._delete_bay(old_model.uuid)
        self.bays.remove((old_model.uuid, 'default'))

    @testtools.testcase.attr('negative')
    def test_delete_bay_for_nonexisting_bay(self):
        bay_client = bay_cli.BayClient.as_user('default')
        self.assertRaises(
            exceptions.NotFound,
            bay_client.delete_bay, data_utils.rand_uuid())

    @testtools.testcase.attr('negative')
    def test_delete_bay_twice(self):
        first_model = datagen.valid_bay_data(baymodel_id=BayTest.baymodel.uuid,
                                             name='test')
        _, old_model = self._create_bay(first_model, user='default')
        bay_client = bay_cli.BayClient.as_user('default')
        self._delete_bay(old_model.uuid)
        self.bays.remove((old_model.uuid, 'default'))

        self.assertRaises(
            exceptions.NotFound,
            bay_client.delete_bay, old_model.uuid)

    @testtools.testcase.attr('positive')
    def test_get_existing_bay(self):
        first_model = datagen.valid_bay_data(baymodel_id=BayTest.baymodel.uuid,
                                             name='test')
        _, old_model = self._create_bay(first_model, user='default')
        resp, model = bay_cli.BayClient.as_user('default').get_bay(
            old_model.uuid)

        self.assertEqual(200, resp.status)
        self.assertIsNotNone(model.uuid)
        self.assertEqual(model.status, 'CREATE_COMPLETE')
        self.assertEqual(model.status_reason, 'Stack CREATE '
                                              'completed successfully')
        self.assertEqual(model.baymodel_id, BayTest.baymodel.uuid)
        self.assertGreater(model.node_count, 0)
        self.assertEqual(len(model.node_addresses), model.node_count)
        self.assertEqual(model.name, first_model.name)

    @testtools.testcase.attr('negative')
    def test_get_nonexisting_bay(self):
        bay_client = bay_cli.BayClient.as_user('default')
        self.assertRaises(
            exceptions.NotFound,
            bay_client.get_bay, 'fooo')
