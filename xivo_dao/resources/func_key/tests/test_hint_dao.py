# -*- coding: utf-8 -*-
# Copyright 2014-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import six

from itertools import permutations

from hamcrest import (
    any_of,
    assert_that,
    contains,
    contains_inanyorder,
    empty,
    equal_to,
)
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.helpers.wrap_matcher import wrap_matcher

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.resources.func_key.tests.test_helpers import FuncKeyHelper
from xivo_dao.resources.func_key import hint_dao
from xivo_dao.resources.func_key.model import Hint


class HintMatcher(BaseMatcher):

    def __init__(self, user_id, extension, argument_matcher):
        self._user_id = user_id
        self._extension = extension
        self._argument_matcher = argument_matcher

    def _matches(self, item):
        return (
            item.user_id == self._user_id and
            item.extension == self._extension and
            self._argument_matcher.matches(item.argument),
        )

    def describe_to(self, description):
        (description.append_text('hint with user_id ')
                    .append_description_of(self._user_id)
                    .append_text(' extension ')
                    .append_description_of(self._extension)
                    .append_text(' argument ')
                    .append_description_of(self._argument_matcher))


def a_hint(user_id, extension, argument):
    if isinstance(argument, six.string_types) and '&' in argument:
        argument_matcher = any_of(*list(map('&'.join, permutations(argument.split('&')))))
    else:
        argument_matcher = wrap_matcher(argument)
    return HintMatcher(user_id, extension, argument_matcher)


class TestProgfunckeyExtension(DAOTestCase):

    def test_given_progfunc_key_extension_then_returns_cleaned_progfunckey(self):
        self.add_extension(
            context='xivo-features',
            exten='_*735.',
            type='extenfeatures',
            typeval='phoneprogfunckey',
        )

        assert_that(hint_dao.progfunckey_extension(), equal_to('*735'))


class TestCalluserExtension(DAOTestCase):

    def test_given_calluser_extension_then_returns_cleaned_calluser(self):
        self.add_extension(
            context='xivo-features',
            exten='_*666.',
            type='extenfeatures',
            typeval='calluser',
        )

        assert_that(hint_dao.calluser_extension(), equal_to('*666'))


class TestHints(DAOTestCase, FuncKeyHelper):

    def setUp(self):
        super(TestHints, self).setUp()
        self.setup_funckeys()
        self.context = self.add_context(name='mycontext')
        self.context2 = self.add_context(name='mycontext2')

    def add_user_and_func_key(
        self, endpoint_sip_uuid=None, exten='1000', commented=0, enablehint=1,
    ):
        return self.add_user_sip_and_func_key(endpoint_sip_uuid, exten, commented, enablehint)

    def add_user_sip_and_func_key(
        self, endpoint_sip_uuid=None, exten='1000', commented=0, enablehint=1,
    ):
        if not endpoint_sip_uuid:
            endpoint_sip_uuid = self.add_endpoint_sip().uuid
        line = self.add_line(
            context=self.context.name,
            endpoint_sip_uuid=endpoint_sip_uuid,
            commented=commented
        )
        user_row = self._add_user_line_extension(line.id, exten, commented, enablehint)
        self.add_user_destination(user_row.id)

        return user_row

    def add_user_sccp_and_func_key(self, endpoint_sccp_id=None, exten='1000', commented=0, enablehint=1):
        if not endpoint_sccp_id:
            endpoint_sccp_id = self.add_sccpline().id
        line = self.add_line(
            context=self.context.name,
            endpoint_sccp_id=endpoint_sccp_id,
            commented=commented
        )
        user_row = self._add_user_line_extension(line.id, exten, commented, enablehint)
        self.add_user_destination(user_row.id)

        return user_row

    def add_user_custom_and_func_key(self, endpoint_custom_id=None, exten='1000', commented=0, enablehint=1):
        if not endpoint_custom_id:
            endpoint_custom_id = self.add_usercustom().id
        line = self.add_line(
            context=self.context.name,
            endpoint_custom_id=endpoint_custom_id,
            commented=commented
        )
        user_row = self._add_user_line_extension(line.id, exten, commented, enablehint)
        self.add_user_destination(user_row.id)

        return user_row

    def _add_user_line_extension(self, line_id, exten, commented=0, enablehint=1):
        user_row = self.add_user(enablehint=enablehint)
        extension_row = self.add_extension(exten=exten, context=self.context.name)

        self.add_user_line(
            user_id=user_row.id,
            line_id=line_id,
            main_user=True,
            main_line=True,
        )
        self.add_line_extension(
            line_id=line_id,
            extension_id=extension_row.id,
            main_extension=True,
        )
        return user_row

    def add_sip_line_to_extension_and_user(self, name, user_id, extension_id, main_line=True):
        sip = self.add_endpoint_sip(name=name)
        line = self.add_line(context=self.context.name, endpoint_sip_uuid=sip.uuid)
        self.add_user_line(user_id=user_id, line_id=line.id, main_user=True, main_line=main_line)
        self.add_line_extension(line_id=line.id, extension_id=extension_id, main_extension=True)


