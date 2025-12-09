# Copyright 2014-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from uuid import uuid4

from hamcrest import assert_that, calling, equal_to, none, raises

from xivo_dao.alchemy.func_key_dest_agent import FuncKeyDestAgent
from xivo_dao.alchemy.func_key_dest_bsfilter import FuncKeyDestBSFilter
from xivo_dao.alchemy.func_key_dest_conference import FuncKeyDestConference
from xivo_dao.alchemy.func_key_dest_custom import FuncKeyDestCustom
from xivo_dao.alchemy.func_key_dest_features import (
    FuncKeyDestOnlineRecording,
    FuncKeyDestTransfer,
)
from xivo_dao.alchemy.func_key_dest_forward import FuncKeyDestForward
from xivo_dao.alchemy.func_key_dest_group import FuncKeyDestGroup
from xivo_dao.alchemy.func_key_dest_group_member import FuncKeyDestGroupMember
from xivo_dao.alchemy.func_key_dest_paging import FuncKeyDestPaging
from xivo_dao.alchemy.func_key_dest_paging import (
    FuncKeyDestPaging as FuncKeyDestPagingSchema,
)
from xivo_dao.alchemy.func_key_dest_park_position import FuncKeyDestParkPosition
from xivo_dao.alchemy.func_key_dest_parking import FuncKeyDestParking
from xivo_dao.alchemy.func_key_dest_queue import FuncKeyDestQueue
from xivo_dao.alchemy.func_key_dest_service import FuncKeyDestService
from xivo_dao.alchemy.func_key_dest_user import FuncKeyDestUser
from xivo_dao.alchemy.func_key_mapping import FuncKeyMapping
from xivo_dao.alchemy.func_key_template import FuncKeyTemplate
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema
from xivo_dao.helpers.exception import InputError, NotFoundError
from xivo_dao.resources.func_key.tests.test_helpers import FuncKeyHelper
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao


class TestDao(DAOTestCase, FuncKeyHelper):
    def setUp(self):
        super().setUp()
        self.setup_types()
        self.setup_destination_types()
        self.destination_type_ids = {
            value: key for key, value in self.destination_types.items()
        }

    def assert_template_empty(self, template_id):
        count = (
            self.session.query(FuncKeyMapping)
            .filter(FuncKeyMapping.template_id == template_id)
            .count()
        )

        assert_that(count, equal_to(0))

    def prepare_template(
        self,
        destination_row=None,
        destination=None,
        name=None,
        position=1,
        private=False,
    ):
        template = self.add_func_key_template(name=name, private=private)

        if destination_row and destination:
            self.add_destination_to_template(destination_row, template)
            template.keys = {
                position: FuncKeyMapping(
                    id=destination_row.func_key_id, destination=destination
                )
            }

        return template

    def build_template_with_key(self, destination, position=1):
        return FuncKeyTemplate(
            tenant_uuid=self.default_tenant.uuid,
            keys={position: FuncKeyMapping(destination=destination)},
        )


