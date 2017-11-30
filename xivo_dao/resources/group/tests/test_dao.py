# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (assert_that,
                      contains,
                      empty,
                      equal_to,
                      has_items,
                      has_properties,
                      has_property,
                      is_not,
                      none,
                      not_)

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.groupfeatures import GroupFeatures as Group
from xivo_dao.alchemy.queue import Queue
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.rightcall import RightCall
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.alchemy.schedule import Schedule
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.resources.group import dao as group_dao
from xivo_dao.helpers.exception import NotFoundError, InputError
from xivo_dao.resources.utils.search import SearchResult


class TestFind(DAOTestCase):

    def test_find_no_group(self):
        result = group_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        group_row = self.add_group()

        group = group_dao.find(group_row.id)

        assert_that(group, equal_to(group_row))


class TestGet(DAOTestCase):

    def test_get_no_group(self):
        self.assertRaises(NotFoundError, group_dao.get, 42)

    def test_get(self):
        group_row = self.add_group()

        group = group_dao.get(group_row.id)

        assert_that(group, equal_to(group_row))


class TestFindBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, group_dao.find_by, invalid=42)

    def test_find_by_name(self):
        group_row = self.add_group(name='myname')

        group = group_dao.find_by(name='myname')

        assert_that(group, equal_to(group_row))
        assert_that(group.name, equal_to('myname'))

    def test_find_by_preprocess_subroutine(self):
        group_row = self.add_group(preprocess_subroutine='mysubroutine')

        group = group_dao.find_by(preprocess_subroutine='mysubroutine')

        assert_that(group, equal_to(group_row))
        assert_that(group.preprocess_subroutine, equal_to('mysubroutine'))

    def test_given_group_does_not_exist_then_returns_null(self):
        group = group_dao.find_by(id=42)

        assert_that(group, none())


class TestGetBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, group_dao.get_by, invalid=42)

    def test_get_by_name(self):
        group_row = self.add_group(name='myname')

        group = group_dao.get_by(name='myname')

        assert_that(group, equal_to(group_row))
        assert_that(group.name, equal_to('myname'))

    def test_get_by_preprocess_subroutine(self):
        group_row = self.add_group(preprocess_subroutine='MySubroutine')

        group = group_dao.get_by(preprocess_subroutine='MySubroutine')

        assert_that(group, equal_to(group_row))
        assert_that(group.preprocess_subroutine, equal_to('MySubroutine'))

    def test_given_group_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, group_dao.get_by, id='42')


class TestFindAllBy(DAOTestCase):

    def test_find_all_by_no_group(self):
        result = group_dao.find_all_by(name='toto')

        assert_that(result, contains())

    def test_find_all_by_custom_column(self):
        pass

    def test_find_all_by_native_column(self):
        group1 = self.add_group(preprocess_subroutine='subroutine')
        group2 = self.add_group(preprocess_subroutine='subroutine')

        groups = group_dao.find_all_by(preprocess_subroutine='subroutine')

        assert_that(groups, has_items(has_property('id', group1.id),
                                      has_property('id', group2.id)))


class TestSearch(DAOTestCase):

    def assert_search_returns_result(self, search_result, **parameters):
        result = group_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_given_no_group_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_group_then_returns_one_result(self):
        group = self.add_group()
        expected = SearchResult(1, [group])

        self.assert_search_returns_result(expected)


class TestSearchGivenMultipleGroup(TestSearch):

    def setUp(self):
        super(TestSearch, self).setUp()
        self.group1 = self.add_group(name='Ashton', preprocess_subroutine='resto')
        self.group2 = self.add_group(name='Beaugarton', preprocess_subroutine='bar')
        self.group3 = self.add_group(name='Casa', preprocess_subroutine='resto')
        self.group4 = self.add_group(name='Dunkin', preprocess_subroutine='resto')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.group2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.group1])
        self.assert_search_returns_result(expected_resto, search='ton', preprocess_subroutine='resto')

        expected_bar = SearchResult(1, [self.group2])
        self.assert_search_returns_result(expected_bar, search='ton', preprocess_subroutine='bar')

        expected_all_resto = SearchResult(3, [self.group1, self.group3, self.group4])
        self.assert_search_returns_result(expected_all_resto, preprocess_subroutine='resto', order='name')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4,
                                [self.group1,
                                 self.group2,
                                 self.group3,
                                 self.group4])

        self.assert_search_returns_result(expected, order='name')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(4, [self.group4,
                                    self.group3,
                                    self.group2,
                                    self.group1])

        self.assert_search_returns_result(expected, order='name', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.group1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_skipping_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.group2, self.group3, self.group4])

        self.assert_search_returns_result(expected, skip=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.group2])

        self.assert_search_returns_result(expected,
                                          search='a',
                                          order='name',
                                          direction='desc',
                                          skip=1,
                                          limit=1)


