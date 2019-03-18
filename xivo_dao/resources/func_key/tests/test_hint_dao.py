# -*- coding: utf-8 -*-
# Copyright 2014-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import six

from itertools import permutations

from mock import ANY

from hamcrest import assert_that, empty, equal_to, contains, contains_inanyorder, any_of
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
        return (item.user_id == self._user_id and
                item.extension == self._extension and
                self._argument_matcher.matches(item.argument))

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
        self.add_extension(context='xivo-features',
                           exten='_*735.',
                           type='extenfeatures',
                           typeval='phoneprogfunckey')

        expected = '*735'

        assert_that(hint_dao.progfunckey_extension(), equal_to(expected))


class TestCalluserExtension(DAOTestCase):

    def test_given_calluser_extension_then_returns_cleaned_calluser(self):
        self.add_extension(context='xivo-features',
                           exten='_*666.',
                           type='extenfeatures',
                           typeval='calluser')

        expected = '*666'

        assert_that(hint_dao.calluser_extension(), equal_to(expected))


class TestHints(DAOTestCase, FuncKeyHelper):

    def setUp(self):
        super(TestHints, self).setUp()
        self.setup_funckeys()
        self.context = 'mycontext'
        self.context2 = 'mycontext2'

    def add_user_and_func_key(self, protocol='sip', protocol_id=None, exten='1000', commented=0, enablehint=1):
        if not protocol_id:
            protocol_id = self.add_usersip().id
        user_row = self.add_user_line_extension(protocol, protocol_id, exten, commented, enablehint)
        self.add_user_destination(user_row.id)

        return user_row

    def add_user_line_extension(self, protocol, protocol_id, exten, commented=0, enablehint=1):
        user_row = self.add_user(enablehint=enablehint)
        line_row = self.add_line(context=self.context,
                                 protocol=protocol,
                                 protocolid=protocol_id,
                                 commented=commented)
        extension_row = self.add_extension(exten=exten, context=self.context)

        self.add_user_line(user_id=user_row.id,
                           line_id=line_row.id,
                           main_user=True,
                           main_line=True)
        self.add_line_extension(line_id=line_row.id,
                                extension_id=extension_row.id,
                                main_extension=True)
        return user_row

    def add_sip_line_to_extension_and_user(self, name, user_id, extension_id, main_line=True):
        endpoint = self.add_usersip(name=name, context=self.context)
        line = self.add_line(context=self.context, protocol='sip', protocolid=endpoint.id)
        self.add_user_line(user_id=user_id, line_id=line.id, main_user=True, main_line=main_line)
        self.add_line_extension(line_id=line.id, extension_id=extension_id, main_extension=True)


