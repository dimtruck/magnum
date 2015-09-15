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

import json

from magnum.tests.functional.common.models import BaseModel
from magnum.tests.functional.common.models import EntityModel
from magnum.tests.functional.common.models import CollectionModel

class BayModelPatchData(BaseModel):
    pass


class BayModelPatchModel(EntityModel):
    ENTITY_NAME = 'baymodelpatch'
    MODEL_TYPE = BayModelPatchData
        
class BayModelPatchListModel(CollectionModel):
    MODEL_TYPE = BayModelPatchData
    COLLECTION_NAME = 'baymodelpatchlist'

    def to_json(self):
        # get list from self.COLLECTION_NAME
        data = getattr(self, 'baymodelpatchlist')
        collection = []
        for d in data:
            collection.append(d.to_dict())
        return json.dumps(collection)

    @classmethod
    def from_dict(cls, data):

        # deserialize e.g. data['zones']
        model = cls()
        collection = []
        for d in data:
          collection.append(cls.MODEL_TYPE.from_dict(d))
        setattr(model, cls.COLLECTION_NAME, collection)
        return model