class TestCreate(DAOTestCase):

    def test_create_minimal_fields(self):
        group = Group(name='mygroup')
        created_group = group_dao.create(group)

        row = self.session.query(Group).first()

        assert_that(created_group, equal_to(row))
        assert_that(created_group, has_properties(id=is_not(none()),
                                                  name='mygroup',
                                                  caller_id_mode=none(),
                                                  caller_id_name=none(),
                                                  timeout=none(),
                                                  music_on_hold=none(),
                                                  preprocess_subroutine=none(),
                                                  ring_in_use=True,
                                                  ring_strategy='ringall',
                                                  user_timeout=15,
                                                  retry_delay=5,
                                                  enabled=True))

    def test_create_with_all_fields(self):
        group = Group(name='MyGroup',
                      caller_id_mode='prepend',
                      caller_id_name='toto',
                      timeout=60,
                      music_on_hold='default',
                      preprocess_subroutine='tata',
                      ring_in_use=False,
                      ring_strategy='random',
                      user_timeout=0,
                      retry_delay=0,
                      enabled=False)

        created_group = group_dao.create(group)

        row = self.session.query(Group).first()

        assert_that(created_group, equal_to(row))
        assert_that(created_group, has_properties(id=is_not(none()),
                                                  name='MyGroup',
                                                  caller_id_mode='prepend',
                                                  caller_id_name='toto',
                                                  timeout=60,
                                                  music_on_hold='default',
                                                  preprocess_subroutine='tata',
                                                  ring_in_use=False,
                                                  ring_strategy='random',
                                                  user_timeout=0,
                                                  retry_delay=0,
                                                  enabled=False))


class TestEdit(DAOTestCase):

    def test_edit_all_fields(self):
        group = group_dao.create(Group(name='MyGroup',
                                       caller_id_mode='prepend',
                                       caller_id_name='toto',
                                       timeout=60,
                                       music_on_hold='default',
                                       preprocess_subroutine='tata',
                                       ring_in_use=True,
                                       ring_strategy='ringall',
                                       user_timeout=0,
                                       retry_delay=0,
                                       enabled=True))

        group = group_dao.get(group.id)
        group.name = 'other_name'
        group.caller_id_mode = 'overwrite'
        group.caller_id_name = 'bob'
        group.timeout = 5
        group.music_on_hold = 'not_default'
        group.preprocess_subroutine = 'other_routine'
        group.ring_in_use = False
        group.ring_strategy = 'random'
        group.user_timeout = 180
        group.retry_delay = 1
        group.enabled = False
        group_dao.edit(group)

        row = self.session.query(Group).first()

        assert_that(group, equal_to(row))
        assert_that(group, has_properties(id=is_not(none()),
                                          name='other_name',
                                          caller_id_mode='overwrite',
                                          caller_id_name='bob',
                                          timeout=5,
                                          music_on_hold='not_default',
                                          preprocess_subroutine='other_routine',
                                          ring_in_use=False,
                                          ring_strategy='random',
                                          user_timeout=180,
                                          retry_delay=1,
                                          enabled=False))

    def test_edit_set_fields_to_null(self):
        group = group_dao.create(Group(name='MyGroup',
                                       caller_id_mode='prepend',
                                       caller_id_name='toto',
                                       timeout=0,
                                       music_on_hold='default',
                                       preprocess_subroutine='t',
                                       user_timeout=0,
                                       retry_delay=0))

        group = group_dao.get(group.id)
        group.caller_id_mode = None
        group.caller_id_name = None
        group.timeout = None
        group.music_on_hold = None
        group.preprocess_subroutine = None
        group.user_timeout = None
        group.retry_delay = None

        group_dao.edit(group)

        row = self.session.query(Group).first()
        assert_that(group, equal_to(row))
        assert_that(row, has_properties(timeout=none(),
                                        music_on_hold=none(),
                                        caller_id_mode=none(),
                                        caller_id_name=none(),
                                        preprocess_subroutine=none(),
                                        user_timeout=none(),
                                        retry_delay=none()))

    def test_edit_queue_name(self):
        group_dao.create(Group(name='MyGroup'))
        self.session.expunge_all()

        queue = self.session.query(Queue).first()
        assert_that(queue.name, equal_to('MyGroup'))

        group = self.session.query(Group).first()
        group.name = 'OtherName'
        group_dao.edit(group)

        queue = self.session.query(Queue).first()
        assert_that(queue.name, equal_to('OtherName'))


