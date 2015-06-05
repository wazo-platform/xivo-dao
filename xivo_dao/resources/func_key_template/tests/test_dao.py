# -*- coding: utf-8 -*-

# Copyright (C) 2014-2015 Avencall
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

from hamcrest import assert_that, is_not, none, has_property, equal_to, calling, raises
from mock import patch, ANY, Mock

from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.resources.func_key.tests.test_helpers import FuncKeyHelper
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.func_key_template import FuncKeyTemplate as FuncKeyTemplateSchema
from xivo_dao.alchemy.func_key_mapping import FuncKeyMapping as FuncKeyMappingSchema

from xivo_dao.helpers.exception import DataError
from xivo_dao.resources.func_key_template import dao
from xivo_dao.resources.func_key.model import UserFuncKey, FuncKeyTemplate, FuncKey, \
    UserDestination, QueueDestination, GroupDestination, ConferenceDestination, PagingDestination, \
    BSFilterDestination, CustomDestination, ServiceDestination, TransferDestination, ForwardDestination, \
    AgentDestination, ParkPositionDestination, ParkingDestination


class TestFuncKeyTemplateDao(DAOTestCase, FuncKeyHelper):

    def setUp(self):
        DAOTestCase.setUp(self)
        self.setup_types()
        self.setup_destination_types()

    def assert_template_empty(self, template_id):
        count = (self.session.query(FuncKeyMappingSchema)
                 .filter(FuncKeyMappingSchema.template_id == template_id)
                 .count())

        assert_that(count, equal_to(0))

    def create_user_func_key_for_template(self, template_row, position):
        destination_row = self.create_user_func_key()
        self.add_destination_to_template(destination_row, template_row, position)
        return UserFuncKey(id=destination_row.func_key_id)

    def prepare_template(self, destination_row=None, destination=None, name=None, position=1):
        template_row = self.add_func_key_template(name=name)

        template = FuncKeyTemplate(id=template_row.id,
                                   name=template_row.name)

        if destination_row and destination:
            self.add_destination_to_template(destination_row, template_row)
            template.keys = {position: FuncKey(id=destination_row.func_key_id,
                                               destination=destination)}

        return template