class TestUserHints(TestHints):

    def test_given_user_with_sip_line_then_returns_user_hint(self):
        usersip_row = self.add_usersip(name='abcdef')
        user_row = self.add_user_and_func_key('sip', usersip_row.id)

        expected = a_hint(user_id=user_row.id, extension='1000', argument='SIP/abcdef')

        assert_that(hint_dao.user_hints(self.context), contains(expected))

    def test_given_user_with_sccp_line_then_returns_user_hint(self):
        sccpline_row = self.add_sccpline(name='1001', context=self.context)
        user_row = self.add_user_and_func_key('sccp', sccpline_row.id, '1001')

        expected = a_hint(user_id=user_row.id, extension='1001', argument='SCCP/1001')

        assert_that(hint_dao.user_hints(self.context), contains(expected))

    def test_given_user_with_custom_line_then_returns_user_hint(self):
        custom_row = self.add_usercustom(interface='ghijkl', context=self.context)
        user_row = self.add_user_and_func_key('custom', custom_row.id, '1002')

        expected = a_hint(user_id=user_row.id, extension='1002', argument='ghijkl')

        assert_that(hint_dao.user_hints(self.context), contains(expected))

    def test_given_user_with_commented_line_then_returns_empty_list(self):
        self.add_user_and_func_key(exten='1002', commented=1)

        assert_that(hint_dao.user_hints(self.context), contains())

    def test_given_user_with_hints_disabled_then_returns_empty_list(self):
        self.add_user_and_func_key(exten='1003', enablehint=0)

        assert_that(hint_dao.user_hints(self.context), contains())

    def test_given_user_when_querying_different_context_then_returns_empty_list(self):
        self.add_user_and_func_key(exten='1004')

        assert_that(hint_dao.user_hints('othercontext'), contains())

    def test_given_two_users_with_sip_line_then_returns_only_two_hints(self):
        user1 = self.add_user_and_func_key('sip', self.add_usersip(name='user1').id, '1001')
        user2 = self.add_user_and_func_key('sip', self.add_usersip(name='user2').id, '1002')

        expected = [a_hint(user_id=user1.id, extension='1001', argument='SIP/user1'),
                    a_hint(user_id=user2.id, extension='1002', argument='SIP/user2')]

        assert_that(hint_dao.user_hints(self.context), contains_inanyorder(*expected))

    def test_given_one_user_two_lines_one_extension_then_returns_user_hint(self):
        user = self.add_user(enablehint=1)
        extension = self.add_extension(exten='1001', context=self.context)
        self.add_user_destination(user.id)
        self.add_sip_line_to_extension_and_user('line1', user.id, extension.id)
        self.add_sip_line_to_extension_and_user('line2', user.id, extension.id, main_line=False)

        expected = a_hint(user_id=user.id, extension='1001', argument='SIP/line1&SIP/line2')

        assert_that(hint_dao.user_hints(self.context), contains(expected))

    def test_given_one_user_two_lines_two_extensions_then_returns_user_hint(self):
        user = self.add_user(enablehint=1)
        extension1 = self.add_extension(exten='1001', context=self.context)
        extension2 = self.add_extension(exten='1002', context=self.context)
        self.add_user_destination(user.id)
        self.add_sip_line_to_extension_and_user('line1', user.id, extension1.id)
        self.add_sip_line_to_extension_and_user('line2', user.id, extension2.id, main_line=False)

        expected = [a_hint(user_id=user.id, extension='1001', argument='SIP/line1&SIP/line2'),
                    a_hint(user_id=user.id, extension='1002', argument='SIP/line1&SIP/line2')]

        assert_that(hint_dao.user_hints(self.context), contains_inanyorder(*expected))

    def test_given_one_user_two_lines_two_extensions_two_contexts_then_returns_user_hint(self):
        user = self.add_user(enablehint=1)
        extension1 = self.add_extension(exten='1001', context=self.context)
        extension2 = self.add_extension(exten='1002', context=self.context2)
        self.add_user_destination(user.id)
        self.add_sip_line_to_extension_and_user('line1', user.id, extension1.id)
        self.add_sip_line_to_extension_and_user('line2', user.id, extension2.id, main_line=False)

        expected = a_hint(user_id=user.id, extension='1001', argument='SIP/line1&SIP/line2')

        assert_that(hint_dao.user_hints(self.context), contains(expected))

    def test_given_one_user_three_lines_two_extensions_then_returns_user_hint(self):
        user = self.add_user(enablehint=1)
        extension1 = self.add_extension(exten='1001', context=self.context)
        extension2 = self.add_extension(exten='1002', context=self.context)
        self.add_user_destination(user.id)
        self.add_sip_line_to_extension_and_user('line1', user.id, extension1.id)
        self.add_sip_line_to_extension_and_user('line2', user.id, extension2.id, main_line=False)
        self.add_sip_line_to_extension_and_user('line3', user.id, extension2.id, main_line=False)

        expected = [a_hint(user_id=user.id, extension='1001', argument='SIP/line1&SIP/line2&SIP/line3'),
                    a_hint(user_id=user.id, extension='1002', argument='SIP/line1&SIP/line2&SIP/line3')]

        assert_that(hint_dao.user_hints(self.context), contains_inanyorder(*expected))


class TestConferenceHints(TestHints):

    def prepare_conference(self, commented=0):
        conf_row = self.add_meetmefeatures(commented=commented)
        self.add_extension(context=self.context,
                           exten=conf_row.confno,
                           type='meetme',
                           typeval=str(conf_row.id))
        return conf_row

    def test_given_conference_then_returns_conference_hint(self):
        conf_row = self.prepare_conference()
        self.add_conference_destination(conf_row.id)

        expected = Hint(user_id=None,
                        extension=conf_row.confno,
                        argument=None)

        assert_that(hint_dao.conference_hints(self.context), contains(expected))

    def test_given_commented_conference_then_returns_no_hints(self):
        conf_row = self.prepare_conference(commented=1)
        self.add_conference_destination(conf_row.id)

        assert_that(hint_dao.conference_hints(self.context), contains())

    def test_given_conference_when_querying_different_context_then_returns_no_hints(self):
        conf_row = self.prepare_conference()
        self.add_conference_destination(conf_row.id)

        assert_that(hint_dao.conference_hints('othercontext'), contains())


