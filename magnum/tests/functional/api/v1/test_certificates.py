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

import fixtures

from oslo_log import log as logging
from tempest_lib import exceptions
import testtools

from magnum.tests.functional.common import base
from magnum.tests.functional.common import datagen


class CertificateTest(base.BaseMagnumTest):

    """Tests for certificate calls."""

    baymodel = None
    bay = None
    credentials = None
    baymodel_client = None
    bay_client = None
    LOG = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        super(CertificateTest, self).__init__(*args, **kwargs)
        self.cert_client = None

    def setUp(self):
        super(CertificateTest, self).setUp()
        (self.cert_client, _) = self.get_clients_with_existing_creds(
            creds=CertificateTest.credentials,
            type_of_creds='default',
            request_type='cert')

    @classmethod
    def setUpClass(cls):
        try:
            super(CertificateTest, cls).setUpClass()
            cls.credentials = cls.get_credentials(
                type_of_creds='default',
                class_cleanup=True)
            (cls.baymodel_client, _) = cls.get_clients_with_existing_creds(
                creds=cls.credentials,
                type_of_creds='default',
                request_type='baymodel')
            (cls.bay_client, _) = cls.get_clients_with_existing_creds(
                creds=cls.credentials,
                type_of_creds='default',
                request_type='bay')
            baymodel_model = datagen.valid_swarm_baymodel()
            _, cls.baymodel = cls._create_baymodel(baymodel_model)
            bay_model = datagen.valid_bay_data(
                baymodel_id=CertificateTest.baymodel.uuid)
            _, cls.bay = cls._create_bay(bay_model)

            # NOTE (dimtruck) by default tempest sets timeout to 20 mins.
            # We need more time.
            test_timeout = 3600
            cls.useFixture(fixtures.Timeout(test_timeout, gentle=True))
        except Exception:
            cls.tearDownClass()
            raise

    def tearDown(self):
        super(CertificateTest, self).tearDown()

    @classmethod
    def tearDownClass(cls):
        try:
            cls._delete_bay(cls.bay.uuid)
            cls._delete_baymodel(cls.baymodel.uuid)
        finally:
            super(CertificateTest, cls).tearDownClass()

    @classmethod
    def _create_baymodel(cls, baymodel_model):
        resp, model = cls.baymodel_client.post_baymodel(
            baymodel_model)
        return resp, model

    @classmethod
    def _delete_baymodel(cls, baymodel_id):
        resp, model = cls.baymodel_client.delete_baymodel(
            baymodel_id)
        return resp, model

    @classmethod
    def _create_bay(cls, bay_model):
        resp, model = cls.bay_client.post_bay(bay_model)
        cls.bay_client.wait_for_created_bay(
            model.uuid)
        return resp, model

    @classmethod
    def _delete_bay(cls, bay_id):
        resp, model = cls.bay_client.delete_bay(bay_id)
        cls.bay_client.wait_for_bay_to_delete(bay_id)
        return resp, model

    @testtools.testcase.attr('positive')
    def test_show_ca(self):
        resp, model = self.cert_client.get_cert(
            CertificateTest.bay.uuid)
        self.LOG.info("cert resp: %s" % resp)
        self.LOG.info("cert model: %s" % model)
        self.assertEqual(resp.status, 200)
        self.assertEqual(model.bay_uuid, CertificateTest.bay.uuid)
        self.assertIsNotNone(model.pem)
        self.assertIn('-----BEGIN CERTIFICATE-----', model.pem)
        self.assertIn('-----END CERTIFICATE-----', model.pem)

    @testtools.testcase.attr('positive')
    def test_sign_ca(self):
        model = datagen.cert_data(bay_uuid=CertificateTest.bay.uuid)
        resp, model = self.cert_client.post_cert(model)
        self.LOG.info("cert resp: %s" % resp)
        self.LOG.info("cert model: %s" % model)
        self.assertEqual(resp.status, 201)
        self.assertEqual(model.bay_uuid, CertificateTest.bay.uuid)
        self.assertIsNotNone(model.pem)
        self.assertIn('-----BEGIN CERTIFICATE-----', model.pem)
        self.assertIn('-----END CERTIFICATE-----', model.pem)

    @testtools.testcase.attr('negative')
    def test_sign_ca_no_cert(self):
        model = datagen.cert_data(bay_uuid=CertificateTest.bay.uuid,
                                  cert_data=None)
        self.assertRaises(
            exceptions.ServerFault,
            self.cert_client.post_cert,
            model)
