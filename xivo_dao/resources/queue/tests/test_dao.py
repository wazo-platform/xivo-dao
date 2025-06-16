# Copyright 2015-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    contains_exactly,
    empty,
    equal_to,
    has_items,
    has_properties,
    has_property,
    none,
    not_,
    not_none,
)
from sqlalchemy.inspection import inspect

from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.base_queue import BaseQueue
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.helpers.exception import InputError, NotFoundError
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as queue_dao


class TestFind(DAOTestCase):
    def test_find_no_queue(self):
        result = queue_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        queue_row = self.add_queuefeatures()

        queue = queue_dao.find(queue_row.id)

        assert_that(queue, equal_to(queue_row))

    def test_find_multi_tenant(self):
        tenant = self.add_tenant()

        queue = self.add_queuefeatures(tenant_uuid=tenant.uuid)

        result = queue_dao.find(queue.id, tenant_uuids=[tenant.uuid])
        assert_that(result, equal_to(queue))

        result = queue_dao.find(queue.id, tenant_uuids=[self.default_tenant.uuid])
        assert_that(result, none())


class TestGet(DAOTestCase):
    def test_get_no_queue(self):
        self.assertRaises(NotFoundError, queue_dao.get, 42)

    def test_get(self):
        queue_row = self.add_queuefeatures()

        queue = queue_dao.get(queue_row.id)

        assert_that(queue, equal_to(queue_row))

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()

        queue_row = self.add_queuefeatures(tenant_uuid=tenant.uuid)
        queue = queue_dao.get(queue_row.id, tenant_uuids=[tenant.uuid])
        assert_that(queue, equal_to(queue_row))

        queue_row = self.add_queuefeatures()
        self.assertRaises(
            NotFoundError, queue_dao.get, queue_row.id, tenant_uuids=[tenant.uuid]
        )


class TestFindBy(DAOTestCase):
    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, queue_dao.find_by, invalid=42)

    def test_find_by_name(self):
        queue_row = self.add_queuefeatures(name='myname')

        queue = queue_dao.find_by(name='myname')

        assert_that(queue, equal_to(queue_row))
        assert_that(queue.name, equal_to('myname'))

    def test_find_by_preprocess_subroutine(self):
        queue_row = self.add_queuefeatures(preprocess_subroutine='mysubroutine')

        queue = queue_dao.find_by(preprocess_subroutine='mysubroutine')

        assert_that(queue, equal_to(queue_row))
        assert_that(queue.preprocess_subroutine, equal_to('mysubroutine'))

    def test_given_queue_does_not_exist_then_returns_null(self):
        queue = queue_dao.find_by(id=42)

        assert_that(queue, none())

    def test_find_by_multi_tenant(self):
        tenant = self.add_tenant()

        queue_row = self.add_queuefeatures()
        queue = queue_dao.find_by(name=queue_row.name, tenant_uuids=[tenant.uuid])
        assert_that(queue, none())

        queue_row = self.add_queuefeatures(tenant_uuid=tenant.uuid)
        queue = queue_dao.find_by(name=queue_row.name, tenant_uuids=[tenant.uuid])
        assert_that(queue, equal_to(queue_row))


class TestGetBy(DAOTestCase):
    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, queue_dao.get_by, invalid=42)

    def test_get_by_name(self):
        queue_row = self.add_queuefeatures(name='myname')

        queue = queue_dao.get_by(name='myname')

        assert_that(queue, equal_to(queue_row))
        assert_that(queue.name, equal_to('myname'))

    def test_get_by_preprocess_subroutine(self):
        queue_row = self.add_queuefeatures(preprocess_subroutine='MySubroutine')

        queue = queue_dao.get_by(preprocess_subroutine='MySubroutine')

        assert_that(queue, equal_to(queue_row))
        assert_that(queue.preprocess_subroutine, equal_to('MySubroutine'))

    def test_given_queue_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, queue_dao.get_by, id='42')

    def test_get_by_multi_tenant(self):
        tenant = self.add_tenant()

        queue_row = self.add_queuefeatures()
        self.assertRaises(
            NotFoundError,
            queue_dao.get_by,
            id=queue_row.id,
            tenant_uuids=[tenant.uuid],
        )

        queue_row = self.add_queuefeatures(tenant_uuid=tenant.uuid)
        queue = queue_dao.get_by(id=queue_row.id, tenant_uuids=[tenant.uuid])
        assert_that(queue, equal_to(queue_row))