class TestUserHints(TestHints):

    def test_given_user_with_sip_line_then_returns_user_hint(self):
        endpoint_sip_row = self.add_endpoint_sip(name='abcdef')
        user_row = self.add_user_sip_and_func_key(endpoint_sip_row.uuid)

        assert_that(hint_dao.user_hints(self.context.name), contains(
            a_hint(user_id=user_row.id, extension='1000', argument='SIP/abcdef'),
        ))

    def test_given_user_with_sccp_line_then_returns_user_hint(self):
        sccpline_row = self.add_sccpline(name='1001', context=self.context.name)
        user_row = self.add_user_sccp_and_func_key(sccpline_row.id, '1001')

        assert_that(hint_dao.user_hints(self.context.name), contains(
            a_hint(user_id=user_row.id, extension='1001', argument='SCCP/1001'),
        ))

    def test_given_user_with_custom_line_then_returns_user_hint(self):
        custom_row = self.add_usercustom(interface='ghijkl', context=self.context.name)
        user_row = self.add_user_custom_and_func_key(custom_row.id, '1002')

        assert_that(hint_dao.user_hints(self.context.name), contains(
            a_hint(user_id=user_row.id, extension='1002', argument='ghijkl'),
        ))

    def test_given_user_with_commented_line_then_returns_empty_list(self):
        self.add_user_and_func_key(exten='1002', commented=1)

        assert_that(hint_dao.user_hints(self.context.name), empty())

    def test_given_user_with_hints_disabled_then_returns_empty_list(self):
        self.add_user_and_func_key(exten='1003', enablehint=0)

        assert_that(hint_dao.user_hints(self.context.name), empty())

    def test_given_user_when_querying_different_context_then_returns_empty_list(self):
        self.add_user_and_func_key(exten='1004')

        assert_that(hint_dao.user_hints('othercontext'), empty())

    def test_given_two_users_with_sip_line_then_returns_only_two_hints(self):
        user1 = self.add_user_and_func_key(self.add_endpoint_sip(name='user1').uuid, '1001')
        user2 = self.add_user_and_func_key(self.add_endpoint_sip(name='user2').uuid, '1002')

        assert_that(hint_dao.user_hints(self.context.name), contains_inanyorder(
            a_hint(user_id=user1.id, extension='1001', argument='SIP/user1'),
            a_hint(user_id=user2.id, extension='1002', argument='SIP/user2'),
        ))

    def test_given_one_user_two_lines_one_extension_then_returns_user_hint(self):
        user = self.add_user(enablehint=1)
        extension = self.add_extension(exten='1001', context=self.context.name)
        self.add_user_destination(user.id)
        self.add_sip_line_to_extension_and_user('line1', user.id, extension.id)
        self.add_sip_line_to_extension_and_user('line2', user.id, extension.id, main_line=False)

        assert_that(hint_dao.user_hints(self.context.name), contains(
            a_hint(user_id=user.id, extension='1001', argument='SIP/line1&SIP/line2'),
        ))

    def test_given_one_user_two_lines_two_extensions_then_returns_user_hint(self):
        user = self.add_user(enablehint=1)
        extension1 = self.add_extension(exten='1001', context=self.context.name)
        extension2 = self.add_extension(exten='1002', context=self.context.name)
        self.add_user_destination(user.id)
        self.add_sip_line_to_extension_and_user('line1', user.id, extension1.id)
        self.add_sip_line_to_extension_and_user('line2', user.id, extension2.id, main_line=False)

        assert_that(hint_dao.user_hints(self.context.name), contains_inanyorder(
            a_hint(user_id=user.id, extension='1001', argument='SIP/line1&SIP/line2'),
            a_hint(user_id=user.id, extension='1002', argument='SIP/line1&SIP/line2'),
        ))

    def test_given_one_user_two_lines_two_extensions_two_contexts_then_returns_user_hint(self):
        user = self.add_user(enablehint=1)
        extension1 = self.add_extension(exten='1001', context=self.context.name)
        extension2 = self.add_extension(exten='1002', context=self.context2.name)
        self.add_user_destination(user.id)
        self.add_sip_line_to_extension_and_user('line1', user.id, extension1.id)
        self.add_sip_line_to_extension_and_user('line2', user.id, extension2.id, main_line=False)

        assert_that(hint_dao.user_hints(self.context.name), contains(
            a_hint(user_id=user.id, extension='1001', argument='SIP/line1&SIP/line2'),
        ))

    def test_given_one_user_three_lines_two_extensions_then_returns_user_hint(self):
        user = self.add_user(enablehint=1)
        extension1 = self.add_extension(exten='1001', context=self.context.name)
        extension2 = self.add_extension(exten='1002', context=self.context.name)
        self.add_user_destination(user.id)
        self.add_sip_line_to_extension_and_user('line1', user.id, extension1.id)
        self.add_sip_line_to_extension_and_user('line2', user.id, extension2.id, main_line=False)
        self.add_sip_line_to_extension_and_user('line3', user.id, extension2.id, main_line=False)

        assert_that(hint_dao.user_hints(self.context.name), contains_inanyorder(
            a_hint(user_id=user.id, extension='1001', argument='SIP/line1&SIP/line2&SIP/line3'),
            a_hint(user_id=user.id, extension='1002', argument='SIP/line1&SIP/line2&SIP/line3'),
        ))


