# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
# Author: Endre Karlson <endre.karlson@hp.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from functional.api.v1.models.baymodel_model import BayModelModel
from functional.api.v1.models.baymodel_model import BayModelListModel
from functional.common.client import ClientMixin


class BayModelClient(ClientMixin):

    @classmethod
    def baymodels_uri(cls, filters=None):
        url = "/v1/baymodels"
        if filters:
            url = cls.add_filters(url, filters)
        return url

    @classmethod
    def baymodel_uri(cls, baymodel_id):
        return "{0}/{1}".format(cls.baymodels_uri(), baymodel_id)

    def list_baymodels(self, filters=None, **kwargs):
        resp, body = self.client.get(self.baymodels_uri(filters), **kwargs)
        return self.deserialize(resp, body, BayModelListModel)

    def get_baymodel(self, baymodel_id, **kwargs):
        resp, body = self.client.get(self.baymodel_uri(baymodel_id))
        return self.deserialize(resp, body, BayModelModel)

    def post_baymodel(self, baymodel_model, **kwargs):
        resp, body = self.client.post(
            self.baymodels_uri(),
            body=baymodel_model.to_json(), **kwargs)
        return self.deserialize(resp, body, BayModelModel)

    def patch_baymodel(self, baymodel_id, baymodel_model, **kwargs):
        resp, body = self.client.patch(
            self.baymodel_uri(baymodel_id),
            body=baymodel_model.to_json(), **kwargs)
        return self.deserialize(resp, body, BayModelModel)

    def delete_baymodel(self, baymodel_id, **kwargs):
        return self.client.delete(self.baymodel_uri(baymodel_id), **kwargs)