class TestCreate(TestDao):
    def assert_mapping_has_destination(
        self, destination_type, destination_row, position=1
    ):
        mapping_row = (
            self.session.query(FuncKeyMapping)
            .filter(FuncKeyMapping.func_key_id == destination_row.func_key_id)
            .first()
        )

        assert_that(mapping_row.position, equal_to(position))
        assert_that(mapping_row.func_key_id, equal_to(destination_row.func_key_id))

        destination_type_id = self.destination_type_ids[destination_type]
        assert_that(mapping_row.destination_type_id, equal_to(destination_type_id))

    def test_when_creating_an_empty_template_then_template_row(self):
        template = FuncKeyTemplate(tenant_uuid=self.default_tenant.uuid)

        result = dao.create(template)

        template_row = self.session.query(FuncKeyTemplate).first()

        assert_that(template_row.name, none())
        assert_that(result.name, none())
        assert_that(result.id, equal_to(template_row.id))
        assert_that(result.tenant_uuid, self.default_tenant.uuid)
        assert_that(result.keys, equal_to({}))

    def test_when_creating_a_template_with_name_then_row_has_name(self):
        template = FuncKeyTemplate(name='foobar', tenant_uuid=self.default_tenant.uuid)

        result = dao.create(template)

        template_row = self.session.query(FuncKeyTemplate).first()

        assert_that(template_row.name, equal_to(template.name))
        assert_that(result.name, equal_to(template.name))

    def test_given_template_has_func_key_when_creating_then_blf_is_activated_by_default(
        self,
    ):
        destination_row = self.create_user_func_key()
        template = self.build_template_with_key(
            FuncKeyDestUser(user_id=destination_row.user_id)
        )

        dao.create(template)

        mapping_row = (
            self.session.query(FuncKeyMapping)
            .filter(FuncKeyMapping.func_key_id == destination_row.func_key_id)
            .first()
        )

        assert_that(mapping_row.blf, equal_to(True))

    def test_given_template_has_user_func_key_when_creating_then_creates_mapping(self):
        destination_row = self.create_user_func_key()
        template = self.build_template_with_key(
            FuncKeyDestUser(user_id=destination_row.user_id)
        )

        result = dao.create(template)

        self.assert_mapping_has_destination('user', destination_row)
        assert_that(result.keys[1].id, equal_to(destination_row.func_key_id))

    def test_given_template_has_group_func_key_when_creating_then_creates_mapping(self):
        destination_row = self.create_group_func_key()
        template = self.build_template_with_key(
            FuncKeyDestGroup(group_id=destination_row.group_id)
        )

        result = dao.create(template)

        self.assert_mapping_has_destination('group', destination_row)
        assert_that(result.keys[1].id, equal_to(destination_row.func_key_id))

    def test_given_template_has_queue_func_key_when_creating_then_creates_mapping(self):
        destination_row = self.create_queue_func_key()
        template = self.build_template_with_key(
            FuncKeyDestQueue(queue_id=destination_row.queue_id)
        )

        result = dao.create(template)

        self.assert_mapping_has_destination('queue', destination_row)
        assert_that(result.keys[1].id, equal_to(destination_row.func_key_id))

    def test_given_template_has_conference_func_key_when_creating_then_creates_mapping(
        self,
    ):
        destination_row = self.create_conference_func_key()
        template = self.build_template_with_key(
            FuncKeyDestConference(conference_id=destination_row.conference_id)
        )

        result = dao.create(template)

        self.assert_mapping_has_destination('conference', destination_row)
        assert_that(result.keys[1].id, equal_to(destination_row.func_key_id))

    def test_given_template_has_paging_func_key_when_creating_then_creates_mapping(
        self,
    ):
        destination_row = self.create_paging_func_key()
        template = self.build_template_with_key(
            FuncKeyDestPaging(paging_id=destination_row.paging_id)
        )

        result = dao.create(template)

        self.assert_mapping_has_destination('paging', destination_row)
        assert_that(result.keys[1].id, equal_to(destination_row.func_key_id))

    def test_given_template_has_bsfilter_func_key_when_creating_then_creates_mapping(
        self,
    ):
        _, destination_row = self.create_bsfilter_func_key()
        template = self.build_template_with_key(
            FuncKeyDestBSFilter(filter_member_id=destination_row.filtermember_id)
        )

        result = dao.create(template)

        self.assert_mapping_has_destination('bsfilter', destination_row)
        assert_that(result.keys[1].id, equal_to(destination_row.func_key_id))

    def test_given_template_has_service_func_key_when_creating_then_creates_mapping(
        self,
    ):
        destination_row = self.create_service_func_key('*20', 'enablednd')
        template = self.build_template_with_key(FuncKeyDestService(service='enablednd'))

        result = dao.create(template)

        self.assert_mapping_has_destination('service', destination_row)
        assert_that(result.keys[1].id, equal_to(destination_row.func_key_id))

    def test_given_template_has_commented_service_func_key_when_creating_then_creates_mapping(
        self,
    ):
        destination_row = self.create_service_func_key('*20', 'enablednd', commented=1)
        template = self.build_template_with_key(FuncKeyDestService(service='enablednd'))

        dao.create(template)

        self.assert_mapping_has_destination('service', destination_row)

    def test_given_template_has_forward_func_key_when_creating_then_creates_mapping(
        self,
    ):
        feature_extension_row = self.add_extenfeatures('*21', 'fwdbusy')

        template = self.build_template_with_key(FuncKeyDestForward(forward='busy'))

        result = dao.create(template)

        destination_row = self.find_destination('forward', feature_extension_row.uuid)
        assert_that(destination_row.number, none())

        self.assert_mapping_has_destination('forward', destination_row)
        assert_that(result.keys[1].id, equal_to(destination_row.func_key_id))

    def test_given_template_has_forward_func_key_with_exten_when_creating_then_creates_destination_with_number(
        self,
    ):
        feature_extension_row = self.add_extenfeatures('*22', 'fwdrna')

        template = self.build_template_with_key(
            FuncKeyDestForward(forward='noanswer', exten='1000')
        )

        result = dao.create(template)

        destination_row = self.find_destination('forward', feature_extension_row.uuid)
        assert_that(destination_row.number, equal_to('1000'))
        assert_that(result.keys[1].id, equal_to(destination_row.func_key_id))

    def test_given_template_has_commented_forward_func_key_when_creating_then_creates_destination(
        self,
    ):
        feature_extension_row = self.add_extenfeatures('*22', 'fwdrna', commented=1)

        template = self.build_template_with_key(FuncKeyDestForward(forward='noanswer'))

        dao.create(template)

        destination_row = self.find_destination('forward', feature_extension_row.uuid)
        self.assert_mapping_has_destination('forward', destination_row)

    def test_given_template_has_custom_func_key_when_creating_then_creates_mapping(
        self,
    ):
        template = self.build_template_with_key(FuncKeyDestCustom(exten='1234'))

        result = dao.create(template)

        destination_row = self.find_destination('custom', '1234')
        assert_that(destination_row.exten, equal_to('1234'))

        self.assert_mapping_has_destination('custom', destination_row)
        assert_that(result.keys[1].id, equal_to(destination_row.func_key_id))

    def test_given_template_has_agent_func_key_when_creating_then_creates_mapping(self):
        destination_row = self.create_agent_func_key('_*31.', 'agentstaticlogin')

        template = self.build_template_with_key(
            FuncKeyDestAgent(action='login', agent_id=destination_row.agent_id)
        )

        result = dao.create(template)

        self.assert_mapping_has_destination('agent', destination_row)
        assert_that(result.keys[1].id, equal_to(destination_row.func_key_id))

    def test_given_template_has_commented_agent_func_key_when_creating_then_creates_mapping(
        self,
    ):
        destination_row = self.create_agent_func_key(
            '_*31.', 'agentstaticlogin', commented=1
        )

        template = self.build_template_with_key(
            FuncKeyDestAgent(action='login', agent_id=destination_row.agent_id)
        )

        dao.create(template)

        self.assert_mapping_has_destination('agent', destination_row)

    def test_given_template_has_transfer_func_key_when_creating_then_creates_mapping(
        self,
    ):
        destination_row = self.create_features_func_key('featuremap', 'blindxfer', '*1')

        template = self.build_template_with_key(FuncKeyDestTransfer(transfer='blind'))

        result = dao.create(template)

        self.assert_mapping_has_destination('features', destination_row)
        assert_that(result.keys[1].id, equal_to(destination_row.func_key_id))

    def test_given_template_has_commented_transfer_func_key_when_creating_then_creates_mapping(
        self,
    ):
        destination_row = self.create_features_func_key(
            'featuremap', 'blindxfer', '*1', commented=1
        )

        template = self.build_template_with_key(FuncKeyDestTransfer(transfer='blind'))

        dao.create(template)

        self.assert_mapping_has_destination('features', destination_row)

    def test_given_template_has_onlinerec_destination_when_creating_then_creates_mapping(
        self,
    ):
        destination_row = self.create_features_func_key(
            'applicationmap', 'togglerecord', '*3,self,AGI(localhost,...)'
        )

        template = self.build_template_with_key(FuncKeyDestOnlineRecording())

        result = dao.create(template)

        self.assert_mapping_has_destination('features', destination_row)
        assert_that(result.keys[1].id, equal_to(destination_row.func_key_id))

    def test_given_template_has_park_position_func_key_when_creating_then_creates_mapping(
        self,
    ):
        destination_row = self.create_park_position_func_key('801')
        template = self.build_template_with_key(
            FuncKeyDestParkPosition(
                parking_lot_id=destination_row.parking_lot_id,
                position=destination_row.position,
            )
        )

        result = dao.create(template)

        self.assert_mapping_has_destination('park_position', destination_row)
        assert_that(result.keys[1].id, equal_to(destination_row.func_key_id))

    def test_given_template_has_parking_func_key_when_creating_then_creates_mapping(
        self,
    ):
        destination_row = self.create_parking_func_key()
        template = self.build_template_with_key(
            FuncKeyDestParking(
                parking_lot_id=destination_row.parking_lot_id,
            )
        )

        result = dao.create(template)

        self.assert_mapping_has_destination('parking', destination_row)
        assert_that(result.keys[1].id, equal_to(destination_row.func_key_id))

    def test_given_destination_funckey_does_not_exist_then_raises_error(self):
        self.create_service_func_key('', '')

        template = self.build_template_with_key(
            FuncKeyDestService(feature_extension_uuid=uuid4())
        )

        assert_that(calling(dao.create).with_args(template), raises(InputError))

    def test_given_no_user_func_key_when_created_then_create_new_user_func_key(self):
        user = self.add_user()

        dest_user_count = (
            self.session.query(FuncKeyDestUser)
            .filter(FuncKeyDestUser.user_id == user.id)
            .count()
        )
        assert_that(dest_user_count, equal_to(0))

        template = self.build_template_with_key(FuncKeyDestUser(user_id=user.id))
        dao.create(template)

        template = self.build_template_with_key(FuncKeyDestUser(user_id=user.id))
        dao.create(template)

        dest_user_count = (
            self.session.query(FuncKeyDestUser)
            .filter(FuncKeyDestUser.user_id == user.id)
            .count()
        )
        assert_that(dest_user_count, equal_to(1))

    def test_given_no_group_func_key_when_created_then_create_new_group_func_key(self):
        group = self.add_group()

        dest_group_count = (
            self.session.query(FuncKeyDestGroup)
            .filter(FuncKeyDestGroup.group_id == group.id)
            .count()
        )
        assert_that(dest_group_count, equal_to(0))

        template = self.build_template_with_key(FuncKeyDestGroup(group_id=group.id))
        dao.create(template)

        template = self.build_template_with_key(FuncKeyDestGroup(group_id=group.id))
        dao.create(template)

        dest_group_count = (
            self.session.query(FuncKeyDestGroup)
            .filter(FuncKeyDestGroup.group_id == group.id)
            .count()
        )
        assert_that(dest_group_count, equal_to(1))

    def test_given_no_group_member_func_key_when_created_then_create_new_group_func_key(
        self,
    ):
        group = self.add_group()
        self.add_feature_extension(feature='groupmemberjoin')

        dest_groupmember_count = (
            self.session.query(FuncKeyDestGroupMember)
            .filter(FuncKeyDestGroupMember.group_id == group.id)
            .count()
        )
        assert_that(dest_groupmember_count, equal_to(0))

        template = self.build_template_with_key(
            FuncKeyDestGroupMember(group_id=group.id, action='groupmemberjoin')
        )
        dao.create(template)

        template = self.build_template_with_key(
            FuncKeyDestGroupMember(group_id=group.id, action='groupmemberjoin')
        )
        dao.create(template)

        dest_group_count = (
            self.session.query(FuncKeyDestGroupMember)
            .filter(FuncKeyDestGroupMember.group_id == group.id)
            .count()
        )
        assert_that(dest_group_count, equal_to(1))

    def test_given_no_queue_func_key_when_created_then_create_new_queue_func_key(self):
        queue = self.add_queuefeatures()

        dest_queue_count = (
            self.session.query(FuncKeyDestQueue)
            .filter(FuncKeyDestQueue.queue_id == queue.id)
            .count()
        )
        assert_that(dest_queue_count, equal_to(0))

        template = self.build_template_with_key(FuncKeyDestQueue(queue_id=queue.id))
        dao.create(template)

        template = self.build_template_with_key(FuncKeyDestQueue(queue_id=queue.id))
        dao.create(template)

        dest_queue_count = (
            self.session.query(FuncKeyDestQueue)
            .filter(FuncKeyDestQueue.queue_id == queue.id)
            .count()
        )
        assert_that(dest_queue_count, equal_to(1))

    def test_given_no_conference_func_key_when_created_then_create_new_conference_func_key(
        self,
    ):
        conference = self.add_conference()

        dest_conference_count = (
            self.session.query(FuncKeyDestConference)
            .filter(FuncKeyDestConference.conference_id == conference.id)
            .count()
        )
        assert_that(dest_conference_count, equal_to(0))

        template = self.build_template_with_key(
            FuncKeyDestConference(conference_id=conference.id)
        )
        dao.create(template)

        template = self.build_template_with_key(
            FuncKeyDestConference(conference_id=conference.id)
        )
        dao.create(template)

        dest_conference_count = (
            self.session.query(FuncKeyDestConference)
            .filter(FuncKeyDestConference.conference_id == conference.id)
            .count()
        )
        assert_that(dest_conference_count, equal_to(1))

    def test_given_no_paging_func_key_when_created_then_create_new_paging_func_key(
        self,
    ):
        paging = self.add_paging()

        dest_paging_count = (
            self.session.query(FuncKeyDestPagingSchema)
            .filter(FuncKeyDestPagingSchema.paging_id == paging.id)
            .count()
        )
        assert_that(dest_paging_count, equal_to(0))

        template = self.build_template_with_key(FuncKeyDestPaging(paging_id=paging.id))
        dao.create(template)

        template = self.build_template_with_key(FuncKeyDestPaging(paging_id=paging.id))
        dao.create(template)

        dest_paging_count = (
            self.session.query(FuncKeyDestPagingSchema)
            .filter(FuncKeyDestPagingSchema.paging_id == paging.id)
            .count()
        )
        assert_that(dest_paging_count, equal_to(1))

    def test_given_no_bsfilter_func_key_when_created_then_create_new_bsfilter_func_key(
        self,
    ):
        call_filter = self.add_call_filter()
        filter_member = self.add_call_filter_member(callfilterid=call_filter.id)

        dest_bsfilter_count = (
            self.session.query(FuncKeyDestBSFilter)
            .filter(FuncKeyDestBSFilter.filter_member_id == filter_member.id)
            .count()
        )
        assert_that(dest_bsfilter_count, equal_to(0))

        template = self.build_template_with_key(
            FuncKeyDestBSFilter(filter_member_id=filter_member.id)
        )
        dao.create(template)

        template = self.build_template_with_key(
            FuncKeyDestBSFilter(filter_member_id=filter_member.id)
        )
        dao.create(template)

        dest_bsfilter_count = (
            self.session.query(FuncKeyDestBSFilter)
            .filter(FuncKeyDestBSFilter.filter_member_id == filter_member.id)
            .count()
        )
        assert_that(dest_bsfilter_count, equal_to(1))

    def test_given_no_agent_func_key_when_created_then_create_new_agent_func_key(self):
        agent = self.add_agent()
        self.add_feature_extension(feature='agentstaticlogin')

        dest_agent_count = (
            self.session.query(FuncKeyDestAgent)
            .filter(FuncKeyDestAgent.agent_id == agent.id)
            .count()
        )
        assert_that(dest_agent_count, equal_to(0))

        template = self.build_template_with_key(
            FuncKeyDestAgent(agent_id=agent.id, action='agentstaticlogin')
        )
        dao.create(template)

        template = self.build_template_with_key(
            FuncKeyDestAgent(agent_id=agent.id, action='agentstaticlogin')
        )
        dao.create(template)

        dest_agent_count = (
            self.session.query(FuncKeyDestAgent)
            .filter(FuncKeyDestAgent.agent_id == agent.id)
            .count()
        )
        assert_that(dest_agent_count, equal_to(1))

    def test_given_no_park_position_func_key_when_created_then_create_new_park_position_func_key(
        self,
    ):
        parking_lot = self.add_parking_lot()

        dest_park_position_count = (
            self.session.query(FuncKeyDestParkPosition)
            .filter(FuncKeyDestParkPosition.parking_lot_id == parking_lot.id)
            .count()
        )
        assert_that(dest_park_position_count, equal_to(0))

        template = self.build_template_with_key(
            FuncKeyDestParkPosition(parking_lot_id=parking_lot.id, position='801')
        )
        dao.create(template)

        template = self.build_template_with_key(
            FuncKeyDestParkPosition(parking_lot_id=parking_lot.id, position='801')
        )
        dao.create(template)

        dest_park_position_count = (
            self.session.query(FuncKeyDestParkPosition)
            .filter(FuncKeyDestParkPosition.parking_lot_id == parking_lot.id)
            .count()
        )
        assert_that(dest_park_position_count, equal_to(1))

    def test_given_no_parking_func_key_when_created_then_create_new_parking_func_key(
        self,
    ):
        parking_lot = self.add_parking_lot()

        dest_parking_count = (
            self.session.query(FuncKeyDestParking)
            .filter(FuncKeyDestParking.parking_lot_id == parking_lot.id)
            .count()
        )
        assert_that(dest_parking_count, equal_to(0))

        template = self.build_template_with_key(
            FuncKeyDestParking(parking_lot_id=parking_lot.id)
        )
        dao.create(template)

        template = self.build_template_with_key(
            FuncKeyDestParking(parking_lot_id=parking_lot.id)
        )
        dao.create(template)

        dest_parking_count = (
            self.session.query(FuncKeyDestParking)
            .filter(FuncKeyDestParking.parking_lot_id == parking_lot.id)
            .count()
        )
        assert_that(dest_parking_count, equal_to(1))