class TestFuncKeyTemplateCreate(DAOTestCase, FuncKeyHelper):

    def setUp(self):
        super(TestFuncKeyTemplateCreate, self).setUp()
        self.setup_types()
        self.setup_destination_types()
        self.destination_type_ids = {value: key
                                     for key, value in self.destination_types.iteritems()}

    def build_template_with_key(self, destination, position=1):
        return FuncKeyTemplate(name='foobar',
                               keys={position: FuncKey(destination=destination)})

    def assert_mapping_has_destination(self, destination_type, destination_row, position=1):
        mapping_row = (self.session.query(FuncKeyMappingSchema)
                       .filter(FuncKeyMappingSchema.func_key_id == destination_row.func_key_id)
                       .first())

        assert_that(mapping_row.position, equal_to(position))
        assert_that(mapping_row.func_key_id, equal_to(destination_row.func_key_id))

        destination_type_id = self.destination_type_ids[destination_type]
        assert_that(mapping_row.destination_type_id, equal_to(destination_type_id))

    def test_when_creating_a_template_then_template_row(self):
        template = FuncKeyTemplate(name='foobar')

        result = dao.create(template)

        template_row = self.session.query(FuncKeyTemplateSchema).first()

        assert_that(template_row.name, equal_to(template.name))
        assert_that(result.name, equal_to(template_row.name))
        assert_that(result.id, equal_to(template_row.id))

    def test_given_template_has_user_func_key_when_creating_then_creates_mapping(self):
        destination_row = self.create_user_func_key()
        template = self.build_template_with_key(UserDestination(user_id=destination_row.user_id))

        result = dao.create(template)

        self.assert_mapping_has_destination('user', destination_row)
        assert_that(result.keys[1].id, equal_to(destination_row.func_key_id))

    def test_given_template_has_group_func_key_when_creating_then_creates_mapping(self):
        destination_row = self.create_group_func_key()
        template = self.build_template_with_key(GroupDestination(group_id=destination_row.group_id))

        result = dao.create(template)

        self.assert_mapping_has_destination('group', destination_row)
        assert_that(result.keys[1].id, equal_to(destination_row.func_key_id))

    def test_given_template_has_queue_func_key_when_creating_then_creates_mapping(self):
        destination_row = self.create_queue_func_key()
        template = self.build_template_with_key(QueueDestination(queue_id=destination_row.queue_id))

        result = dao.create(template)

        self.assert_mapping_has_destination('queue', destination_row)
        assert_that(result.keys[1].id, equal_to(destination_row.func_key_id))

    def test_given_template_has_conference_func_key_when_creating_then_creates_mapping(self):
        destination_row = self.create_conference_func_key()
        template = self.build_template_with_key(ConferenceDestination(conference_id=destination_row.conference_id))

        result = dao.create(template)

        self.assert_mapping_has_destination('conference', destination_row)
        assert_that(result.keys[1].id, equal_to(destination_row.func_key_id))

    def test_given_template_has_paging_func_key_when_creating_then_creates_mapping(self):
        destination_row = self.create_paging_func_key()
        template = self.build_template_with_key(PagingDestination(paging_id=destination_row.paging_id))

        result = dao.create(template)

        self.assert_mapping_has_destination('paging', destination_row)
        assert_that(result.keys[1].id, equal_to(destination_row.func_key_id))

    def test_given_template_has_bsfilter_func_key_when_creating_then_creates_mapping(self):
        _, destination_row = self.create_bsfilter_func_key()
        template = self.build_template_with_key(BSFilterDestination(filter_member_id=destination_row.filtermember_id))

        result = dao.create(template)

        self.assert_mapping_has_destination('bsfilter', destination_row)
        assert_that(result.keys[1].id, equal_to(destination_row.func_key_id))

    def test_given_template_has_service_func_key_when_creating_then_creates_mapping(self):
        destination_row = self.create_service_func_key('*20', 'enablednd')
        template = self.build_template_with_key(ServiceDestination(service='enablednd'))

        result = dao.create(template)

        self.assert_mapping_has_destination('service', destination_row)
        assert_that(result.keys[1].id, equal_to(destination_row.func_key_id))

    def test_given_template_has_forward_func_key_when_creating_then_creates_mapping(self):
        extension_row = self.add_extenfeatures('*21', 'fwdbusy')

        template = self.build_template_with_key(ForwardDestination(forward='busy'))

        result = dao.create(template)

        destination_row = self.find_destination('forward', extension_row.id)
        assert_that(destination_row.number, none())

        self.assert_mapping_has_destination('forward', destination_row)
        assert_that(result.keys[1].id, equal_to(destination_row.func_key_id))

    def test_given_template_has_forward_func_key_with_exten_when_creating_then_creates_destination_with_number(self):
        extension_row = self.add_extenfeatures('*22', 'fwdrna')

        template = self.build_template_with_key(ForwardDestination(forward='noanswer',
                                                                   exten='1000'))

        result = dao.create(template)

        destination_row = self.find_destination('forward', extension_row.id)
        assert_that(destination_row.number, equal_to('1000'))
        assert_that(result.keys[1].id, equal_to(destination_row.func_key_id))

    def test_given_template_has_park_position_func_key_when_creating_then_creates_mapping(self):
        template = self.build_template_with_key(ParkPositionDestination(position=701))

        result = dao.create(template)

        destination_row = self.find_destination('park_position', '701')
        assert_that(destination_row.park_position, equal_to('701'))

        self.assert_mapping_has_destination('park_position', destination_row)
        assert_that(result.keys[1].id, equal_to(destination_row.func_key_id))

    def test_given_template_has_custom_func_key_when_creating_then_creates_mapping(self):
        template = self.build_template_with_key(CustomDestination(exten='1234'))

        result = dao.create(template)

        destination_row = self.find_destination('custom', '1234')
        assert_that(destination_row.exten, equal_to('1234'))

        self.assert_mapping_has_destination('custom', destination_row)
        assert_that(result.keys[1].id, equal_to(destination_row.func_key_id))

    def test_given_template_has_agent_func_key_when_creating_then_creates_mapping(self):
        destination_row = self.create_agent_func_key('_*31.', 'agentstaticlogin')

        template = self.build_template_with_key(AgentDestination(action='login',
                                                                 agent_id=destination_row.agent_id))

        result = dao.create(template)

        self.assert_mapping_has_destination('agent', destination_row)
        assert_that(result.keys[1].id, equal_to(destination_row.func_key_id))

    def test_given_template_has_transfer_func_key_when_creating_then_creates_mapping(self):
        destination_row = self.create_features_func_key('featuremap', 'blindxfer', '*1')

        template = self.build_template_with_key(TransferDestination(transfer='blind',
                                                                    exten='1000'))

        result = dao.create(template)

        self.assert_mapping_has_destination('features', destination_row)
        assert_that(result.keys[1].id, equal_to(destination_row.func_key_id))

    def test_given_template_has_parking_destination_when_creating_then_creates_mapping(self):
        destination_row = self.create_features_func_key('general', 'parkext', '700')

        template = self.build_template_with_key(ParkingDestination())

        result = dao.create(template)

        self.assert_mapping_has_destination('features', destination_row)
        assert_that(result.keys[1].id, equal_to(destination_row.func_key_id))