class TestFindAllBy(DAOTestCase):
    def test_find_all_by_no_queue(self):
        result = queue_dao.find_all_by(name='toto')

        assert_that(result, contains_exactly())

    def test_find_all_by_custom_column(self):
        pass

    def test_find_all_by_native_column(self):
        queue1 = self.add_queuefeatures(preprocess_subroutine='subroutine')
        queue2 = self.add_queuefeatures(preprocess_subroutine='subroutine')

        queues = queue_dao.find_all_by(preprocess_subroutine='subroutine')

        assert_that(
            queues,
            has_items(has_property('id', queue1.id), has_property('id', queue2.id)),
        )

    def test_find_all_multi_tenant(self):
        tenant = self.add_tenant()

        queue1 = self.add_queuefeatures(
            preprocess_subroutine='subroutine', tenant_uuid=tenant.uuid
        )
        queue2 = self.add_queuefeatures(preprocess_subroutine='subroutine')

        tenants = [tenant.uuid, self.default_tenant.uuid]
        queues = queue_dao.find_all_by(
            preprocess_subroutine='subroutine', tenant_uuids=tenants
        )
        assert_that(queues, has_items(queue1, queue2))

        tenants = [tenant.uuid]
        queues = queue_dao.find_all_by(
            preprocess_subroutine='subroutine', tenant_uuids=tenants
        )
        assert_that(queues, all_of(has_items(queue1), not_(has_items(queue2))))


class TestSearch(DAOTestCase):
    def assert_search_returns_result(self, search_result, **parameters):
        result = queue_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):
    def test_given_no_queue_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_queue_then_returns_one_result(self):
        queue = self.add_queuefeatures()
        expected = SearchResult(1, [queue])

        self.assert_search_returns_result(expected)

    def test_search_multi_tenant(self):
        tenant = self.add_tenant()

        queue1 = self.add_queuefeatures()
        queue2 = self.add_queuefeatures(tenant_uuid=tenant.uuid)

        expected = SearchResult(2, [queue1, queue2])
        tenants = [tenant.uuid, self.default_tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)

        expected = SearchResult(1, [queue2])
        tenants = [tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)


class TestSearchGivenMultipleQueue(TestSearch):
    def setUp(self):
        super(TestSearch, self).setUp()
        self.queue1 = self.add_queuefeatures(
            name='Ashton', preprocess_subroutine='resto'
        )
        self.queue2 = self.add_queuefeatures(
            name='Beaugarton', preprocess_subroutine='bar'
        )
        self.queue3 = self.add_queuefeatures(name='Casa', preprocess_subroutine='resto')
        self.queue4 = self.add_queuefeatures(
            name='Dunkin', preprocess_subroutine='resto'
        )

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.queue2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.queue1])
        self.assert_search_returns_result(
            expected_resto, search='ton', preprocess_subroutine='resto'
        )

        expected_bar = SearchResult(1, [self.queue2])
        self.assert_search_returns_result(
            expected_bar, search='ton', preprocess_subroutine='bar'
        )

        expected_all_resto = SearchResult(3, [self.queue1, self.queue3, self.queue4])
        self.assert_search_returns_result(
            expected_all_resto, preprocess_subroutine='resto', order='name'
        )

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4, [self.queue1, self.queue2, self.queue3, self.queue4])

        self.assert_search_returns_result(expected, order='name')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(
        self,
    ):
        expected = SearchResult(4, [self.queue4, self.queue3, self.queue2, self.queue1])

        self.assert_search_returns_result(expected, order='name', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.queue1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_offset_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.queue2, self.queue3, self.queue4])

        self.assert_search_returns_result(expected, offset=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.queue2])

        self.assert_search_returns_result(
            expected, search='a', order='name', direction='desc', offset=1, limit=1
        )


