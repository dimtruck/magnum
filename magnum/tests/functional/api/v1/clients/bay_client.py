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

from functional.api.v1.models.bay_model import BayModel
from functional.api.v1.models.bay_model import BayListModel
from functional.common.client import ClientMixin


class BayClient(ClientMixin):

    @classmethod
    def bays_uri(cls, filters=None):
        url = "/v1/bays"
        if filters:
            url = cls.add_filters(url, filters)
        return url

    @classmethod
    def bay_uri(cls, bay_id):
        return "{0}/{1}".format(cls.bays_uri(), bay_id)

    def list_bays(self, filters=None, **kwargs):
        resp, body = self.client.get(self.bays_uri(filters), **kwargs)
        return self.deserialize(resp, body, BayListModel)

    def get_bay(self, bay_id, **kwargs):
        resp, body = self.client.get(self.bay_uri(bay_id))
        return self.deserialize(resp, body, BayModel)

    def post_bay(self, bay_model, **kwargs):
        resp, body = self.client.post(
            self.bays_uri(),
            body=bay_model.to_json(), **kwargs)
        return self.deserialize(resp, body, BayModel)

    def patch_bay(self, bay_id, bay_model, **kwargs):
        resp, body = self.client.patch(
            self.bay_uri(bay_id),
            body=bay_model.to_json(), **kwargs)
        return self.deserialize(resp, body, BayModel)

    def delete_bay(self, bay_id, **kwargs):
        return self.client.delete(self.bay_uri(bay_id), **kwargs)