class TestFuncKeyTemplateGet(TestFuncKeyTemplateDao):

    def test_given_no_template_then_raises_error(self):
        assert_that(calling(dao.get).with_args(1),
                    raises(NotFoundError))

    def test_given_empty_template_when_getting_then_returns_empty_template(self):
        template_row = self.add_func_key_template(name='foobar')

        expected = FuncKeyTemplate(id=template_row.id, name='foobar')

        result = dao.get(template_row.id)

        assert_that(expected, equal_to(result))

    def test_given_template_has_user_func_key_when_getting_then_returns_user_func_key(self):
        destination_row = self.create_user_func_key()
        expected = self.prepare_template(destination_row,
                                         UserDestination(user_id=destination_row.user_id))

        result = dao.get(expected.id)

        assert_that(expected, equal_to(result))

    def test_given_template_has_queue_func_key_when_getting_then_returns_queue_func_key(self):
        destination_row = self.create_queue_func_key()
        expected = self.prepare_template(destination_row,
                                         QueueDestination(queue_id=destination_row.queue_id))

        result = dao.get(expected.id)

        assert_that(expected, equal_to(result))

    def test_given_template_has_group_func_key_when_getting_then_returns_group_func_key(self):
        destination_row = self.create_group_func_key()
        expected = self.prepare_template(destination_row,
                                         GroupDestination(group_id=destination_row.group_id))

        result = dao.get(expected.id)

        assert_that(expected, equal_to(result))

    def test_given_template_has_conference_func_key_when_getting_then_returns_conference_func_key(self):
        destination_row = self.create_conference_func_key()
        expected = self.prepare_template(destination_row,
                                         ConferenceDestination(conference_id=destination_row.conference_id))

        result = dao.get(expected.id)

        assert_that(expected, equal_to(result))

    def test_given_template_has_paging_func_key_when_getting_then_returns_paging_func_key(self):
        destination_row = self.create_paging_func_key()
        expected = self.prepare_template(destination_row,
                                         PagingDestination(paging_id=destination_row.paging_id))

        result = dao.get(expected.id)

        assert_that(expected, equal_to(result))

    def test_given_template_has_bsfilter_func_key_when_getting_then_returns_bsfilter_func_key(self):
        _, destination_row = self.create_bsfilter_func_key()
        expected = self.prepare_template(destination_row,
                                         BSFilterDestination(filter_member_id=destination_row.filtermember_id))

        result = dao.get(expected.id)

        assert_that(expected, equal_to(result))

    def test_given_template_has_service_func_key_when_getting_then_returns_service_func_key(self):
        destination_row = self.create_service_func_key('*25', 'enablednd')
        expected = self.prepare_template(destination_row,
                                         ServiceDestination(service='enablednd'))

        result = dao.get(expected.id)

        assert_that(expected, equal_to(result))

    def test_given_template_has_forward_func_key_when_getting_then_returns_service_func_key(self):
        destination_row = self.create_forward_func_key('_*23.', 'fwdbusy', '1000')
        expected = self.prepare_template(destination_row,
                                         ForwardDestination(forward='busy',
                                                            exten='1000'))

        result = dao.get(expected.id)

        assert_that(expected, equal_to(result))

    def test_given_template_has_park_position_func_key_when_getting_then_returns_service_func_key(self):
        destination_row = self.create_park_position_func_key('701')
        expected = self.prepare_template(destination_row,
                                         ParkPositionDestination(position=701))

        result = dao.get(expected.id)

        assert_that(expected, equal_to(result))

    def test_given_template_has_custom_func_key_when_getting_then_returns_service_func_key(self):
        destination_row = self.create_custom_func_key('1234')
        expected = self.prepare_template(destination_row,
                                         CustomDestination(exten='1234'))

        result = dao.get(expected.id)

        assert_that(expected, equal_to(result))

    def test_given_template_has_agent_func_key_when_getting_then_returns_agent_func_key(self):
        destination_row = self.create_agent_func_key('_*31.', 'agentstaticlogin')
        expected = self.prepare_template(destination_row,
                                         AgentDestination(action='login',
                                                          agent_id=destination_row.agent_id))

        result = dao.get(expected.id)

        assert_that(expected, equal_to(result))

    def test_given_template_has_transfer_func_key_when_getting_then_returns_transfer_func_key(self):
        destination_row = self.create_features_func_key('featuremap', 'atxfer', '*2')
        expected = self.prepare_template(destination_row,
                                         TransferDestination(transfer='attended'))

        result = dao.get(expected.id)

        assert_that(expected, equal_to(result))

    def test_given_template_has_parking_func_key_when_getting_then_returns_parking_func_key(self):
        destination_row = self.create_features_func_key('general', 'parkext', '701')
        expected = self.prepare_template(destination_row,
                                         ParkingDestination())

        result = dao.get(expected.id)

        assert_that(expected, equal_to(result))