class TestGet(TestDao):
    def test_given_no_template_then_raises_error(self):
        assert_that(calling(dao.get).with_args(1), raises(NotFoundError))

    def test_given_empty_template_when_getting_then_returns_empty_template(self):
        template_row = self.add_func_key_template()

        result = dao.get(template_row.id)

        assert_that(result, equal_to(template_row))

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()

        funckey_template_row = self.add_func_key_template(tenant_uuid=tenant.uuid)
        funckey_template = dao.get(funckey_template_row.id, tenant_uuids=[tenant.uuid])
        assert_that(funckey_template, equal_to(funckey_template_row))

        funckey_template_row = self.add_func_key_template()
        self.assertRaises(
            NotFoundError,
            dao.get,
            funckey_template_row.id,
            tenant_uuids=[tenant.uuid],
        )

    def test_given_template_is_private_then_func_keys_are_not_inherited(self):
        destination_row = self.create_user_func_key()
        expected = self.prepare_template(
            destination_row,
            FuncKeyDestUser(user_id=destination_row.user_id),
            private=True,
        )
        expected.keys[1].inherited = False

        result = dao.get(expected.id)

        assert_that(expected, equal_to(result))

    def test_given_template_is_public_then_func_keys_are_inherited(self):
        destination_row = self.create_user_func_key()
        expected = self.prepare_template(
            destination_row,
            FuncKeyDestUser(user_id=destination_row.user_id),
            private=False,
        )
        expected.keys[1].inherited = True

        result = dao.get(expected.id)

        assert_that(expected, equal_to(result))

    def test_given_template_has_user_func_key_when_getting_then_returns_user_func_key(
        self,
    ):
        destination_row = self.create_user_func_key()
        expected = self.prepare_template(
            destination_row, FuncKeyDestUser(user_id=destination_row.user_id)
        )

        result = dao.get(expected.id)

        assert_that(expected, equal_to(result))

    def test_given_template_has_queue_func_key_when_getting_then_returns_queue_func_key(
        self,
    ):
        destination_row = self.create_queue_func_key()
        expected = self.prepare_template(
            destination_row, FuncKeyDestQueue(queue_id=destination_row.queue_id)
        )

        result = dao.get(expected.id)

        assert_that(expected, equal_to(result))

    def test_given_template_has_group_func_key_when_getting_then_returns_group_func_key(
        self,
    ):
        destination_row = self.create_group_func_key()
        expected = self.prepare_template(
            destination_row, FuncKeyDestGroup(group_id=destination_row.group_id)
        )

        result = dao.get(expected.id)

        assert_that(expected, equal_to(result))

    def test_given_template_has_conference_func_key_when_getting_then_returns_conference_func_key(
        self,
    ):
        destination_row = self.create_conference_func_key()
        expected = self.prepare_template(
            destination_row,
            FuncKeyDestConference(conference_id=destination_row.conference_id),
        )

        result = dao.get(expected.id)

        assert_that(expected, equal_to(result))

    def test_given_template_has_paging_func_key_when_getting_then_returns_paging_func_key(
        self,
    ):
        destination_row = self.create_paging_func_key()
        expected = self.prepare_template(
            destination_row, FuncKeyDestPaging(paging_id=destination_row.paging_id)
        )

        result = dao.get(expected.id)

        assert_that(expected, equal_to(result))

    def test_given_template_has_bsfilter_func_key_when_getting_then_returns_bsfilter_func_key(
        self,
    ):
        _, destination_row = self.create_bsfilter_func_key()
        expected = self.prepare_template(
            destination_row,
            FuncKeyDestBSFilter(filter_member_id=destination_row.filtermember_id),
        )

        result = dao.get(expected.id)

        assert_that(expected, equal_to(result))

    def test_given_template_has_service_func_key_when_getting_then_returns_service_func_key(
        self,
    ):
        destination_row = self.create_service_func_key('*25', 'enablednd')
        expected = self.prepare_template(
            destination_row,
            FuncKeyDestService(
                service='enablednd',
                feature_extension_uuid=destination_row.feature_extension_uuid,
            ),
        )

        result = dao.get(expected.id)

        assert_that(expected, equal_to(result))

    def test_given_template_has_forward_func_key_when_getting_then_returns_service_func_key(
        self,
    ):
        destination_row = self.create_forward_func_key('_*23.', 'fwdbusy', '1000')
        expected = self.prepare_template(
            destination_row,
            FuncKeyDestForward(
                forward='busy',
                exten='1000',
                feature_extension_uuid=destination_row.feature_extension_uuid,
            ),
        )

        result = dao.get(expected.id)

        assert_that(expected, equal_to(result))

    def test_given_template_has_custom_func_key_when_getting_then_returns_service_func_key(
        self,
    ):
        destination_row = self.create_custom_func_key('1234')
        expected = self.prepare_template(
            destination_row, FuncKeyDestCustom(exten='1234')
        )

        result = dao.get(expected.id)

        assert_that(expected, equal_to(result))

    def test_given_template_has_agent_func_key_when_getting_then_returns_agent_func_key(
        self,
    ):
        destination_row = self.create_agent_func_key('_*31.', 'agentstaticlogin')
        expected = self.prepare_template(
            destination_row,
            FuncKeyDestAgent(
                action='login',
                agent_id=destination_row.agent_id,
                feature_extension_uuid=destination_row.feature_extension_uuid,
            ),
        )

        result = dao.get(expected.id)

        assert_that(expected, equal_to(result))

    def test_given_template_has_transfer_func_key_when_getting_then_returns_transfer_func_key(
        self,
    ):
        destination_row = self.create_features_func_key('featuremap', 'atxfer', '*2')
        expected = self.prepare_template(
            destination_row,
            FuncKeyDestTransfer(
                transfer='attended', feature_id=destination_row.features_id
            ),
        )

        result = dao.get(expected.id)

        assert_that(expected, equal_to(result))

    def test_given_template_has_park_position_func_key_when_getting_then_returns_park_position_func_key(
        self,
    ):
        destination_row = self.create_park_position_func_key('801')
        expected = self.prepare_template(
            destination_row,
            FuncKeyDestParkPosition(
                parking_lot_id=destination_row.parking_lot_id,
                position='801',
            ),
        )

        result = dao.get(expected.id)

        assert_that(expected, equal_to(result))

    def test_given_template_has_parking_func_key_when_getting_then_returns_parking_func_key(
        self,
    ):
        destination_row = self.create_parking_func_key()
        expected = self.prepare_template(
            destination_row,
            FuncKeyDestParkPosition(
                parking_lot_id=destination_row.parking_lot_id,
            ),
        )

        result = dao.get(expected.id)

        assert_that(expected, equal_to(result))