class TestDelete(DAOTestCase):

    def test_delete(self):
        group = self.add_group()

        group_dao.delete(group)

        row = self.session.query(Group).first()
        assert_that(row, none())

    def test_when_deleting_then_extension_are_dissociated(self):
        group = self.add_group()
        extension = self.add_extension(type='group', typeval=str(group.id))

        group_dao.delete(group)

        row = self.session.query(Extension).first()
        assert_that(row.id, equal_to(extension.id))
        assert_that(row, has_properties(type='user', typeval='0'))

    def test_when_deleting_then_call_permission_are_dissociated(self):
        group = self.add_group()
        call_permission = self.add_call_permission()
        self.add_group_call_permission(typeval=str(group.id))

        group_dao.delete(group)

        group_call_permission = self.session.query(RightCallMember).first()
        assert_that(group_call_permission, none())

        row = self.session.query(RightCall).first()
        assert_that(row.id, equal_to(call_permission.id))

    def test_when_deleting_then_schedule_are_dissociated(self):
        group = self.add_group()
        schedule = self.add_schedule()
        self.add_group_schedule(schedule_id=schedule.id, pathid=group.id)

        group_dao.delete(group)

        group_schedule = self.session.query(SchedulePath).first()
        assert_that(group_schedule, none())

        row = self.session.query(Schedule).first()
        assert_that(row.id, equal_to(schedule.id))

    def test_when_deleting_then_dialactions_are_unlinked(self):
        group = self.add_group()
        self.add_dialaction(action='group', actionarg1=str(group.id), linked=1)

        group_dao.delete(group)

        dialaction = self.session.query(Dialaction).filter(Dialaction.actionarg1 == str(group.id)).first()
        assert_that(dialaction, has_properties(linked=0))


class TestAssociateMemberUsers(DAOTestCase):

    def test_associate_user_sip(self):
        user = self.add_user()
        sip = self.add_usersip(name='sipname')
        line = self.add_line(protocol='sip', protocolid=sip.id)
        self.add_user_line(user_id=user.id, line_id=line.id)
        group_row = self.add_group()

        group_dao.associate_all_member_users(group_row, [{'user': user}])

        group = self.session.query(Group).first()
        assert_that(group, equal_to(group_row))
        assert_that(group.group_members, contains(
            has_properties(queue_name=group.name,
                           interface='SIP/sipname',
                           channel='SIP',
                           user=has_properties(id=user.id,
                                               firstname=user.firstname,
                                               lastname=user.lastname))
        ))

    def test_associate_multiple_users(self):
        group_row = self.add_group()

        user1 = self.add_user()
        sip1 = self.add_usersip()
        line1 = self.add_line(protocol='sip', protocolid=sip1.id)
        self.add_user_line(user_id=user1.id, line_id=line1.id)

        user2 = self.add_user()
        sip2 = self.add_sccpline()
        line2 = self.add_line(protocol='sccp', protocolid=sip2.id)
        self.add_user_line(user_id=user2.id, line_id=line2.id)

        user3 = self.add_user()
        sip3 = self.add_usercustom()
        line3 = self.add_line(protocol='custom', protocolid=sip3.id)
        self.add_user_line(user_id=user3.id, line_id=line3.id)
        members = [{'user': user1, 'priority': 3},
                   {'user': user2, 'priority': 1},
                   {'user': user3, 'priority': 2}]

        group_dao.associate_all_member_users(group_row, members)

        self.session.expire_all()
        group = self.session.query(Group).first()
        assert_that(group, equal_to(group_row))
        assert_that(group.users_member, contains(user2, user3, user1))

    def test_associate_sip_fix(self):
        user = self.add_user()
        sip = self.add_usersip(name='sipname')
        line = self.add_line(protocol='sip', protocolid=sip.id)
        self.add_user_line(user_id=user.id, line_id=line.id)
        group_row = self.add_group()

        group_dao.associate_all_member_users(group_row, [{'user': user}])

        group = self.session.query(Group).first()
        assert_that(group.group_members, contains(
            has_properties(queue_name=group.name,
                           interface='SIP/sipname',
                           channel='SIP')
        ))

    def test_associate_sccp_fix(self):
        user = self.add_user()
        sccp = self.add_sccpline(name='sccpname')
        line = self.add_line(protocol='sccp', protocolid=sccp.id)
        self.add_user_line(user_id=user.id, line_id=line.id)
        group_row = self.add_group()

        group_dao.associate_all_member_users(group_row, [{'user': user}])

        group = self.session.query(Group).first()
        assert_that(group.group_members, contains(
            has_properties(queue_name=group.name,
                           interface='SCCP/sccpname',
                           channel='SCCP')
        ))

    def test_associate_custom_fix(self):
        user = self.add_user()
        custom = self.add_usercustom(interface='custom/interface')
        line = self.add_line(protocol='custom', protocolid=custom.id)
        self.add_user_line(user_id=user.id, line_id=line.id)
        group_row = self.add_group()

        group_dao.associate_all_member_users(group_row, [{'user': user}])

        group = self.session.query(Group).first()
        assert_that(group.group_members, contains(
            has_properties(queue_name=group.name,
                           interface='custom/interface',
                           channel='**Unknown**')
        ))

    def test_users_dissociation(self):
        user = self.add_user()
        sip = self.add_usersip(name='sipname')
        line = self.add_line(protocol='sip', protocolid=sip.id)
        self.add_user_line(user_id=user.id, line_id=line.id)
        group_row = self.add_group()
        group_dao.associate_all_member_users(group_row, [{'user': user}])

        group = self.session.query(Group).first()
        assert_that(group.users_member, contains(user))

        group_dao.associate_all_member_users(group_row, [])

        group = self.session.query(Group).first()
        assert_that(group, equal_to(group_row))
        assert_that(group.users_member, empty())

        row = self.session.query(UserFeatures).first()
        assert_that(row, not_(none()))

        row = self.session.query(QueueMember).first()
        assert_that(row, none())