class TestConferenceHints(TestHints):

    def prepare_conference(self, commented=0):
        conf_row = self.add_meetmefeatures(commented=commented)
        self.add_extension(
            context=self.context.name,
            exten=conf_row.confno,
            type='meetme',
            typeval=str(conf_row.id),
        )
        return conf_row

    def test_given_conference_then_returns_conference_hint(self):
        conf_row = self.prepare_conference()
        self.add_conference_destination(conf_row.id)

        assert_that(hint_dao.conference_hints(self.context.name), contains(
            Hint(user_id=None, extension=conf_row.confno, argument=None),
        ))

    def test_given_commented_conference_then_returns_no_hints(self):
        conf_row = self.prepare_conference(commented=1)
        self.add_conference_destination(conf_row.id)

        assert_that(hint_dao.conference_hints(self.context.name), empty())

    def test_given_conference_when_querying_different_context_then_returns_no_hints(self):
        conf_row = self.prepare_conference()
        self.add_conference_destination(conf_row.id)

        assert_that(hint_dao.conference_hints('othercontext'), empty())


class TestServiceHints(TestHints):

    def test_given_service_func_key_then_returns_service_hint(self):
        destination_row = self.create_service_func_key('*25', 'enablednd')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        assert_that(hint_dao.service_hints(self.context.name), contains(
            Hint(user_id=user_row.id, extension='*25', argument=None),
        ))

    def test_given_commented_extension_then_returns_no_hints(self):
        destination_row = self.create_service_func_key('*25', 'enablednd', commented=1)

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        assert_that(hint_dao.service_hints(self.context.name), empty())

    def test_given_no_blf_then_returns_no_hints(self):
        destination_row = self.create_service_func_key('*25', 'enablednd')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row, blf=False)

        assert_that(hint_dao.service_hints(self.context.name), empty())

    def test_given_user_when_query_different_context_then_returns_no_hints(self):
        destination_row = self.create_service_func_key('*25', 'enablednd')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row, blf=False)

        assert_that(hint_dao.service_hints('othercontext'), empty())