class TestDelete(TestDao):
    def test_given_template_has_no_funckeys_when_deleting_then_deletes_template(self):
        template = self.prepare_template()

        dao.delete(template)

        result = self.session.get(FuncKeyTemplate, template.id)

        assert_that(result, none())

    def test_given_template_has_func_key_when_deleting_then_deletes_mappings(self):
        destination_row = self.create_user_func_key()
        template = self.prepare_template(
            destination_row, FuncKeyDestUser(user_id=destination_row.user_id)
        )

        dao.delete(template)

        count = (
            self.session.query(FuncKeyMapping)
            .filter(FuncKeyMapping.template_id == template.id)
            .count()
        )

        assert_that(count, equal_to(0))

    def test_given_template_has_forward_func_key_when_deleting_then_deletes_forward(
        self,
    ):
        destination_row = self.create_forward_func_key('_*22.', 'fwdrna', '1000')
        template = self.prepare_template(
            destination_row, FuncKeyDestForward(forward='noanswer', exten='1000')
        )

        dao.delete(template)

        self.assert_destination_deleted(
            'forward', destination_row.feature_extension_uuid
        )

    def test_given_template_has_custom_func_key_when_deleting_then_deletes_custom(self):
        destination_row = self.create_custom_func_key('1234')
        template = self.prepare_template(
            destination_row, FuncKeyDestCustom(exten='1234')
        )

        dao.delete(template)

        self.assert_destination_deleted('custom', destination_row.exten)

    def test_given_template_is_associated_to_user_when_deleting_then_dissociates_user(
        self,
    ):
        template = self.add_func_key_template()
        user_row = self.add_user(func_key_template_id=template.id)

        dao.delete(template)

        func_key_template_id = (
            self.session.query(UserSchema.func_key_template_id)
            .filter(UserSchema.id == user_row.id)
            .scalar()
        )
        assert_that(func_key_template_id, none())

    def test_given_template_is_associated_to_user_when_deleting_template(self):
        user = self.add_user()
        template = self.build_template_with_key(FuncKeyDestUser(user_id=user.id))
        dao.create(template)

        dao.delete(template)

        dest_user_count = (
            self.session.query(FuncKeyDestUser)
            .filter(FuncKeyDestUser.user_id == user.id)
            .count()
        )
        assert_that(dest_user_count, equal_to(0))

    def test_given_multi_template_is_associated_to_user_when_deleting_template(self):
        user = self.add_user()
        template = self.build_template_with_key(FuncKeyDestUser(user_id=user.id))
        dao.create(template)

        template = self.build_template_with_key(FuncKeyDestUser(user_id=user.id))
        dao.create(template)

        template = self.build_template_with_key(FuncKeyDestUser(user_id=user.id))
        dao.create(template)

        dao.delete(template)

        dest_user_count = (
            self.session.query(FuncKeyDestUser)
            .filter(FuncKeyDestUser.user_id == user.id)
            .count()
        )
        assert_that(dest_user_count, equal_to(1))

    def test_given_template_is_associated_to_group_when_deleting_template(self):
        group = self.add_group()
        template = self.build_template_with_key(FuncKeyDestGroup(group_id=group.id))
        dao.create(template)

        dao.delete(template)

        dest_group_count = (
            self.session.query(FuncKeyDestGroup)
            .filter(FuncKeyDestGroup.group_id == group.id)
            .count()
        )
        assert_that(dest_group_count, equal_to(0))

    def test_given_multi_template_is_associated_to_group_when_deleting_template(self):
        group = self.add_group()
        template = self.build_template_with_key(FuncKeyDestGroup(group_id=group.id))
        dao.create(template)

        template = self.build_template_with_key(FuncKeyDestGroup(group_id=group.id))
        dao.create(template)

        template = self.build_template_with_key(FuncKeyDestGroup(group_id=group.id))
        dao.create(template)

        dao.delete(template)

        dest_group_count = (
            self.session.query(FuncKeyDestGroup)
            .filter(FuncKeyDestGroup.group_id == group.id)
            .count()
        )
        assert_that(dest_group_count, equal_to(1))

    def test_given_template_is_associated_to_queue_when_deleting_template(self):
        queue = self.add_queuefeatures()
        template = self.build_template_with_key(FuncKeyDestQueue(queue_id=queue.id))
        dao.create(template)

        dao.delete(template)

        dest_queue_count = (
            self.session.query(FuncKeyDestQueue)
            .filter(FuncKeyDestQueue.queue_id == queue.id)
            .count()
        )
        assert_that(dest_queue_count, equal_to(0))

    def test_given_multi_template_is_associated_to_queue_when_deleting_template(self):
        queue = self.add_queuefeatures()
        template = self.build_template_with_key(FuncKeyDestQueue(queue_id=queue.id))
        dao.create(template)

        template = self.build_template_with_key(FuncKeyDestQueue(queue_id=queue.id))
        dao.create(template)

        template = self.build_template_with_key(FuncKeyDestQueue(queue_id=queue.id))
        dao.create(template)

        dao.delete(template)

        dest_queue_count = (
            self.session.query(FuncKeyDestQueue)
            .filter(FuncKeyDestQueue.queue_id == queue.id)
            .count()
        )
        assert_that(dest_queue_count, equal_to(1))

    def test_given_template_is_associated_to_conference_when_deleting_template(self):
        conference = self.add_conference()
        template = self.build_template_with_key(
            FuncKeyDestConference(conference_id=conference.id)
        )
        dao.create(template)

        dao.delete(template)

        dest_conference_count = (
            self.session.query(FuncKeyDestConference)
            .filter(FuncKeyDestConference.conference_id == conference.id)
            .count()
        )
        assert_that(dest_conference_count, equal_to(0))

    def test_given_multi_template_is_associated_to_conference_when_deleting_template(
        self,
    ):
        conference = self.add_conference()
        template = self.build_template_with_key(
            FuncKeyDestConference(conference_id=conference.id)
        )
        dao.create(template)

        template = self.build_template_with_key(
            FuncKeyDestConference(conference_id=conference.id)
        )
        dao.create(template)

        dao.delete(template)

        dest_conference_count = (
            self.session.query(FuncKeyDestConference)
            .filter(FuncKeyDestConference.conference_id == conference.id)
            .count()
        )
        assert_that(dest_conference_count, equal_to(1))

    def test_given_template_is_associated_to_paging_when_deleting_template(self):
        paging = self.add_paging()
        template = self.build_template_with_key(FuncKeyDestPaging(paging_id=paging.id))
        dao.create(template)

        dao.delete(template)

        dest_paging_count = (
            self.session.query(FuncKeyDestPagingSchema)
            .filter(FuncKeyDestPagingSchema.paging_id == paging.id)
            .count()
        )
        assert_that(dest_paging_count, equal_to(0))

    def test_given_multi_template_is_associated_to_paging_when_deleting_template(self):
        paging = self.add_paging()
        template = self.build_template_with_key(FuncKeyDestPaging(paging_id=paging.id))
        dao.create(template)

        template = self.build_template_with_key(FuncKeyDestPaging(paging_id=paging.id))
        dao.create(template)

        dao.delete(template)

        dest_paging_count = (
            self.session.query(FuncKeyDestPagingSchema)
            .filter(FuncKeyDestPagingSchema.paging_id == paging.id)
            .count()
        )
        assert_that(dest_paging_count, equal_to(1))

    def test_given_template_is_associated_to_bsfilter_when_deleting_template(self):
        call_filter = self.add_call_filter()
        filter_member = self.add_call_filter_member(callfilterid=call_filter.id)
        template = self.build_template_with_key(
            FuncKeyDestBSFilter(filter_member_id=filter_member.id)
        )
        dao.create(template)

        dao.delete(template)

        dest_bsfilter_count = (
            self.session.query(FuncKeyDestBSFilter)
            .filter(FuncKeyDestBSFilter.filter_member_id == filter_member.id)
            .count()
        )
        assert_that(dest_bsfilter_count, equal_to(0))

    def test_given_multi_template_is_associated_to_bsfilter_when_deleting_template(
        self,
    ):
        call_filter = self.add_call_filter()
        filter_member = self.add_call_filter_member(callfilterid=call_filter.id)
        template = self.build_template_with_key(
            FuncKeyDestBSFilter(filter_member_id=filter_member.id)
        )
        dao.create(template)

        template = self.build_template_with_key(
            FuncKeyDestBSFilter(filter_member_id=filter_member.id)
        )
        dao.create(template)

        dao.delete(template)

        dest_bsfilter_count = (
            self.session.query(FuncKeyDestBSFilter)
            .filter(FuncKeyDestBSFilter.filter_member_id == filter_member.id)
            .count()
        )
        assert_that(dest_bsfilter_count, equal_to(1))

    def test_given_template_is_associated_to_agent_when_deleting_template(self):
        agent = self.add_agent()
        self.add_feature_extension(feature='agentstaticlogin')
        template = self.build_template_with_key(
            FuncKeyDestAgent(agent_id=agent.id, action='agentstaticlogin')
        )
        dao.create(template)

        dao.delete(template)

        dest_agent_count = (
            self.session.query(FuncKeyDestAgent)
            .filter(FuncKeyDestAgent.agent_id == agent.id)
            .count()
        )
        assert_that(dest_agent_count, equal_to(0))

    def test_given_multi_template_is_associated_to_agent_when_deleting_template(self):
        agent = self.add_agent()
        self.add_feature_extension(feature='agentstaticlogin')
        template = self.build_template_with_key(
            FuncKeyDestAgent(agent_id=agent.id, action='agentstaticlogin')
        )

        dao.create(template)

        template = self.build_template_with_key(
            FuncKeyDestAgent(agent_id=agent.id, action='agentstaticlogin')
        )
        dao.create(template)

        template = self.build_template_with_key(
            FuncKeyDestAgent(agent_id=agent.id, action='agentstaticlogin')
        )
        dao.create(template)

        dao.delete(template)

        dest_agent_count = (
            self.session.query(FuncKeyDestAgent)
            .filter(FuncKeyDestAgent.agent_id == agent.id)
            .count()
        )
        assert_that(dest_agent_count, equal_to(1))

    def test_given_template_is_associated_to_park_position_when_deleting_template(self):
        parking_lot = self.add_parking_lot()
        template = self.build_template_with_key(
            FuncKeyDestParkPosition(parking_lot_id=parking_lot.id, position='801')
        )
        dao.create(template)

        dao.delete(template)

        dest_park_position_count = (
            self.session.query(FuncKeyDestParkPosition)
            .filter(FuncKeyDestParkPosition.parking_lot_id == parking_lot.id)
            .count()
        )
        assert_that(dest_park_position_count, equal_to(0))

    def test_given_multi_template_is_associated_to_park_position_when_deleting_template(
        self,
    ):
        parking_lot = self.add_parking_lot()
        template = self.build_template_with_key(
            FuncKeyDestParkPosition(parking_lot_id=parking_lot.id, position='801')
        )
        dao.create(template)

        template = self.build_template_with_key(
            FuncKeyDestParkPosition(parking_lot_id=parking_lot.id, position='801')
        )
        dao.create(template)

        dao.delete(template)

        dest_park_position_count = (
            self.session.query(FuncKeyDestParkPosition)
            .filter(FuncKeyDestParkPosition.parking_lot_id == parking_lot.id)
            .count()
        )
        assert_that(dest_park_position_count, equal_to(1))

    def test_given_template_is_associated_to_parking_when_deleting_template(self):
        parking_lot = self.add_parking_lot()
        template = self.build_template_with_key(
            FuncKeyDestParking(parking_lot_id=parking_lot.id)
        )
        dao.create(template)

        dao.delete(template)

        dest_parking_count = (
            self.session.query(FuncKeyDestParking)
            .filter(FuncKeyDestParking.parking_lot_id == parking_lot.id)
            .count()
        )
        assert_that(dest_parking_count, equal_to(0))

    def test_given_multi_template_is_associated_to_parking_when_deleting_template(
        self,
    ):
        parking_lot = self.add_parking_lot()
        template = self.build_template_with_key(
            FuncKeyDestParking(parking_lot_id=parking_lot.id)
        )
        dao.create(template)

        template = self.build_template_with_key(
            FuncKeyDestParking(parking_lot_id=parking_lot.id)
        )
        dao.create(template)

        dao.delete(template)

        dest_parking_count = (
            self.session.query(FuncKeyDestParking)
            .filter(FuncKeyDestParking.parking_lot_id == parking_lot.id)
            .count()
        )
        assert_that(dest_parking_count, equal_to(1))


