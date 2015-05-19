# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from hamcrest import assert_that, none

from xivo_dao.alchemy.func_key_dest_service import FuncKeyDestService as FuncKeyDestServiceSchema
from xivo_dao.alchemy.func_key_dest_conference import FuncKeyDestConference as FuncKeyDestConferenceSchema
from xivo_dao.alchemy.func_key_dest_forward import FuncKeyDestForward as FuncKeyDestForwardSchema
from xivo_dao.alchemy.func_key_dest_group import FuncKeyDestGroup as FuncKeyDestGroupSchema
from xivo_dao.alchemy.func_key_dest_queue import FuncKeyDestQueue as FuncKeyDestQueueSchema
from xivo_dao.alchemy.func_key_dest_user import FuncKeyDestUser as FuncKeyDestUserSchema
from xivo_dao.alchemy.func_key_dest_agent import FuncKeyDestAgent as FuncKeyDestAgentSchema
from xivo_dao.alchemy.func_key_dest_custom import FuncKeyDestCustom as FuncKeyDestCustomSchema
from xivo_dao.alchemy.func_key_dest_bsfilter import FuncKeyDestBSFilter as FuncKeyDestBSFilterSchema


class FuncKeyHelper(object):

    destination_types = {
        1: 'user',
        2: 'group',
        3: 'queue',
        4: 'conference',
        5: 'service',
        6: 'forward',
        7: 'park_position',
        8: 'features',
        9: 'paging',
        10: 'custom',
        11: 'agent',
        12: 'bsfilter',
    }

    destinations = {
        'user': (FuncKeyDestUserSchema, 'user_id', 1),
        'group': (FuncKeyDestGroupSchema, 'group_id', 2),
        'queue': (FuncKeyDestQueueSchema, 'queue_id', 3),
        'conference': (FuncKeyDestConferenceSchema, 'conference_id', 4),
        'service': (FuncKeyDestServiceSchema, 'extension_id', 5),
        'forward': (FuncKeyDestForwardSchema, 'extension_id', 6),
        'bsfilter': (FuncKeyDestBSFilterSchema, 'filtermember_id', 12),
    }

    def setup_funckeys(self):
        self.setup_types()
        self.setup_destination_types()

    def setup_types(self):
        row = self.add_func_key_type(id=1, name='speeddial')
        self.speeddial_id = row.id

    def setup_destination_types(self):
        for destination_id, name in self.destination_types.items():
            self.add_func_key_destination_type(id=destination_id,
                                               name=name)

    def add_extenfeatures(self, exten, typeval, commented=0):
        extension_row = self.add_extension(exten=exten,
                                           type='extenfeatures',
                                           context='xivo-features',
                                           typeval=typeval,
                                           commented=commented)
        return extension_row

    def add_user_destination(self, dest_id):
        return self._add_destination('user', dest_id)

    def add_group_destination(self, dest_id):
        return self._add_destination('group', dest_id)

    def add_queue_destination(self, dest_id):
        return self._add_destination('queue', dest_id)

    def add_conference_destination(self, dest_id):
        return self._add_destination('conference', dest_id)

    def add_service_destination(self, dest_id):
        return self._add_destination('service', dest_id)

    def add_forward_destination(self, extension_id, number=None):
        destination_type_id = 6
        func_key_row = self.create_func_key(destination_type_id)
        destination_row = FuncKeyDestForwardSchema(func_key_id=func_key_row.id,
                                                   extension_id=extension_id,
                                                   destination_type_id=destination_type_id,
                                                   number=number)
        self.add_me(destination_row)
        return destination_row

    def add_agent_destination(self, agent_id, extension_id):
        destination_type_id = 11
        func_key_row = self.create_func_key(destination_type_id)
        destination_row = FuncKeyDestAgentSchema(func_key_id=func_key_row.id,
                                                 destination_type_id=destination_type_id,
                                                 agent_id=agent_id,
                                                 extension_id=extension_id)
        self.add_me(destination_row)
        return destination_row

    def add_custom_destination(self, exten):
        destination_type_id = 10
        func_key_row = self.create_func_key(destination_type_id)
        destination_row = FuncKeyDestCustomSchema(func_key_id=func_key_row.id,
                                                  destination_type_id=destination_type_id,
                                                  exten=exten)
        self.add_me(destination_row)
        return destination_row

    def add_bsfilter_destination(self, filtermember_id):
        destination_type_id = 12
        func_key_row = self.create_func_key(destination_type_id)
        destination_row = FuncKeyDestBSFilterSchema(func_key_id=func_key_row.id,
                                                    destination_type_id=destination_type_id,
                                                    filtermember_id=filtermember_id)
        self.add_me(destination_row)
        return destination_row

    def create_func_key(self, dest_type_id):
        return self.add_func_key(type_id=self.speeddial_id,
                                 destination_type_id=dest_type_id)

    def create_forward_func_key(self, exten, fwd_type, number=None, commented=0):
        extension_row = self.add_extenfeatures(exten, fwd_type, commented=commented)
        return self.add_forward_destination(extension_row.id, number)

    def create_service_func_key(self, exten, service_type, commented=0):
        extension_row = self.add_extenfeatures(exten, service_type, commented=commented)
        return self.add_service_destination(extension_row.id)

    def create_user_func_key(self):
        user_row = self.add_user()
        return self.add_user_destination(user_row.id)

    def create_group_func_key(self):
        group_row = self.add_group()
        return self.add_group_destination(group_row.id)

    def create_queue_func_key(self):
        queue_row = self.add_queuefeatures()
        return self.add_queue_destination(queue_row.id)

    def create_conference_func_key(self):
        conference_row = self.add_meetmefeatures()
        return self.add_conference_destination(conference_row.id)

    def create_agent_func_key(self, exten, exten_action, commented=0):
        agent_row = self.add_agent()
        extension_row = self.add_extenfeatures(exten, exten_action, commented=commented)
        return self.add_agent_destination(agent_row.id, extension_row.id)

    def create_custom_func_key(self, exten):
        return self.add_custom_destination(exten)

    def create_bsfilter_func_key(self):
        user_row = self.add_user()
        bsfilter_row = self.add_bsfilter()
        filter_member_row = self.add_filter_member(bsfilter_row.id, user_row.id, 'secretary')
        return filter_member_row, self.add_bsfilter_destination(filter_member_row.id)

    def add_func_key_to_user(self, destination_row, user_row, position=1, blf=True):
        self.add_func_key_mapping(template_id=user_row.func_key_private_template_id,
                                  destination_type_id=destination_row.destination_type_id,
                                  func_key_id=destination_row.func_key_id,
                                  position=position,
                                  blf=blf)

    def find_destination(self, destination, destination_id):
        schema, column_name, _ = self.destinations[destination]
        column = getattr(schema, column_name)

        row = (self.session.query(schema)
               .filter(column == destination_id)
               .first())

        return row

    def assert_destination_deleted(self, destination, destination_id):
        row = self.find_destination(destination, destination_id)
        assert_that(row, none())

    def _add_destination(self, dest_type, dest_id):
        schema, column, destination_type_id = self.destinations[dest_type]

        func_key_row = self.create_func_key(destination_type_id)

        destination_row = schema(**{'func_key_id': func_key_row.id,
                                    column: dest_id})
        self.add_me(destination_row)

        return destination_row