class TestForwardHints(TestHints):

    def test_given_forward_func_key_then_returns_forward_hint(self):
        destination_row = self.create_forward_func_key('_*23.', 'fwdbusy', '1234')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        assert_that(hint_dao.forward_hints(self.context.name), contains(
            Hint(user_id=user_row.id, extension='*23', argument='1234'),
        ))

    def test_given_forward_without_number_then_returns_forward_hint(self):
        destination_row = self.create_forward_func_key('_*23.', 'fwdbusy')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        assert_that(hint_dao.forward_hints(self.context.name), contains(
            Hint(user_id=user_row.id, extension='*23', argument=None),
        ))

    def test_given_commented_extension_then_returns_no_hints(self):
        destination_row = self.create_forward_func_key('_*23.', 'fwdbusy', '1234', commented=1)

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        assert_that(hint_dao.forward_hints(self.context.name), contains())

    def test_given_no_blf_then_returns_no_hints(self):
        destination_row = self.create_forward_func_key('_*23.', 'fwdbusy', '1234')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row, blf=False)

        assert_that(hint_dao.forward_hints(self.context.name), contains())

    def test_given_user_when_query_other_context_then_returns_no_hints(self):
        destination_row = self.create_forward_func_key('_*23.', 'fwdbusy', '1234')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        assert_that(hint_dao.forward_hints('othercontext'), contains())

    def test_forward_extension_with_xxx_pattern_is_cleaned(self):
        destination_row = self.create_forward_func_key('_*23XXXX', 'fwdbusy', '1234')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        assert_that(hint_dao.forward_hints(self.context.name), contains(
            Hint(user_id=user_row.id, extension='*23', argument='1234'),
        ))


class TestAgentHints(TestHints):

    def test_given_agent_func_key_then_returns_agent_hint(self):
        destination_row = self.create_agent_func_key('_*31.', 'agentstaticlogin')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        assert_that(hint_dao.agent_hints(self.context.name), contains(
            Hint(user_id=user_row.id, extension='*31', argument=str(destination_row.agent_id)),
        ))

    def test_given_commented_extension_then_returns_no_hints(self):
        destination_row = self.create_agent_func_key('_*31.', 'agentstaticlogin')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row, blf=False)

        assert_that(hint_dao.agent_hints(self.context.name), empty())

    def test_given_no_blf_then_returns_no_hints(self):
        destination_row = self.create_agent_func_key('_*31.', 'agentstaticlogin')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row, blf=False)

        assert_that(hint_dao.agent_hints(self.context.name), empty())

    def test_given_user_when_querying_other_context_then_returns_no_hints(self):
        destination_row = self.create_agent_func_key('_*31.', 'agentstaticlogin')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        assert_that(hint_dao.agent_hints('othercontext'), empty())

    def test_agent_extension_with_xxx_pattern_is_cleaned(self):
        destination_row = self.create_agent_func_key('_*31XXXX', 'agentstaticlogin')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        assert_that(hint_dao.agent_hints(self.context.name), contains(
            Hint(user_id=user_row.id, extension='*31', argument=str(destination_row.agent_id)),
        ))


class TestCustomHints(TestHints):

    def test_given_custom_func_key_then_returns_custom_hint(self):
        destination_row = self.create_custom_func_key('1234')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        assert_that(hint_dao.custom_hints(self.context.name), contains(
            Hint(user_id=None, extension='1234', argument=None),
        ))

    def test_given_user_when_querying_other_context_then_returns_no_hints(self):
        destination_row = self.create_custom_func_key('1234')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        assert_that(hint_dao.custom_hints('othercontext'), empty())