class TestEdit(TestDao):
    def test_given_template_name_is_modified_when_editing_then_updates_name(self):
        template = self.prepare_template(name='foobar')
        template.name = 'newfoobar'

        dao.edit(template)

        template_row = self.session.get(FuncKeyTemplate, template.id)
        assert_that(template_row.name, equal_to('newfoobar'))

    def test_given_func_key_modified_when_editing_then_updates_func_key(self):
        destination_row = self.create_user_func_key()
        template = self.prepare_template(
            destination_row, FuncKeyDestUser(user_id=destination_row.user_id)
        )

        template.keys[1].blf = False
        template.keys[1].label = 'mylabel'

        dao.edit(template)

        mapping = (
            self.session.query(FuncKeyMapping)
            .filter(FuncKeyMapping.template_id == template.id)
            .first()
        )

        assert_that(mapping.blf, equal_to(False))
        assert_that(mapping.label, equal_to('mylabel'))
        assert_that(mapping.position, equal_to(1))

    def test_given_destination_replaced_when_editing_then_replaces_destination(self):
        first_destination_row = self.create_user_func_key()
        updated_destination_row = self.create_queue_func_key()

        template = self.prepare_template(
            first_destination_row,
            FuncKeyDestUser(user_id=first_destination_row.user_id),
        )

        updated_destination = FuncKeyDestQueue(
            queue_id=updated_destination_row.queue_id
        )
        template.keys[1].destination = updated_destination

        dao.edit(template)

        mapping = (
            self.session.query(FuncKeyMapping)
            .filter(FuncKeyMapping.template_id == template.id)
            .first()
        )

        assert_that(mapping.func_key_id, equal_to(updated_destination_row.func_key_id))
        assert_that(
            mapping.destination_type_id,
            equal_to(updated_destination_row.destination_type_id),
        )
        assert_that(mapping.position, equal_to(1))

    def test_given_func_key_removed_when_editing_then_removes_func_key(self):
        destination_row = self.create_user_func_key()
        template = self.prepare_template(
            destination_row, FuncKeyDestUser(user_id=destination_row.user_id)
        )

        template.keys = {}

        dao.edit(template)

        self.assert_template_empty(template.id)


class TestSearch(TestDao):
    def assert_search_returns_result(self, search_result, **parameters):
        result = dao.search(**parameters)
        assert_that(result, equal_to(search_result))

    def test_given_no_templates_then_returns_empty_search_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_template_with_func_key_then_returns_one_result(self):
        destination_row = self.create_user_func_key()
        template = self.prepare_template(
            destination_row, FuncKeyDestUser(user_id=destination_row.user_id)
        )

        expected = SearchResult(1, [template])

        self.assert_search_returns_result(expected)

    def test_given_private_template_then_returns_empty_result(self):
        self.add_func_key_template(private=True)

        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_search_multi_tenant(self):
        tenant = self.add_tenant()

        template1 = self.add_func_key_template(name='a')
        template2 = self.add_func_key_template(name='b', tenant_uuid=tenant.uuid)

        expected = SearchResult(2, [template1, template2])
        tenants = [tenant.uuid, self.default_tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)

        expected = SearchResult(1, [template2])
        tenants = [tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)