class TestServiceHints(TestHints):

    def test_given_service_func_key_then_returns_service_hint(self):
        destination_row = self.create_service_func_key('*25', 'enablednd')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        expected = Hint(user_id=user_row.id,
                        extension='*25',
                        argument=None)

        assert_that(hint_dao.service_hints(self.context), contains(expected))

    def test_given_commented_extension_then_returns_no_hints(self):
        destination_row = self.create_service_func_key('*25', 'enablednd', commented=1)

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        assert_that(hint_dao.service_hints(self.context), contains())

    def test_given_no_blf_then_returns_no_hints(self):
        destination_row = self.create_service_func_key('*25', 'enablednd')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row, blf=False)

        assert_that(hint_dao.service_hints(self.context), contains())

    def test_given_user_when_query_different_context_then_returns_no_hints(self):
        destination_row = self.create_service_func_key('*25', 'enablednd')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row, blf=False)

        assert_that(hint_dao.service_hints('othercontext'), contains())


class TestForwardHints(TestHints):

    def test_given_forward_func_key_then_returns_forward_hint(self):
        destination_row = self.create_forward_func_key('_*23.', 'fwdbusy', '1234')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        expected = Hint(user_id=user_row.id,
                        extension='*23',
                        argument='1234')

        assert_that(hint_dao.forward_hints(self.context), contains(expected))

    def test_given_forward_without_number_then_returns_forward_hint(self):
        destination_row = self.create_forward_func_key('_*23.', 'fwdbusy')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        expected = Hint(user_id=user_row.id,
                        extension='*23',
                        argument=None)

        assert_that(hint_dao.forward_hints(self.context), contains(expected))

    def test_given_commented_extension_then_returns_no_hints(self):
        destination_row = self.create_forward_func_key('_*23.', 'fwdbusy', '1234', commented=1)

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        assert_that(hint_dao.forward_hints(self.context), contains())

    def test_given_no_blf_then_returns_no_hints(self):
        destination_row = self.create_forward_func_key('_*23.', 'fwdbusy', '1234')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row, blf=False)

        assert_that(hint_dao.forward_hints(self.context), contains())

    def test_given_user_when_query_other_context_then_returns_no_hints(self):
        destination_row = self.create_forward_func_key('_*23.', 'fwdbusy', '1234')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        assert_that(hint_dao.forward_hints('othercontext'), contains())

    def test_forward_extension_with_xxx_pattern_is_cleaned(self):
        destination_row = self.create_forward_func_key('_*23XXXX', 'fwdbusy', '1234')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        expected = Hint(user_id=user_row.id,
                        extension='*23',
                        argument='1234')

        assert_that(hint_dao.forward_hints(self.context), contains(expected))


class TestAgentHints(TestHints):

    def test_given_agent_func_key_then_returns_agent_hint(self):
        destination_row = self.create_agent_func_key('_*31.', 'agentstaticlogin')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        expected = Hint(user_id=user_row.id,
                        extension='*31',
                        argument=str(destination_row.agent_id))

        assert_that(hint_dao.agent_hints(self.context), contains(expected))

    def test_given_commented_extension_then_returns_no_hints(self):
        destination_row = self.create_agent_func_key('_*31.', 'agentstaticlogin')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row, blf=False)

        assert_that(hint_dao.agent_hints(self.context), contains())

    def test_given_no_blf_then_returns_no_hints(self):
        destination_row = self.create_agent_func_key('_*31.', 'agentstaticlogin')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row, blf=False)

        assert_that(hint_dao.agent_hints(self.context), contains())

    def test_given_user_when_querying_other_context_then_returns_no_hints(self):
        destination_row = self.create_agent_func_key('_*31.', 'agentstaticlogin')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        assert_that(hint_dao.agent_hints('othercontext'), contains())

    def test_agent_extension_with_xxx_pattern_is_cleaned(self):
        destination_row = self.create_agent_func_key('_*31XXXX', 'agentstaticlogin')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        expected = Hint(user_id=user_row.id,
                        extension='*31',
                        argument=str(destination_row.agent_id))

        assert_that(hint_dao.agent_hints(self.context), contains(expected))


