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

from magnum.tests.functional.api.v1.models import bay_model
from magnum.tests.functional.common import client
from magnum.tests.functional.common import utils


class BayClient(client.ClientMixin):
    """Encapsulates REST calls and maps JSON to/from models"""

    @classmethod
    def bays_uri(cls, filters=None):
        """Construct bays uri with optional filters

        :param filters: Optional k:v dict that's converted to url query
        :returns: url string
        """

        url = "/bays"
        if filters:
            url = cls.add_filters(url, filters)
        return url

    @classmethod
    def bay_uri(cls, bay_id):
        """Construct bay uri

        :param bay_id: bay uuid or name
        :returns: url string
        """

        return "{0}/{1}".format(cls.bays_uri(), bay_id)

    def list_bays(self, filters=None, **kwargs):
        """Makes GET /bays request and returns BayCollection

        Abstracts REST call to return all bays

        :param filters: Optional k:v dict that's converted to url query
        :returns: response object and BayCollection object
        """

        resp, body = self.client.get(self.bays_uri(filters), **kwargs)
        return self.deserialize(resp, body, bay_model.BayCollection)

    def get_bay(self, bay_id, **kwargs):
        """Makes GET /bay request and returns BayEntity

        Abstracts REST call to return a single bay based on uuid or name

        :param bay_id: bay uuid or name
        :returns: response object and BayCollection object
        """

        resp, body = self.client.get(self.bay_uri(bay_id))
        return self.deserialize(resp, body, bay_model.BayEntity)

    def post_bay(self, model, **kwargs):
        """Makes POST /bay request and returns BayEntity

        Abstracts REST call to create new bay

        :param model: BayEntity
        :returns: response object and BayEntity object
        """

        resp, body = self.client.post(
            self.bays_uri(),
            body=model.to_json(), **kwargs)
        return self.deserialize(resp, body, bay_model.BayEntity)

    def patch_bay(self, bay_id, baypatch_listmodel, **kwargs):
        """Makes PATCH /bay request and returns BayEntity

        Abstracts REST call to update bay attributes

        :param bay_id: UUID of bay
        :param baypatch_listmodel: BayPatchCollection
        :returns: response object and BayEntity object
        """

        resp, body = self.client.patch(
            self.bay_uri(bay_id),
            body=baypatch_listmodel.to_json(), **kwargs)
        return self.deserialize(resp, body, bay_model.BayEntity)

    def delete_bay(self, bay_id, **kwargs):
        """Makes DELETE /bay request and returns response object

        Abstracts REST call to delete bay based on uuid or name

        :param bay_id: UUID or name of bay
        :returns: response object
        """

        return self.client.delete(self.bay_uri(bay_id), **kwargs)

    def wait_for_bay_to_delete(self, bay_id):
        utils.wait_for_condition(
            lambda: self.does_bay_not_exist(bay_id), 1, 1800)

    def wait_for_created_bay(self, bay_id):
        try:
            utils.wait_for_condition(
                lambda: self.does_bay_exist(bay_id), 1, 1800)
        except Exception:
            # In error state.  Clean up the bay id
            self.delete_bay(bay_id)
            self.wait_for_bay_to_delete(bay_id)
            raise

    def does_bay_exist(self, bay_id):
        try:
            resp, model = self.get_bay(bay_id)
            if model.status in ['CREATED', 'CREATE_COMPLETE']:
                return True
            elif model.status in ['ERROR', 'CREATE_FAILED']:
                raise exceptions.ServerFault(
                    "Got into an error condition: %s for %s" %
                    (model.status, bay_id))
            else:
                return False
        except exceptions.NotFound:
            return False

    def does_bay_not_exist(self, bay_id):
        try:
            self.get_bay(bay_id)
        except exceptions.NotFound:
            return True
        return False