class TestBSFilterHints(TestHints):

    def setUp(self):
        super(TestBSFilterHints, self).setUp()
        self.add_extension(
            context='xivo-features',
            exten='_*37.',
            type='extenfeatures',
            typeval='bsfilter',
        )

    def create_boss_and_secretary(self, commented=0):
        boss_row = self.add_user_and_func_key(exten='1000')
        secretary_row = self.add_user_and_func_key(exten='1001')

        callfilter_row = self.add_call_filter(commented=commented)
        boss_member_row = self.add_filter_member(callfilter_row.id, boss_row.id)
        secretary_member_row = self.add_filter_member(
            callfilter_row.id,
            secretary_row.id,
            'secretary',
        )
        self.add_bsfilter_destination(secretary_member_row.id)
        return boss_member_row, secretary_member_row

    def test_given_bs_filter_func_key_then_returns_bs_filter_hint(self):
        _, filtermember_row = self.create_boss_and_secretary()

        assert_that(hint_dao.bsfilter_hints(self.context.name), contains(
            Hint(user_id=None, extension='*37', argument=str(filtermember_row.id)),
        ))

    def test_given_commented_bs_filter_func_key_then_returns_empty_list(self):
        self.create_boss_and_secretary(commented=1)

        assert_that(hint_dao.bsfilter_hints(self.context.name), empty())

    def test_given_secretary_when_querying_different_context_then_returns_no_hints(self):
        self.create_boss_and_secretary()

        assert_that(hint_dao.bsfilter_hints('othercontext'), empty())


class TestGroupHints(TestHints):

    def test_given_group_member_func_key_then_returns_group_member_hint(self):
        destination_row = self.create_group_member_func_key('_*51.', 'groupmemberjoin')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        expected = Hint(user_id=user_row.id,
                        extension='*51',
                        argument=str(destination_row.group_id))

        assert_that(hint_dao.groupmember_hints(self.context.name), contains(expected))

    def test_given_commented_extension_then_returns_no_hints(self):
        destination_row = self.create_group_member_func_key('_*51.', 'groupmemberjoin')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row, blf=False)

        assert_that(hint_dao.groupmember_hints(self.context.name), contains())

    def test_given_no_blf_then_returns_no_hints(self):
        destination_row = self.create_group_member_func_key('_*51.', 'groupmemberjoin')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row, blf=False)

        assert_that(hint_dao.groupmember_hints(self.context.name), contains())

    def test_given_user_when_querying_other_context_then_returns_no_hints(self):
        destination_row = self.create_group_member_func_key('_*51.', 'groupmemberjoin')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        assert_that(hint_dao.groupmember_hints('othercontext'), contains())

    def test_group_extension_with_xxx_pattern_is_cleaned(self):
        destination_row = self.create_group_member_func_key('_*51XXXX', 'groupmemberjoin')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        expected = Hint(user_id=user_row.id,
                        extension='*51',
                        argument=str(destination_row.group_id))

        assert_that(hint_dao.groupmember_hints(self.context.name), contains(expected))


class TestUserSharedHints(TestHints):

    def test_multi_line_user(self):
        user = self.add_user()
        sip_1 = self.add_endpoint_sip()
        custom_1 = self.add_usercustom(interface='custom')
        sccp_1 = self.add_sccpline(name='1001')
        line_1 = self.add_line(endpoint_sip_uuid=sip_1.uuid)
        line_2 = self.add_line(endpoint_custom_id=custom_1.id)
        line_3 = self.add_line(endpoint_sccp_id=sccp_1.id)
        extension_1 = self.add_extension(typeval=user.id)
        extension_2 = self.add_extension(typeval=user.id)
        self.add_user_line(user_id=user.id, line_id=line_1.id, main_line=True)
        self.add_user_line(user_id=user.id, line_id=line_2.id, main_line=False)
        self.add_user_line(user_id=user.id, line_id=line_3.id, main_line=False)
        self.add_line_extension(line_id=line_1.id, extension_id=extension_1.id)
        self.add_line_extension(line_id=line_2.id, extension_id=extension_1.id)
        self.add_line_extension(line_id=line_3.id, extension_id=extension_2.id)

        results = hint_dao.user_shared_hints()

        assert_that(
            results[0].argument,
            equal_to('pjsip/{}&{}&sccp/{}'.format(line_1.name, line_2.name, line_3.name)),
        )

    def test_no_line(self):
        self.add_user()

        results = hint_dao.user_shared_hints()

        assert_that(results, empty())