class TestAssociateMemberExtensions(DAOTestCase):

    def test_associate_extension_sip(self):
        group_row = self.add_group()
        extension = {'exten': '123', 'context': 'default'}

        group_dao.associate_all_member_extensions(group_row, [{'extension': extension}])

        group = self.session.query(Group).first()
        assert_that(group, equal_to(group_row))
        assert_that(group.group_members, contains(
            has_properties(queue_name=group.name,
                           interface='Local/123@default',
                           channel='Local',
                           usertype='user',
                           userid=0)
        ))

    def test_associate_multiple_extensions(self):
        group_row = self.add_group()

        extension1 = {'exten': '123', 'context': 'default'}
        extension2 = {'exten': '456', 'context': 'outcall'}
        extension3 = {'exten': '789', 'context': 'default'}

        members = [{'extension': extension1, 'priority': 3},
                   {'extension': extension2, 'priority': 1},
                   {'extension': extension3, 'priority': 2}]

        group_dao.associate_all_member_extensions(group_row, members)

        self.session.expire_all()
        group = self.session.query(Group).first()
        assert_that(group, equal_to(group_row))
        assert_that(group.extensions_member, contains(has_properties(interface='Local/456@outcall'),
                                                      has_properties(interface='Local/789@default'),
                                                      has_properties(interface='Local/123@default')))

    def test_extensions_dissociation(self):
        group_row = self.add_group()
        extension = {'exten': '123', 'context': 'default'}
        group_dao.associate_all_member_extensions(group_row, [{'extension': extension}])

        group = self.session.query(Group).first()
        assert_that(group.extensions_member, contains(has_properties(interface='Local/123@default')))

        group_dao.associate_all_member_extensions(group_row, [])

        group = self.session.query(Group).first()
        assert_that(group, equal_to(group_row))
        assert_that(group.extensions_member, empty())

        row = self.session.query(QueueMember).first()
        assert_that(row, none())


class TestAssociateCallPermission(DAOTestCase):

    def test_associate_call_permission(self):
        group = self.add_group()
        call_permission = self.add_call_permission()

        result = group_dao.associate_call_permission(group, call_permission)

        result = self.session.query(Group).first()
        assert_that(result, equal_to(group))
        assert_that(result.call_permissions, contains(call_permission))

        result = self.session.query(RightCall).first()
        assert_that(result, equal_to(call_permission))
        assert_that(result.groups, contains(group))

    def test_associate_group_call_permission_already_associated(self):
        group = self.add_group()
        call_permission = self.add_call_permission()
        group_dao.associate_call_permission(group, call_permission)

        result = group_dao.associate_call_permission(group, call_permission)

        result = self.session.query(Group).first()
        assert_that(result, equal_to(group))
        assert_that(result.call_permissions, contains(call_permission))

        result = self.session.query(RightCall).first()
        assert_that(result, equal_to(call_permission))
        assert_that(result.groups, contains(group))


class TestDissociateCallPermission(DAOTestCase):

    def test_dissociate_group_call_permission(self):
        group = self.add_group()
        call_permission = self.add_call_permission()
        group_dao.associate_call_permission(group, call_permission)

        group_dao.dissociate_call_permission(group, call_permission)

        result = self.session.query(Group).first()
        assert_that(result, equal_to(group))
        assert_that(result.call_permissions, empty())

    def test_dissociate_group_call_permission_not_associated(self):
        group = self.add_group()
        call_permission = self.add_call_permission()

        group_dao.dissociate_call_permission(group, call_permission)

        result = self.session.query(Group).first()
        assert_that(result, equal_to(group))
        assert_that(result.call_permissions, empty())