class TestCreate(DAOTestCase):
    def test_create_minimal_fields(self):
        queue = QueueFeatures(
            tenant_uuid=self.default_tenant.uuid, name='myqueue', label=None
        )
        created_queue = queue_dao.create(queue)

        row = self.session.query(QueueFeatures).first()

        assert_that(created_queue, equal_to(row))
        assert_that(
            created_queue,
            has_properties(
                id=not_none(),
                name='myqueue',
                caller_id_mode=None,
                caller_id_name=None,
                data_quality_bool=False,
                dtmf_hangup_callee_enabled=False,
                dtmf_hangup_caller_enabled=False,
                dtmf_transfer_callee_enabled=False,
                dtmf_transfer_caller_enabled=False,
                dtmf_record_callee_enabled=False,
                dtmf_record_caller_enabled=False,
                dtmf_record_toggle=False,
                retry_on_timeout=True,
                ring_on_hold=False,
                announce_hold_time_on_entry=False,
                ignore_forward_bool=True,
                wait_time_threshold=None,
                wait_ratio_threshold=None,
                timeout=None,
                preprocess_subroutine=None,
                enabled=True,
            ),
        )

    def test_create_with_all_fields(self):
        queue = QueueFeatures(
            tenant_uuid=self.default_tenant.uuid,
            name='MyQueue',
            label=None,
            caller_id_mode='prepend',
            caller_id_name='toto',
            data_quality_bool=True,
            dtmf_hangup_callee_enabled=True,
            dtmf_hangup_caller_enabled=True,
            dtmf_transfer_callee_enabled=True,
            dtmf_transfer_caller_enabled=True,
            dtmf_record_callee_enabled=True,
            dtmf_record_caller_enabled=True,
            dtmf_record_toggle=True,
            retry_on_timeout=False,
            ring_on_hold=True,
            announce_hold_time_on_entry=True,
            ignore_forward_bool=False,
            wait_time_threshold=1,
            wait_ratio_threshold=1.4,
            timeout=42,
            preprocess_subroutine='routine',
            enabled=False,
        )

        created_queue = queue_dao.create(queue)

        row = self.session.query(QueueFeatures).first()

        assert_that(created_queue, equal_to(row))
        assert_that(
            created_queue,
            has_properties(
                id=not_none(),
                name='MyQueue',
                caller_id_mode='prepend',
                caller_id_name='toto',
                data_quality_bool=True,
                dtmf_hangup_callee_enabled=True,
                dtmf_hangup_caller_enabled=True,
                dtmf_transfer_callee_enabled=True,
                dtmf_transfer_caller_enabled=True,
                dtmf_record_callee_enabled=True,
                dtmf_record_caller_enabled=True,
                dtmf_record_toggle=True,
                retry_on_timeout=False,
                ring_on_hold=True,
                announce_hold_time_on_entry=True,
                ignore_forward_bool=False,
                wait_time_threshold=1,
                wait_ratio_threshold=1.4,
                timeout=42,
                preprocess_subroutine='routine',
                enabled=False,
            ),
        )