class TestCustomHints(TestHints):

    def test_given_custom_func_key_then_returns_custom_hint(self):
        destination_row = self.create_custom_func_key('1234')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        expected = Hint(user_id=None,
                        extension='1234',
                        argument=None)

        assert_that(hint_dao.custom_hints(self.context), contains(expected))

    def test_given_user_when_querying_other_context_then_returns_no_hints(self):
        destination_row = self.create_custom_func_key('1234')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        assert_that(hint_dao.custom_hints('othercontext'), contains())


class TestBSFilterHints(TestHints):

    def setUp(self):
        super(TestBSFilterHints, self).setUp()
        self.add_extension(context='xivo-features',
                           exten='_*37.',
                           type='extenfeatures',
                           typeval='bsfilter')

    def create_boss_and_secretary(self, commented=0):
        boss_row = self.add_user_and_func_key(exten='1000')
        secretary_row = self.add_user_and_func_key(exten='1001')

        callfilter_row = self.add_call_filter(commented=commented)
        boss_member_row = self.add_filter_member(callfilter_row.id, boss_row.id)
        secretary_member_row = self.add_filter_member(callfilter_row.id, secretary_row.id, 'secretary')
        self.add_bsfilter_destination(secretary_member_row.id)
        return boss_member_row, secretary_member_row

    def test_given_bs_filter_func_key_then_returns_bs_filter_hint(self):
        _, filtermember_row = self.create_boss_and_secretary()

        expected = Hint(user_id=None,
                        extension='*37',
                        argument=str(filtermember_row.id))

        assert_that(hint_dao.bsfilter_hints(self.context), contains(expected))

    def test_given_commented_bs_filter_func_key_then_returns_empty_list(self):
        self.create_boss_and_secretary(commented=1)

        assert_that(hint_dao.bsfilter_hints(self.context), contains())

    def test_given_secretary_when_querying_different_context_then_returns_no_hints(self):
        self.create_boss_and_secretary()

        assert_that(hint_dao.bsfilter_hints('othercontext'), contains())


class TestGroupHints(TestHints):

    def test_given_group_member_func_key_then_returns_group_member_hint(self):
        destination_row = self.create_group_member_func_key('_*51.', 'groupmemberjoin')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        expected = Hint(user_id=user_row.id,
                        extension='*51',
                        argument=str(destination_row.group_id))

        assert_that(hint_dao.groupmember_hints(self.context), contains(expected))

    def test_given_commented_extension_then_returns_no_hints(self):
        destination_row = self.create_group_member_func_key('_*51.', 'groupmemberjoin')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row, blf=False)

        assert_that(hint_dao.groupmember_hints(self.context), contains())

    def test_given_no_blf_then_returns_no_hints(self):
        destination_row = self.create_group_member_func_key('_*51.', 'groupmemberjoin')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row, blf=False)

        assert_that(hint_dao.groupmember_hints(self.context), contains())

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

        assert_that(hint_dao.groupmember_hints(self.context), contains(expected))


class TestUserSharedHints(TestHints):

    def test_multi_line_user(self):
        user = self.add_user()
        sip_1 = self.add_usersip()
        sip_2 = self.add_usersip()
        sccp_1 = self.add_sccpline(name='1001')
        line_1 = self.add_line(protocol='sip', protocolid=sip_1.id)
        line_2 = self.add_line(protocol='sip', protocolid=sip_2.id)
        line_3 = self.add_line(protocol='sccp', protocolid=sccp_1.id)
        extension_1 = self.add_extension(typeval=user.id)
        extension_2 = self.add_extension(typeval=user.id)
        self.add_user_line(user_id=user.id, line_id=line_1.id, main_line=True)
        self.add_user_line(user_id=user.id, line_id=line_2.id, main_line=False)
        self.add_user_line(user_id=user.id, line_id=line_3.id, main_line=False)
        self.add_line_extension(line_id=line_1.id, extension_id=extension_1.id)
        self.add_line_extension(line_id=line_2.id, extension_id=extension_1.id)
        self.add_line_extension(line_id=line_3.id, extension_id=extension_2.id)

        results = hint_dao.user_shared_hints()

        assert_that(results, contains_inanyorder(
            Hint(ANY, user.uuid, '&'.join([
                'pjsip/{}'.format(line_1.name),
                'pjsip/{}'.format(line_2.name),
                'sccp/{}'.format(line_3.name),
            ])),
        ))

    def test_no_line(self):
        self.add_user()

        results = hint_dao.user_shared_hints()

        assert_that(results, empty())