class TestFuncKeyTemplateDelete(TestFuncKeyTemplateDao):

    def test_given_template_has_no_funckeys_when_deleting_then_deletes_template(self):
        template = self.prepare_template()

        dao.delete(template)

        result = self.session.query(FuncKeyTemplateSchema).get(template.id)

        assert_that(result, none())

    def test_given_template_has_func_key_when_deleting_then_deletes_mappings(self):
        destination_row = self.create_user_func_key()
        template = self.prepare_template(destination_row,
                                         UserDestination(user_id=destination_row.user_id))

        dao.delete(template)

        count = (self.session.query(FuncKeyMappingSchema)
                 .filter(FuncKeyMappingSchema.template_id == template.id)
                 .count())

        assert_that(count, equal_to(0))

    def test_given_template_has_forward_func_key_when_deleting_then_deletes_forward(self):
        destination_row = self.create_forward_func_key('_*22.', 'fwdrna', '1000')
        template = self.prepare_template(destination_row,
                                         ForwardDestination(forward='noanswer',
                                                            exten='1000'))

        dao.delete(template)

        self.assert_destination_deleted('forward', destination_row.extension_id)
        self.assert_func_key_deleted(destination_row.func_key_id)

    def test_given_template_has_park_position_func_key_when_deleting_then_deletes_park_position(self):
        destination_row = self.create_park_position_func_key('701')
        template = self.prepare_template(destination_row,
                                         ParkPositionDestination(position=701))

        dao.delete(template)

        self.assert_destination_deleted('park_position', destination_row.park_position)
        self.assert_func_key_deleted(destination_row.func_key_id)

    def test_given_template_has_custom_func_key_when_deleting_then_deletes_custom(self):
        destination_row = self.create_custom_func_key('1234')
        template = self.prepare_template(destination_row,
                                         CustomDestination(exten='1234'))

        dao.delete(template)

        self.assert_destination_deleted('custom', destination_row.exten)
        self.assert_func_key_deleted(destination_row.func_key_id)


class TestFuncKeyTemplateEdit(TestFuncKeyTemplateDao):

    def test_given_template_name_is_modified_when_editing_then_updates_name(self):
        template = self.prepare_template(name='foobar')
        template.name = 'newfoobar'

        dao.edit(template)

        template_row = self.session.query(FuncKeyTemplateSchema).get(template.id)
        assert_that(template_row.name, equal_to('newfoobar'))

    def test_given_func_key_modified_when_editing_then_updates_func_key(self):
        destination_row = self.create_user_func_key()
        template = self.prepare_template(destination_row,
                                         UserDestination(user_id=destination_row.user_id))

        template.keys[1].blf = True
        template.keys[1].label = 'mylabel'

        dao.edit(template)

        mapping = (self.session.query(FuncKeyMappingSchema)
                   .filter(FuncKeyMappingSchema.template_id == template.id)
                   .first())

        assert_that(mapping.blf, equal_to(True))
        assert_that(mapping.label, equal_to('mylabel'))
        assert_that(mapping.position, equal_to(1))

    def test_given_destination_replaced_when_editing_then_replaces_destination(self):
        first_destination_row = self.create_user_func_key()
        updated_destination_row = self.create_queue_func_key()

        template = self.prepare_template(first_destination_row,
                                         UserDestination(user_id=first_destination_row.user_id))

        updated_destination = QueueDestination(queue_id=updated_destination_row.queue_id)
        template.keys[1].destination = updated_destination

        dao.edit(template)

        mapping = (self.session.query(FuncKeyMappingSchema)
                   .filter(FuncKeyMappingSchema.template_id == template.id)
                   .first())

        assert_that(mapping.func_key_id, equal_to(updated_destination_row.func_key_id))
        assert_that(mapping.destination_type_id, equal_to(updated_destination_row.destination_type_id))
        assert_that(mapping.position, equal_to(1))

    def test_given_func_key_removed_when_editing_then_removes_func_key(self):
        destination_row = self.create_user_func_key()
        template = self.prepare_template(destination_row,
                                         UserDestination(user_id=destination_row.user_id))

        template.keys = {}

        dao.edit(template)

        self.assert_template_empty(template.id)

    def test_given_2_funckeys_when_only_1_modified_then_other_func_key_remains_unmodified(self):
        template_row = self.add_func_key_template()
        user_destination_row = self.create_user_func_key()
        queue_destination_row = self.create_queue_func_key()
        conference_destination_row = self.create_conference_func_key()

        # queue func key will be replaced by conference func key during edit
        self.add_destination_to_template(user_destination_row, template_row, position=1)
        self.add_destination_to_template(queue_destination_row, template_row, position=2)

        template = dao.get(template_row.id)

        template.keys[2] = FuncKey(destination=ConferenceDestination(conference_id=conference_destination_row.conference_id))

        dao.edit(template)

        first_mapping_row = (self.session.query(FuncKeyMappingSchema)
                             .filter(FuncKeyMappingSchema.template_id == template_row.id)
                             .filter(FuncKeyMappingSchema.position == 1)
                             .first())

        second_mapping_row = (self.session.query(FuncKeyMappingSchema)
                              .filter(FuncKeyMappingSchema.template_id == template_row.id)
                              .filter(FuncKeyMappingSchema.position == 2)
                              .first())

        assert_that(first_mapping_row.func_key_id, equal_to(user_destination_row.func_key_id))
        assert_that(second_mapping_row.func_key_id, equal_to(conference_destination_row.func_key_id))