class TestEdit(DAOTestCase):
    def test_edit_all_fields(self):
        queue = queue_dao.create(
            QueueFeatures(
                tenant_uuid=self.default_tenant.uuid,
                name='MyQueue',
                label=None,
                caller_id_mode='prepend',
                caller_id_name='toto',
                data_quality_bool=False,
                dtmf_hangup_callee_enabled=False,
                dtmf_hangup_caller_enabled=False,
                dtmf_transfer_callee_enabled=False,
                dtmf_transfer_caller_enabled=False,
                dtmf_record_callee_enabled=False,
                dtmf_record_caller_enabled=False,
                dtmf_record_toggle=False,
                retry_on_timeout=True,
                ring_on_hold=False,
                announce_hold_time_on_entry=False,
                ignore_forward_bool=True,
                wait_time_threshold=None,
                wait_ratio_threshold=None,
                timeout=None,
                preprocess_subroutine=None,
                enabled=True,
            )
        )

        queue = queue_dao.get(queue.id)
        queue.name = 'other_name'
        queue.label = 'other_label'
        queue.caller_id_mode = 'overwrite'
        queue.caller_id_name = 'bob'
        queue.enabled = False
        queue.data_quality_bool = True
        queue.dtmf_hangup_callee_enabled = True
        queue.dtmf_hangup_caller_enabled = True
        queue.dtmf_transfer_callee_enabled = True
        queue.dtmf_transfer_caller_enabled = True
        queue.dtmf_record_callee_enabled = True
        queue.dtmf_record_caller_enabled = True
        queue.dtmf_record_toggle = True
        queue.retry_on_timeout = False
        queue.ring_on_hold = True
        queue.announce_hold_time_on_entry = True
        queue.ignore_forward_bool = False
        queue.wait_time_threshold = 1
        queue.wait_ratio_threshold = 1.4
        queue.timeout = 42
        queue.preprocess_subroutine = 'routine'
        queue_dao.edit(queue)

        row = self.session.query(QueueFeatures).first()

        assert_that(queue, equal_to(row))
        assert_that(
            queue,
            has_properties(
                id=not_none(),
                name='other_name',
                label='other_label',
                caller_id_mode='overwrite',
                caller_id_name='bob',
                data_quality_bool=True,
                dtmf_hangup_callee_enabled=True,
                dtmf_hangup_caller_enabled=True,
                dtmf_transfer_callee_enabled=True,
                dtmf_transfer_caller_enabled=True,
                dtmf_record_callee_enabled=True,
                dtmf_record_caller_enabled=True,
                dtmf_record_toggle=True,
                retry_on_timeout=False,
                ring_on_hold=True,
                announce_hold_time_on_entry=True,
                ignore_forward_bool=False,
                wait_time_threshold=1,
                wait_ratio_threshold=1.4,
                timeout=42,
                preprocess_subroutine='routine',
                enabled=False,
            ),
        )

    def test_edit_set_fields_to_null(self):
        queue = queue_dao.create(
            QueueFeatures(
                tenant_uuid=self.default_tenant.uuid,
                name='MyQueue',
                label=None,
                caller_id_mode='prepend',
                caller_id_name='toto',
                wait_time_threshold=2,
                wait_ratio_threshold=42,
                timeout=3,
                preprocess_subroutine='t',
            )
        )

        queue = queue_dao.get(queue.id)
        queue.caller_id_mode = None
        queue.caller_id_name = None
        queue.wait_time_threshold = None
        queue.wait_ratio_threshold = None
        queue.timeout = None
        queue.preprocess_subroutine = None
        queue_dao.edit(queue)

        row = self.session.query(QueueFeatures).first()
        assert_that(queue, equal_to(row))
        assert_that(
            row,
            has_properties(
                preprocess_subroutine=none(),
                caller_id_mode=none(),
                caller_id_name=none(),
                wait_time_threshold=none(),
                wait_ratio_threshold=none(),
                timeout=none(),
            ),
        )

    def test_edit_queue_name(self):
        queue_dao.create(
            QueueFeatures(
                tenant_uuid=self.default_tenant.uuid,
                name='MyQueue',
                label=None,
            )
        )
        self.session.expunge_all()

        meta_queue = self.session.query(BaseQueue).first()
        assert_that(meta_queue.name, equal_to('MyQueue'))

        queue = self.session.query(QueueFeatures).first()
        queue.name = 'OtherName'
        queue_dao.edit(queue)

        meta_queue = self.session.query(BaseQueue).first()
        assert_that(meta_queue.name, equal_to('OtherName'))


class TestDelete(DAOTestCase):
    def test_delete(self):
        queue = self.add_queuefeatures()

        queue_dao.delete(queue)

        row = self.session.query(QueueFeatures).first()
        assert_that(row, none())

    def test_when_deleting_then_extension_are_dissociated(self):
        queue = self.add_queuefeatures()
        extension = self.add_extension(type='queue', typeval=str(queue.id))

        queue_dao.delete(queue)

        row = self.session.query(Extension).first()
        assert_that(row.id, equal_to(extension.id))
        assert_that(row, has_properties(type='user', typeval='0'))

    def test_when_deleting_then_contextmember_are_dissociated(self):
        queue = self.add_queuefeatures()
        context_member = self.add_context_member(type='queue', typeval=str(queue.id))

        queue_dao.delete(queue)

        assert_that(inspect(context_member).deleted)


class TestAssociateSchedule(DAOTestCase):
    def test_associate_schedule(self):
        queue = self.add_queuefeatures()
        schedule = self.add_schedule()

        queue_dao.associate_schedule(queue, schedule)

        self.session.expire_all()
        assert_that(queue.schedules, contains_exactly(schedule))
        assert_that(schedule.queues, contains_exactly(queue))

    def test_associate_already_associated(self):
        queue = self.add_queuefeatures()
        schedule = self.add_schedule()
        queue_dao.associate_schedule(queue, schedule)

        queue_dao.associate_schedule(queue, schedule)

        self.session.expire_all()
        assert_that(queue.schedules, contains_exactly(schedule))


class TestDissociateSchedule(DAOTestCase):
    def test_dissociate_queue_schedule(self):
        queue = self.add_queuefeatures()
        schedule = self.add_schedule()
        queue_dao.associate_schedule(queue, schedule)

        queue_dao.dissociate_schedule(queue, schedule)

        self.session.expire_all()
        assert_that(queue.schedules, empty())

    def test_dissociate_queue_schedule_not_associated(self):
        queue = self.add_queuefeatures()
        schedule = self.add_schedule()

        queue_dao.dissociate_schedule(queue, schedule)

        self.session.expire_all()
        assert_that(queue.schedules, empty())


