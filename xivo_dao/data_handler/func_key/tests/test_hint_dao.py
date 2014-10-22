# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from hamcrest import assert_that, equal_to, contains
from xivo_dao.tests.test_dao import DAOTestCase

from xivo_dao.alchemy.callfilter import Callfilter
from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.data_handler.func_key.tests.test_helpers import FuncKeyHelper

from xivo_dao.data_handler.func_key import hint_dao
from xivo_dao.data_handler.func_key.model import Hint


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
                           extension_id=extension_row.id,
                           main_user=True,
                           main_line=True)
        return user_row


class TestUserHints(TestHints):

    def test_given_user_with_sip_line_then_returns_user_hint(self):
        usersip_row = self.add_usersip(name='abcdef')
        user_row = self.add_user_and_func_key('sip', usersip_row.id)

        expected = Hint(user_id=user_row.id,
                        extension='1000',
                        argument='SIP/abcdef')

        assert_that(hint_dao.user_hints(self.context), contains(expected))

    def test_given_user_with_sccp_line_then_returns_user_hint(self):
        sccpline_row = self.add_sccpline(name='1001', context=self.context)
        user_row = self.add_user_and_func_key('sccp', sccpline_row.id, '1001')

        expected = Hint(user_id=user_row.id,
                        extension='1001',
                        argument='SCCP/1001')

        assert_that(hint_dao.user_hints(self.context), contains(expected))

    def test_given_user_with_custom_line_then_returns_user_hint(self):
        custom_row = self.add_usercustom(interface='ghijkl', context=self.context)
        user_row = self.add_user_and_func_key('custom', custom_row.id, '1002')

        expected = Hint(user_id=user_row.id,
                        extension='1002',
                        argument='ghijkl')

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


class TestAgentHints(TestHints):

    def test_given_agent_func_key_then_returns_agent_hint(self):
        destination_row = self.create_agent_func_key('_*31.', 'agentstaticlogin', 'login')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        expected = Hint(user_id=user_row.id,
                        extension='*31',
                        argument=str(destination_row.agent_id))

        assert_that(hint_dao.agent_hints(self.context), contains(expected))

    def test_given_commented_extension_then_returns_no_hints(self):
        destination_row = self.create_agent_func_key('_*31.', 'agentstaticlogin', 'login')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row, blf=False)

        assert_that(hint_dao.agent_hints(self.context), contains())

    def test_given_no_blf_then_returns_no_hints(self):
        destination_row = self.create_agent_func_key('_*31.', 'agentstaticlogin', 'login')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row, blf=False)

        assert_that(hint_dao.agent_hints(self.context), contains())

    def test_given_user_when_querying_other_context_then_returns_no_hints(self):
        destination_row = self.create_agent_func_key('_*31.', 'agentstaticlogin', 'login')

        user_row = self.add_user_and_func_key()
        self.add_func_key_to_user(destination_row, user_row)

        assert_that(hint_dao.agent_hints('othercontext'), contains())


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
        callfilter_row = self.add_call_filter('bsfilter', commented=commented)
        boss_member_row = self.add_user_to_filter(boss_row.id, callfilter_row.id)
        secretary_member_row = self.add_user_to_filter(secretary_row.id, callfilter_row.id, 'secretary')
        return boss_member_row, secretary_member_row

    def add_call_filter(self, name, commented=0):
        callfilter = Callfilter(callfrom='internal',
                                type='bosssecretary',
                                bosssecretary='bossfirst-serial',
                                name=name,
                                description='',
                                commented=commented)
        self.add_me(callfilter)
        return callfilter

    def add_user_to_filter(self, userid, filterid, role='boss'):
        member = Callfiltermember(type='user',
                                  typeval=str(userid),
                                  callfilterid=filterid,
                                  bstype=role)
        self.add_me(member)
        return member

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