class TestCreatePrivateTemplate(TestFuncKeyTemplateDao):

    def assert_private_template_created(self, template_id):
        template_row = self.session.query(FuncKeyTemplateSchema).get(template_id)
        assert_that(template_row, is_not(none()))

        assert_that(template_row, has_property('private', True))
        assert_that(template_row, has_property('name', none()))

    def test_create_private_template(self):
        template_id = dao.create_private_template()

        self.assert_private_template_created(template_id)

    @patch('xivo_dao.resources.func_key_template.dao.commit_or_abort')
    def test_given_database_error_then_transaction_aborted(self, commit_or_abort):
        dao.create_private_template()

        commit_or_abort.assert_called_with(ANY, DataError.on_create, 'FuncKeyTemplate')


class TestRemoveFuncKeyFromTemplate(TestFuncKeyTemplateDao):

    def test_given_one_func_key_mapped_when_removed_then_template_empty(self):
        template_row = self.add_func_key_template()
        func_key = self.create_user_func_key_for_template(template_row, 1)

        dao.remove_func_key_from_templates(func_key)

        self.assert_template_empty(template_row.id)

    def test_given_two_func_keys_mapped_when_first_removed_then_other_func_key_remains(self):
        template_row = self.add_func_key_template()
        first_func_key = self.create_user_func_key_for_template(template_row, 1)
        second_func_key = self.create_user_func_key_for_template(template_row, 2)

        dao.remove_func_key_from_templates(first_func_key)

        self.assert_template_contains_func_key(template_row, second_func_key)

    @patch('xivo_dao.resources.func_key_template.dao.commit_or_abort')
    def test_given_database_error_then_transaction_aborted(self, commit_or_abort):
        func_key = Mock(id=1)
        dao.remove_func_key_from_templates(func_key)

        commit_or_abort.assert_called_with(ANY, DataError.on_delete, 'FuncKeyTemplate')

    def assert_template_contains_func_key(self, template_row, func_key_row):
        count = (self.session.query(FuncKeyMappingSchema)
                 .filter(FuncKeyMappingSchema.template_id == template_row.id)
                 .filter(FuncKeyMappingSchema.func_key_id == func_key_row.id)
                 .count())

        assert_that(count, equal_to(1))


class TestDeletePrivateTemplate(TestFuncKeyTemplateDao):

    def test_given_empty_template_then_template_deleted(self):
        template_row = self.add_func_key_template(private=True)

        dao.delete_private_template(template_row.id)

        self.assert_template_deleted(template_row)

    def test_given_template_with_one_func_key_then_template_and_mapping_deleted(self):
        template_row = self.add_func_key_template(private=True)
        self.create_user_func_key_for_template(template_row, 1)

        dao.delete_private_template(template_row.id)

        self.assert_template_deleted(template_row)
        self.assert_template_empty(template_row.id)

    def assert_template_deleted(self, template_row):
        row = self.session.query(FuncKeyTemplateSchema).get(template_row.id)
        assert_that(row, none())

    @patch('xivo_dao.resources.func_key_template.dao.commit_or_abort')
    def test_given_database_error_then_transaction_aborted(self, commit_or_abort):
        template_id = 1
        dao.delete_private_template(template_id)

        commit_or_abort.assert_called_with(ANY, DataError.on_delete, 'FuncKeyTemplate')