class TestAssociateMemberUser(DAOTestCase):
    def test_associate(self):
        user = self.add_user()
        sip = self.add_endpoint_sip()
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        self.add_user_line(user_id=user.id, line_id=line.id)
        queue = self.add_queuefeatures()

        queue_dao.associate_member_user(queue, QueueMember(user=user))

        self.session.expire_all()
        assert_that(
            queue.user_queue_members,
            contains_exactly(
                has_properties(
                    queue_name=queue.name,
                    category='queue',
                    usertype='user',
                    userid=user.id,
                )
            ),
        )

    def test_associate_fix(self):
        user = self.add_user()
        sip = self.add_endpoint_sip(name='sipname')
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        self.add_user_line(user_id=user.id, line_id=line.id)
        queue = self.add_queuefeatures()

        queue_dao.associate_member_user(queue, QueueMember(user=user))

        self.session.expire_all()
        assert_that(
            queue.user_queue_members,
            contains_exactly(
                has_properties(
                    interface='PJSIP/sipname',
                    channel='SIP',
                )
            ),
        )

    def test_association_already_associated(self):
        user = self.add_user()
        sip = self.add_endpoint_sip()
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        self.add_user_line(user_id=user.id, line_id=line.id)
        queue = self.add_queuefeatures()
        queue_member = QueueMember(user=user)

        queue_dao.associate_member_user(queue, queue_member)

        self.session.expire_all()
        queue_dao.associate_member_user(queue, queue_member)

        self.session.expire_all()
        assert_that(queue.user_queue_members, contains_exactly(queue_member))


class TestDissociateMemberUser(DAOTestCase):
    def test_dissociation(self):
        user = self.add_user()
        sip = self.add_endpoint_sip(name='sipname')
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        self.add_user_line(user_id=user.id, line_id=line.id)
        queue = self.add_queuefeatures()
        queue_member = QueueMember(user=user)
        queue_dao.associate_member_user(queue, queue_member)

        self.session.expire_all()
        queue_dao.dissociate_member_user(queue, queue_member)

        self.session.expire_all()
        assert_that(queue.user_queue_members, empty())

        row = self.session.query(UserFeatures).first()
        assert_that(row, not_none())

        row = self.session.query(QueueMember).first()
        assert_that(row, none())


class TestAssociateMemberAgent(DAOTestCase):
    def test_associate(self):
        agent = self.add_agent()
        queue = self.add_queuefeatures()

        queue_dao.associate_member_agent(queue, QueueMember(agent=agent))

        self.session.expire_all()
        assert_that(
            queue.agent_queue_members,
            contains_exactly(
                has_properties(
                    queue_name=queue.name,
                    category='queue',
                    usertype='agent',
                    userid=agent.id,
                )
            ),
        )

    def test_associate_fix(self):
        agent = self.add_agent(number='1234')
        queue = self.add_queuefeatures()

        queue_dao.associate_member_agent(queue, QueueMember(agent=agent))

        self.session.expire_all()
        assert_that(
            queue.agent_queue_members,
            contains_exactly(
                has_properties(
                    interface='Agent/1234',
                    channel='Agent',
                )
            ),
        )

    def test_association_already_associated(self):
        agent = self.add_agent()
        queue = self.add_queuefeatures()
        queue_member = QueueMember(agent=agent)

        queue_dao.associate_member_agent(queue, queue_member)

        self.session.expire_all()
        queue_dao.associate_member_agent(queue, queue_member)

        self.session.expire_all()
        assert_that(queue.agent_queue_members, contains_exactly(queue_member))


class TestDissociateMemberAgent(DAOTestCase):
    def test_dissociation(self):
        agent = self.add_agent()
        queue = self.add_queuefeatures()
        queue_member = QueueMember(agent=agent)
        queue_dao.associate_member_agent(queue, queue_member)

        self.session.expire_all()
        queue_dao.dissociate_member_agent(queue, queue_member)

        self.session.expire_all()
        assert_that(queue.agent_queue_members, empty())

        row = self.session.query(AgentFeatures).first()
        assert_that(row, not_none())

        row = self.session.query(QueueMember).first()
        assert_that(row, none())
