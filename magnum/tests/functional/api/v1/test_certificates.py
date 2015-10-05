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
from tempest_lib import exceptions
import testtools

from magnum.tests.functional.api.v1.clients import bay_client as bay_cli
from magnum.tests.functional.api.v1.clients import baymodel_client as bm_cli
from magnum.tests.functional.api.v1.clients import cert_client as cert_cli
from magnum.tests.functional.common import base
from magnum.tests.functional.common import datagen


class CertificateTest(base.BaseMagnumTest):

    """Tests for certificate calls."""

    baymodel = None
    invalid_baymodel = None
    tls_disabled_baymodel = None
    bay = None
    invalid_bay = None
    tls_disabled_bay = None
    LOG = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        super(CertificateTest, self).__init__(*args, **kwargs)

    def setUp(self):
        super(CertificateTest, self).setUp()

    @classmethod
    def setUpClass(cls):
        super(CertificateTest, cls).setUpClass()
        model = datagen.valid_swarm_baymodel()
        _, cls.baymodel = cls._create_baymodel(model, user='default')
        model = datagen.valid_swarm_baymodel(tls_disabled=True)
        _, cls.tls_disabled_baymodel = cls._create_baymodel(model, user='default')
        model = datagen.invalid_swarm_baymodel()
        _, cls.invalid_baymodel = cls._create_baymodel(model, user='default')
        bay_model = datagen.valid_bay_data(
            baymodel_id=CertificateTest.baymodel.uuid)
        _, cls.bay = cls._create_bay(bay_model, user='default')
        bay_model = datagen.valid_bay_data(
            baymodel_id=CertificateTest.tls_disabled_baymodel.uuid)
        _, cls.tls_disabled_bay = cls._create_bay(bay_model, user='default')
        bay_model = datagen.bay_data(
            baymodel_id=CertificateTest.invalid_baymodel.uuid)
        _, cls.invalid_bay = cls._create_bay(bay_model, user='default')

    def tearDown(self):
        super(CertificateTest, self).tearDown()

    @classmethod
    def tearDownClass(cls):
        super(CertificateTest, cls).tearDownClass()
        cls.LOG.info("bay id: %s" % cls.bay.uuid)
        cls.LOG.info("baymodel id: %s" % cls.baymodel.uuid)
        cls._delete_bay(cls.bay.uuid, 'default')
        cls._delete_baymodel(cls.baymodel.uuid, 'default')
        cls._delete_bay(cls.tls_disabled_bay.uuid, 'default')
        cls._delete_baymodel(cls.tls_disabled_baymodel.uuid, 'default')
        cls._delete_bay(cls.invalid_bay.uuid, 'default')
        cls._delete_baymodel(cls.invalid_baymodel.uuid, 'default')

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

    @classmethod
    def _create_bay(cls, bay_model, user='default'):
        resp, model = bay_cli.BayClient.as_user(user).post_bay(bay_model)
        try:
            bay_cli.BayClient.as_user('default').wait_for_created_bay(model.uuid)
        finally:
            return resp, model

    @classmethod
    def _delete_bay(cls, bay_id, user='default'):
        resp, model = bay_cli.BayClient.as_user(user).delete_bay(bay_id)
        bay_cli.BayClient.as_user('default').wait_for_bay_to_delete(bay_id)
        return resp, model

    @testtools.testcase.attr('positive')
    def test_show_ca(self):
        resp, model = cert_cli.CertClient.as_user('default').get_cert(CertificateTest.bay.uuid)
        self.LOG.info("cert resp: %s" % resp)
        self.LOG.info("cert model: %s" % model)
        self.assertEqual(resp.status, 200)
        self.assertEqual(model.bay_uuid, CertificateTest.bay.uuid)
        self.assertIsNotNone(model.pem)
        self.assertIn('-----BEGIN CERTIFICATE-----', model.pem)
        self.assertIn('-----END CERTIFICATE-----', model.pem)

    @testtools.testcase.attr('negative')
    def test_show_ca_for_invalid_bay(self):
        cert_client = cert_cli.CertClient.as_user('default')
        self.assertRaises(
            exceptions.NotFound,
            cert_client.get_cert, 'fooo')

    @testtools.testcase.attr('negative')
    def test_show_ca_for_failed_bay(self):
        # I expected this to return a 400 but instead this is blocked on client
        # and works for the api
        _, model = bay_cli.BayClient.as_user('default').get_bay(CertificateTest.invalid_bay.uuid)
        self.assertEqual(model.status, 'CREATE_FAILED')
        
        cert_client = cert_cli.CertClient.as_user('default')
        resp, model = cert_client.get_cert(CertificateTest.invalid_bay.uuid)
        self.assertEqual(resp.status, 200)
        self.assertEqual(model.bay_uuid, CertificateTest.invalid_bay.uuid)
        self.assertIsNotNone(model.pem)
        self.assertIn('-----BEGIN CERTIFICATE-----', model.pem)
        self.assertIn('-----END CERTIFICATE-----', model.pem)

    @testtools.testcase.attr('negative')
    def test_show_ca_for_in_progress_bay(self):
        # I expected this to return a 400 but instead this is blocked on client
        # and works for the api
        bay_data = datagen.valid_bay_data(
            baymodel_id=CertificateTest.baymodel.uuid)
        resp, bay = bay_cli.BayClient.as_user('default').post_bay(bay_data)
        cert_client = cert_cli.CertClient.as_user('default')
        resp, model = cert_client.get_cert(bay.uuid)
        self.assertEqual(resp.status, 200)
        self.assertEqual(model.bay_uuid, bay.uuid)
        self.assertIsNotNone(model.pem)
        self.assertIn('-----BEGIN CERTIFICATE-----', model.pem)
        self.assertIn('-----END CERTIFICATE-----', model.pem)
        try:
            bay_cli.BayClient.as_user('default').wait_for_final_state(bay.uuid)
        finally:
            CertificateTest._delete_bay(bay.uuid)

    @testtools.testcase.attr('negative')
    def test_show_ca_for_tls_disabled_bay(self):
        # I expected this to return a 400 but instead this is blocked on client
        # and works for the api
        _, model = bay_cli.BayClient.as_user('default').get_bay(CertificateTest.tls_disabled_bay.uuid)
        self.assertEqual(model.status, 'CREATE_COMPLETE')
        
        cert_client = cert_cli.CertClient.as_user('default')
        resp, model = cert_client.get_cert(CertificateTest.tls_disabled_bay.uuid)
        self.assertEqual(resp.status, 200)
        self.assertEqual(model.bay_uuid, CertificateTest.tls_disabled_bay.uuid)
        self.assertIsNotNone(model.pem)
        self.assertIn('-----BEGIN CERTIFICATE-----', model.pem)
        self.assertIn('-----END CERTIFICATE-----', model.pem)

    @testtools.testcase.attr('positive')
    def test_sign_ca(self):
        model = datagen.cert_data(bay_uuid=CertificateTest.bay.uuid, csr_data='default.csr')
        resp, model = cert_cli.CertClient.as_user('default').post_cert(model)
        self.LOG.info("cert resp: %s" % resp)
        self.LOG.info("cert model: %s" % model)
        self.assertEqual(resp.status, 201)
        self.assertEqual(model.bay_uuid, CertificateTest.bay.uuid)
        self.assertIsNotNone(model.pem)
        self.assertIn('-----BEGIN CERTIFICATE-----', model.pem)
        self.assertIn('-----END CERTIFICATE-----', model.pem)

    @testtools.testcase.attr('negative')
    def test_sign_invalid_ca(self):
        model = datagen.cert_data(bay_uuid=CertificateTest.bay.uuid, csr_data='invalid.csr')
        cert_client = cert_cli.CertClient.as_user('default')
        self.assertRaises(
            exceptions.ServerFault,
            cert_client.post_cert, model)

    @testtools.testcase.attr('negative')
    def test_sign_nonexisting_ca(self):
        model = datagen.cert_data(bay_uuid=CertificateTest.bay.uuid)
        cert_client = cert_cli.CertClient.as_user('default')
        self.assertRaises(
            exceptions.ServerFault,
            cert_client.post_cert, model)

    @testtools.testcase.attr('negative')
    def test_sign_ca_for_invalid_bay(self):
        model = datagen.cert_data(bay_uuid='foo', csr_data='default.csr')
        cert_client = cert_cli.CertClient.as_user('default')
        self.assertRaises(
            exceptions.BadRequest,
            cert_client.post_cert, model)

    @testtools.testcase.attr('negative')
    def test_sign_ca_for_failed_bay(self):
        # I expected this to return a 400 but instead this is blocked on client
        # and works for the api
        model = datagen.cert_data(bay_uuid=CertificateTest.invalid_bay.uuid, csr_data='default.csr')
        resp, model = cert_cli.CertClient.as_user('default').post_cert(model)
        self.LOG.info("cert resp: %s" % resp)
        self.LOG.info("cert model: %s" % model)
        self.assertEqual(resp.status, 201)
        self.assertEqual(model.bay_uuid, CertificateTest.invalid_bay.uuid)
        self.assertIsNotNone(model.pem)
        self.assertIn('-----BEGIN CERTIFICATE-----', model.pem)
        self.assertIn('-----END CERTIFICATE-----', model.pem)

    @testtools.testcase.attr('negative')
    def test_sign_ca_for_in_progress_bay(self):
        # I expected this to return a 400 but instead this is blocked on client
        # and works for the api
        bay_data = datagen.valid_bay_data(
            baymodel_id=CertificateTest.baymodel.uuid)
        resp, bay = bay_cli.BayClient.as_user('default').post_bay(bay_data)
        model = datagen.cert_data(bay_uuid=bay.uuid, csr_data='default.csr')
        resp, model = cert_cli.CertClient.as_user('default').post_cert(model)
        self.assertEqual(resp.status, 201)
        self.assertEqual(model.bay_uuid, bay.uuid)
        self.assertIsNotNone(model.pem)
        self.assertIn('-----BEGIN CERTIFICATE-----', model.pem)
        self.assertIn('-----END CERTIFICATE-----', model.pem)
        try:
            bay_cli.BayClient.as_user('default').wait_for_final_state(bay.uuid)
        finally:
            CertificateTest._delete_bay(bay.uuid)

    @testtools.testcase.attr('negative')
    def test_sign_ca_for_tls_disabled_bay(self):
        # I expected this to return a 400 but instead this is blocked on client
        # and works for the api
        _, model = bay_cli.BayClient.as_user('default').get_bay(CertificateTest.tls_disabled_bay.uuid)
        print model
        self.assertEqual(model.status, 'CREATE_COMPLETE')
        
        cert_client = cert_cli.CertClient.as_user('default')
        model = datagen.cert_data(bay_uuid=CertificateTest.tls_disabled_bay.uuid, csr_data='default.csr')
        resp, model = cert_cli.CertClient.as_user('default').post_cert(model)
        self.assertEqual(resp.status, 201)
        self.assertEqual(model.bay_uuid, CertificateTest.tls_disabled_bay.uuid)
        self.assertIsNotNone(model.pem)
        self.assertIn('-----BEGIN CERTIFICATE-----', model.pem)
        self.assertIn('-----END CERTIFICATE-----', model.pem)
