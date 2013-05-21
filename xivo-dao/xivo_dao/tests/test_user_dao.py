# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
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

from hamcrest import *
from xivo_dao import user_dao
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.callfilter import Callfilter
from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.alchemy.contextinclude import ContextInclude
from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.alchemy.ctiphonehintsgroup import CtiPhoneHintsGroup
from xivo_dao.alchemy.ctipresences import CtiPresences
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.phonefunckey import PhoneFunckey


class TestUserFeaturesDAO(DAOTestCase):

    tables = [UserFeatures, LineFeatures, ContextInclude, AgentFeatures,
              CtiPresences, CtiPhoneHintsGroup, CtiProfile, QueueMember,
              RightCallMember, Callfiltermember, Callfilter, Dialaction,
              PhoneFunckey]

    def setUp(self):
        self.empty_tables()

    def test_get_one_result(self):
        user_id = self._insert_user('first')

        user = user_dao.get(user_id)

        self.assertEqual(user.id, user_id)

    def test_get_string_id(self):
        user_id = self._insert_user('first')

        user = user_dao.get(str(user_id))

        self.assertEqual(user.id, user_id)

    def test_get_no_result(self):
        self.assertRaises(LookupError, user_dao.get, 1)

    def test_set_dnd(self):
        user_id = self._insert_user_dnd_not_set()

        user_dao.enable_dnd(user_id)

        self._check_dnd_is_set(user_id)

    def test_unset_dnd(self):
        user_id = self._insert_user_dnd_set()

        user_dao.disable_dnd(user_id)

        self._check_dnd_is_not_set(user_id)

    def _insert_user(self, firstname):
        user = UserFeatures()
        user.firstname = firstname

        self.add_me(user)

        return user.id

    def _insert_user_dnd_set(self):
        user_features = UserFeatures()
        user_features.enablednd = 1
        user_features.firstname = 'firstname_test'

        self.add_me(user_features)

        user_id = user_features.id
        return user_id

    def _insert_user_dnd_not_set(self):
        user_features = UserFeatures()
        user_features.enablednd = 0
        user_features.firstname = 'firstname_dnd not set'

        self.add_me(user_features)

        user_id = user_features.id
        return user_id

    def _check_dnd_is_set(self, user_id):
        user_features = (self.session.query(UserFeatures)
                         .filter(UserFeatures.id == user_id))[0]
        self.assertTrue(user_features.enablednd)

    def _check_dnd_is_not_set(self, user_id):
        user_features = (self.session.query(UserFeatures)
                         .filter(UserFeatures.id == user_id))[0]
        self.assertFalse(user_features.enablednd)

    def test_enable_filter(self):
        user_id = self._insert_user_with_filter(0)

        user_dao.enable_filter(user_id)

        self._check_filter_in_db(user_id, 1)

    def test_disable_filter(self):
        user_id = self._insert_user_with_filter(1)

        user_dao.disable_filter(user_id)

        self._check_filter_in_db(user_id, 0)

    def _insert_user_with_filter(self, filter_status):
        user_features = UserFeatures()
        user_features.incallfilter = filter_status
        user_features.firstname = 'firstname_filter not set'

        self.add_me(user_features)

        user_id = user_features.id
        return user_id

    def test_enable_recording(self):
        user_id = self._insert_user_recording_disabled()
        user_dao.enable_recording(user_id)
        self._check_recording(user_id, 1)

    def test_disable_recording(self):
        user_id = self._insert_user_recording_enabled()
        user_dao.disable_recording(user_id)
        self._check_recording(user_id, 0)

    def _check_recording(self, user_id, value):
        user_features = (self.session.query(UserFeatures)
                         .filter(UserFeatures.id == user_id))[0]
        self.assertEquals(user_features.callrecord, value)

    def _insert_user_recording_disabled(self):
        user_features = UserFeatures()
        user_features.callrecord = 0
        user_features.firstname = 'firstname_recording not set'
        self.add_me(user_features)

        user_id = user_features.id
        return user_id

    def _insert_user_recording_enabled(self):
        user_features = UserFeatures()
        user_features.callrecord = 1
        user_features.firstname = 'firstname_recording set'
        self.add_me(user_features)

        user_id = user_features.id
        return user_id

    def _check_filter_in_db(self, user_id, value):
        user_features = (self.session.query(UserFeatures)
                         .filter(UserFeatures.id == user_id))[0]
        self.assertEquals(user_features.incallfilter, value)

    def test_enable_unconditional_fwd(self):
        destination = '765'
        user_id = self._insert_user_with_unconditional_fwd(destination, 0)

        user_dao.enable_unconditional_fwd(user_id, destination)

        self._check_unconditional_fwd_in_db(user_id, 1)
        self._check_unconditional_dest_in_db(user_id, destination)

    def _insert_user_with_unconditional_fwd(self, destination, enabled):
        user_features = UserFeatures()
        user_features.enableunc = enabled
        user_features.destunc = destination
        user_features.firstname = 'firstname_unconditional_fwd'

        self.add_me(user_features)

        user_id = user_features.id
        return user_id

    def _check_unconditional_fwd_in_db(self, user_id, value):
        user_features = (self.session.query(UserFeatures)
                         .filter(UserFeatures.id == user_id))[0]
        self.assertEquals(user_features.enableunc, value)

    def test_unconditional_fwd_disabled(self):
        destination = '4321'
        user_id = self._insert_user_with_unconditional_fwd('', 0)

        user_dao.disable_unconditional_fwd(user_id, destination)

        self._check_unconditional_fwd_in_db(user_id, 0)
        self._check_unconditional_dest_in_db(user_id, destination)

    def _check_unconditional_dest_in_db(self, user_id, destination):
        user_features = (self.session.query(UserFeatures)
                         .filter(UserFeatures.id == user_id))[0]
        self.assertEquals(user_features.destunc, destination)

    def test_rna_fwd_enabled(self):
        destination = '4321'
        user_id = self._insert_user_with_rna_fwd('', 1)

        user_dao.enable_rna_fwd(user_id, destination)

        self._check_rna_fwd_in_db(user_id, 1)
        self._check_rna_dest_in_db(user_id, destination)

    def test_rna_fwd_disabled(self):
        destination = '4325'
        user_id = self._insert_user_with_rna_fwd('', 0)

        user_dao.disable_rna_fwd(user_id, destination)

        self._check_rna_fwd_in_db(user_id, 0)
        self._check_rna_dest_in_db(user_id, destination)

    def _insert_user_with_rna_fwd(self, destination, enabled):
        user_features = UserFeatures()
        user_features.enablerna = enabled
        user_features.destrna = destination
        user_features.firstname = 'firstname_rna_fwd'

        self.add_me(user_features)

        user_id = user_features.id
        return user_id

    def _check_rna_dest_in_db(self, user_id, destination):
        user_features = (self.session.query(UserFeatures)
                         .filter(UserFeatures.id == user_id))[0]
        self.assertEquals(user_features.destrna, destination)

    def _check_rna_fwd_in_db(self, user_id, value):
        user_features = (self.session.query(UserFeatures)
                         .filter(UserFeatures.id == user_id))[0]
        self.assertEquals(user_features.enablerna, value)

    def _insert_user_with_busy_fwd(self, destination, enabled):
        user_features = UserFeatures()
        user_features.enablebusy = enabled
        user_features.destbusy = destination
        user_features.firstname = 'firstname_busy_fwd'

        self.add_me(user_features)

        user_id = user_features.id
        return user_id

    def _check_busy_fwd_in_db(self, user_id, value):
        user_features = (self.session.query(UserFeatures)
                         .filter(UserFeatures.id == user_id))[0]
        self.assertEquals(user_features.enablebusy, value)

    def _check_busy_dest_in_db(self, user_id, destination):
        user_features = (self.session.query(UserFeatures)
                         .filter(UserFeatures.id == user_id))[0]
        self.assertEquals(user_features.destbusy, destination, 'Destination not updated')

    def test_busy_fwd_disabled(self):
        destination = '435'
        user_id = self._insert_user_with_busy_fwd('', 0)

        user_dao.disable_busy_fwd(user_id, destination)

        self._check_busy_fwd_in_db(user_id, 0)
        self._check_busy_dest_in_db(user_id, destination)

    def test_busy_fwd_enabled(self):
        destination = '435'
        user_id = self._insert_user_with_busy_fwd('', 1)

        user_dao.enable_busy_fwd(user_id, destination)

        self._check_busy_fwd_in_db(user_id, 1)
        self._check_busy_dest_in_db(user_id, destination)

    def test_find_by_agent_id(self):
        agent_id = 5
        user = UserFeatures()

        user.firstname = 'test_agent'
        user.agentid = agent_id

        self.add_me(user)

        user_ids = user_dao.find_by_agent_id(agent_id)

        self.assertEqual(user_ids[0], user.id)

    def test_agent_id(self):
        agent_id = 5
        user = UserFeatures()

        user.firstname = 'test_agent'
        user.agentid = agent_id

        self.add_me(user)

        res = user_dao.agent_id(user.id)

        self.assertEqual(res, agent_id)

    def test_agent_id_no_agent(self):
        user = UserFeatures()

        user.firstname = 'test_agent'

        self.add_me(user)

        res = user_dao.agent_id(user.id)

        self.assertEqual(res, None)

    def test_is_agent_yes(self):
        agent_id = 5
        user = UserFeatures()

        user.firstname = 'test_agent'
        user.agentid = agent_id

        self.add_me(user)

        result = user_dao.is_agent(user.id)

        self.assertEqual(result, True)

    def test_is_agent_no(self):
        user = UserFeatures()

        user.firstname = 'test_agent'

        self.add_me(user)

        result = user_dao.is_agent(user.id)

        self.assertEqual(result, False)

    def test_get_profile(self):
        user_profile_id = self._add_profile('test_profile')

        user = UserFeatures()
        user.firstname = 'test_agent'
        user.cti_profile_id = user_profile_id

        self.add_me(user)

        result = user_dao.get_profile(user.id)

        self.assertEqual(result, user_profile_id)

    def _add_presence(self, name):
        cti_presence = CtiPresences()
        cti_presence.name = name

        self.add_me(cti_presence)

        return cti_presence.id

    def _add_phone_hints_group(self, name):
        cti_phone_hints_group = CtiPhoneHintsGroup()
        cti_phone_hints_group.name = name

        self.add_me(cti_phone_hints_group)

        return cti_phone_hints_group.id

    def _add_profile(self, name):
        cti_profile = CtiProfile()
        cti_profile.name = name
        cti_profile.presence_id = self._add_presence('test_presence')
        cti_profile.phonehints_id = self._add_phone_hints_group('test_add_phone_hints_group')

        self.add_me(cti_profile)

        return cti_profile.id

    def _add_user(self, firstname, lastname=''):
        user = UserFeatures(
            firstname=firstname,
            lastname=lastname
        )
        self.add_me(user)

        return user

    def _add_user_with_line(self, name, context='default'):
        user = self._add_user(name)

        line = LineFeatures()
        line.iduserfeatures = user.id
        line.context = context
        line.protocolid = 1
        line.name = 'jk1j3'
        line.provisioningid = '12345'

        self.add_me(line)

        return user, line

    def _add_user_to_queue(self, userid, queuename):
        queuemember = QueueMember(usertype='user',
                                  userid=userid,
                                  category='queue',
                                  queue_name=queuename,
                                  interface='SIP/stuff',
                                  channel='SIP')
        self.add_me(queuemember)

    def _add_user_to_rightcall(self, userid, rightcallid):
        member = RightCallMember(type='user', typeval=str(userid), rightcallid=rightcallid)
        self.add_me(member)

    def _add_user_to_callfilter(self, userid, callfilterid):
        member = Callfiltermember(type='user',
                                  typeval=str(userid),
                                  callfilterid=callfilterid,
                                  bstype='boss')
        self.add_me(member)

    def _add_dialaction_to_user(self, userid):
        dialaction = Dialaction(event='answer', category='user', categoryval=str(userid), action='none')
        self.add_me(dialaction)

    def _add_function_key_to_user(self, userid):
        key = PhoneFunckey(iduserfeatures=userid, fknum=1, typeextenumbersright='user')
        self.add_me(key)

    def test_get_reachable_contexts(self):
        context = 'my_context'

        user, line = self._add_user_with_line('Tester', context)

        result = user_dao.get_reachable_contexts(user.id)

        self.assertEqual(result, [context])

    def test_get_reachable_context_no_line(self):
        user = UserFeatures()
        user.name = 'Tester'

        self.add_me(user)

        self.assertEqual(user_dao.get_reachable_contexts(user.id), [])

    def test_get_reachable_context_included_ctx(self):
        context = 'my_context'
        included_context = 'second_ctx'

        ctx_include = ContextInclude()
        ctx_include.context = context
        ctx_include.include = included_context

        self.add_me(ctx_include)

        user, line = self._add_user_with_line('Tester', context)

        result = user_dao.get_reachable_contexts(user.id)

        self.assertEqual(result, [context, included_context])

    def test_get_reachable_context_loop(self):
        context = 'my_context'
        included_context = 'second_ctx'
        looping_context = 'third_ctx'

        ctx = ContextInclude()
        ctx.context = context
        ctx.include = included_context

        ctx_include = ContextInclude()
        ctx_include.context = included_context
        ctx_include.include = looping_context

        ctx_loop = ContextInclude()
        ctx_loop.context = looping_context
        ctx_loop.include = context

        map(self.add_me, [ctx, ctx_include, ctx_loop])

        user, line = self._add_user_with_line('Tester', context)

        result = user_dao.get_reachable_contexts(user.id)

        for context in [context, included_context, looping_context]:
            self.assertTrue(context in result)

    def test_get_line_identity(self):
        self.assertRaises(LookupError, user_dao.get_line_identity, 1234)

        user = UserFeatures()
        user.name = 'Tester'

        self.add_me(user)

        line = LineFeatures()
        line.protocolid = 1
        line.name = 'a1b2c3'
        line.protocol = 'sip'
        line.iduserfeatures = user.id
        line.context = 'ctx'
        line.provisioningid = 1234

        self.add_me(line)

        expected = 'sip/a1b2c3'
        result = user_dao.get_line_identity(user.id)

        self.assertEqual(result, expected)

    def test_find_by_line_id(self):
        user = UserFeatures()
        user.firstname = 'test'

        self.add_me(user)

        line = LineFeatures()
        line.protocolid = 1
        line.name = 'abc'
        line.context = 'test_ctx'
        line.provisioningid = 2
        line.iduserfeatures = user.id

        self.add_me(line)

        user_id = user_dao.find_by_line_id(line.id)

        self.assertEqual(user_id, user.id)

    def test_get_agent_number(self):
        self.assertRaises(LookupError, user_dao.get_agent_number, 1)

        agent = AgentFeatures()
        agent.number = '1234'
        agent.numgroup = 0
        agent.passwd = ''
        agent.context = 'ctx'
        agent.language = 'fr'

        self.add_me(agent)

        user = UserFeatures()
        user.agentid = agent.id

        self.add_me(user)

        result = user_dao.get_agent_number(user.id)

        self.assertEqual(result, agent.number)

    def test_get_dest_unc(self):
        user = UserFeatures()

        self.add_me(user)

        result = user_dao.get_dest_unc(user.id)

        self.assertEqual(result, '')

        self.session.begin()
        user.destunc = '1002'
        self.session.commit()

        result = user_dao.get_dest_unc(user.id)

        self.assertEqual(result, '1002')

    def test_get_fwd_unc(self):
        user = UserFeatures()

        self.add_me(user)

        result = user_dao.get_fwd_unc(user.id)

        self.assertFalse(result)

        self.session.begin()
        user.enableunc = 1
        self.session.commit()

        result = user_dao.get_fwd_unc(user.id)

        self.assertTrue(result)

    def test_get_dest_busy(self):
        user = UserFeatures()

        self.add_me(user)

        result = user_dao.get_dest_busy(user.id)

        self.assertEqual(result, '')

        self.session.begin()
        user.destbusy = '1002'
        self.session.commit()

        result = user_dao.get_dest_busy(user.id)

        self.assertEqual(result, '1002')

    def test_get_fwd_busy(self):
        user = UserFeatures()

        self.add_me(user)

        result = user_dao.get_fwd_busy(user.id)

        self.assertFalse(result)

        self.session.begin()
        user.enablebusy = 1
        self.session.commit()

        result = user_dao.get_fwd_busy(user.id)

        self.assertTrue(result)

    def test_get_dest_rna(self):
        user = UserFeatures()

        self.add_me(user)

        result = user_dao.get_dest_rna(user.id)

        self.assertEqual(result, '')

        self.session.begin()
        user.destrna = '1002'
        self.session.commit()

        result = user_dao.get_dest_rna(user.id)

        self.assertEqual(result, '1002')

    def test_get_fwd_rna(self):
        user = UserFeatures()

        self.add_me(user)

        result = user_dao.get_fwd_rna(user.id)

        self.assertFalse(result)

        self.session.begin()
        user.enablerna = 1
        self.session.commit()

        result = user_dao.get_fwd_rna(user.id)

        self.assertTrue(result)

    def test_get_name_number(self):
        user = UserFeatures()
        user.firstname = 'Toto'
        user.lastname = 'Plop'

        self.add_me(user)

        line = LineFeatures()
        line.number = '1234'
        line.name = '12kjdhf'
        line.context = 'context'
        line.provisioningid = 1234
        line.iduserfeatures = user.id
        line.protocolid = 1

        self.add_me(line)

        name, number = user_dao.get_name_number(user.id)

        self.assertEqual(name, '%s %s' % (user.firstname, user.lastname))
        self.assertEqual(number, '1234')

    def test_get_device_id_with_one_user(self):
        device_id = 8

        user = UserFeatures()
        user.firstname = 'Toto'
        user.lastname = 'Plop'

        self.add_me(user)

        line = LineFeatures()
        line.number = '1234'
        line.name = '12kjdhf'
        line.context = 'context'
        line.provisioningid = 1234
        line.iduserfeatures = user.id
        line.protocolid = 1
        line.device = str(8)

        self.add_me(line)

        result = user_dao.get_device_id(user.id)

        self.assertEqual(result, device_id)

    def test_get_device_id_with_two_users(self):
        device_id = 24

        user1 = UserFeatures()
        user1.firstname = 'Toto1'
        user1.lastname = 'Plop1'

        self.add_me(user1)

        user2 = UserFeatures()
        user2.firstname = 'Toto2'
        user2.lastname = 'Plop2'

        self.add_me(user2)

        line = LineFeatures()
        line.number = '1234'
        line.name = '12kjdhf'
        line.context = 'context'
        line.provisioningid = 1234
        line.iduserfeatures = user2.id
        line.protocolid = 1
        line.device = str(device_id)

        self.add_me(line)

        result = user_dao.get_device_id(user2.id)

        self.assertEqual(result, device_id)

    def test_get_device_id_no_line(self):
        user = UserFeatures()
        user.firstname = 'Toto'
        user.lastname = 'Plop'

        self.add_me(user)

        self.assertRaises(LookupError, user_dao.get_device_id, user.id)

    def test_get_device_id_no_user(self):
        self.assertRaises(LookupError, user_dao.get_device_id, 666)

    def test_get_context(self):
        user, line = self._add_user_with_line('test_user1')

        context = user_dao.get_context(user.id)

        self.assertEquals(context, line.context)

    def test_get_context_no_line(self):
        user = self._add_user('test_user1')

        context = user_dao.get_context(user.id)

        self.assertEqual(context, None)

    def test_get_all(self):
        user1 = self._add_user('test_user_1')
        user2 = self._add_user('test_user_2')
        result = user_dao.get_all()
        self.assertEqual(result[0].firstname, user1.firstname)
        self.assertEqual(result[1].firstname, user2.firstname)

    def test_delete_all(self):
        self._add_user('test_user_1')
        self._add_user('test_user_2')
        user_dao.delete_all()
        result = user_dao.get_all()
        self.assertEqual(result, [])

    def test_add_user(self):
        user = UserFeatures()
        user.firstname = 'test_user'
        user_dao.add_user(user)
        result = user_dao.get_all()
        self.assertEqual(result, [user])

    def test_update(self):
        user = self._add_user('test')
        data = {'firstname': 'test_first',
                'lastname': 'test_last'}

        result = user_dao.update(user.id, data)

        user = user_dao.get(user.id)
        self.assertEqual(user.firstname, 'test_first')
        self.assertEqual(user.lastname, 'test_last')
        self.assertEqual(result, 1)

    def test_update_unexisting_user(self):
        data = {'firstname': 'test_first',
                'lastname': 'test_last'}
        result = user_dao.update(1, data)
        self.assertEqual(result, 0)

    def test_delete(self):
        user1 = self._add_user('test1')
        generated_id = user1.id
        queuename = "my_queue"
        rightcallid = 3
        self._add_user_to_queue(user1.id, queuename)
        self._add_user_to_rightcall(user1.id, rightcallid)
        callfilter = Callfilter(type='bosssecretary', name='test', bosssecretary='secretary-simult', callfrom='all', description='')
        self.add_me(callfilter)
        self._add_user_to_callfilter(user1.id, callfilter.id)
        self._add_dialaction_to_user(user1.id)
        self._add_function_key_to_user(user1.id)

        result = user_dao.delete(generated_id)

        self.assertEqual(result, 1)
        self.assertRaises(LookupError, user_dao.get, generated_id)
        queue_member_for_user = (self.session.query(QueueMember)
                                             .filter(QueueMember.usertype == 'user')
                                             .filter(QueueMember.userid == generated_id)
                                             .first())
        self.assertEquals(None, queue_member_for_user)
        rightcallmember_for_user = (self.session.query(RightCallMember)
                                                .filter(RightCallMember.type == 'user')
                                                .filter(RightCallMember.typeval == str(generated_id))
                                                .first())
        self.assertEquals(None, rightcallmember_for_user)
        callfiltermember_for_user = (self.session.query(Callfiltermember)
                                                 .filter(Callfiltermember.type == 'user')
                                                 .filter(Callfiltermember.typeval == str(generated_id))
                                                 .first())
        self.assertEquals(None, callfiltermember_for_user)
        user_dialaction = (self.session.query(Dialaction)
                               .filter(Dialaction.category == 'user')
                               .filter(Dialaction.categoryval == str(generated_id))
                               .first())
        self.assertEquals(None, user_dialaction)
        user_key = self.session.query(PhoneFunckey).filter(PhoneFunckey.iduserfeatures == generated_id).first()
        self.assertEquals(None, user_key)

    def test_delete_unexisting_user(self):
        result = user_dao.delete(1)
        self.assertEqual(result, 0)

    def test_get_user_config(self):
        firstname = u'Jack'
        lastname = u'Strap'
        fullname = u'%s %s' % (firstname, lastname)
        callerid = u'"%s"' % fullname
        context = u'mycontext'

        user = UserFeatures(
            firstname=firstname,
            lastname=lastname,
            callerid=callerid,
        )
        self.add_me(user)

        line = LineFeatures(
            iduserfeatures=user.id,
            number='1234',
            name='12kjdhf',
            context=context,
            provisioningid=1234,
            protocolid=1,
        )
        self.add_me(line)

        user_id = user.id
        line_list = [str(line.id)]
        expected = {
            str(user_id): {
                'agentid': None,
                'bsfilter': 'no',
                'callerid': callerid,
                'callrecord': 0,
                'commented': 0,
                'context': context,
                'cti_profile_id': None,
                'description': None,
                'destbusy': u'',
                'destrna': u'',
                'destunc': u'',
                'enableautomon': 0,
                'enablebusy': 0,
                'enableclient': 1,
                'enablednd': 0,
                'enablehint': 1,
                'enablerna': 0,
                'enableunc': 0,
                'enablevoicemail': 0,
                'enablexfer': 0,
                'entityid': None,
                'firstname': firstname,
                'fullname': fullname,
                'id': user_id,
                'identity': fullname,
                'incallfilter': 0,
                'language': None,
                'lastname': lastname,
                'linelist': line_list,
                'loginclient': u'',
                'mobilephonenumber': u'',
                'musiconhold': u'',
                'outcallerid': u'',
                'passwdclient': u'',
                'pictureid': None,
                'preprocess_subroutine': None,
                'rightcallcode': None,
                'ringextern': None,
                'ringforward': None,
                'ringgroup': None,
                'ringintern': None,
                'ringseconds': 30,
                'simultcalls': 5,
                'timezone': None,
                'userfield': u'',
                'voicemailid': None,
                'voicemailtype': None,
            }
        }

        result = user_dao.get_user_config(user_id)

        result_dict = result[str(user_id)]
        expected_dict = expected[str(user_id)]

        for key, expected_value in expected_dict.iteritems():
            result_value = result_dict[key]
            assert_that(expected_value, equal_to(result_value),
                        'key %r does not match' % key)
        assert_that(result, equal_to(expected))

    def test_get_user_config_with_no_line(self):
        user = UserFeatures()
        self.add_me(user)

        result = user_dao.get_user_config(user.id)

        assert_that(result[str(user.id)]['context'], none())
        assert_that(result[str(user.id)]['linelist'], equal_to([]))

    def test_get_users_config(self):
        user1 = UserFeatures(
            firstname='John',
            lastname='Jackson',
        )
        user2 = UserFeatures(
            firstname='Jack',
            lastname='Johnson',
        )
        self.add_me(user1)
        self.add_me(user2)

        result = user_dao.get_users_config()

        user1_id = str(user1.id)
        user2_id = str(user2.id)
        assert_that(result, contains_inanyorder(user1_id, user2_id))
        assert_that(result[user1_id]['firstname'], equal_to(user1.firstname))
        assert_that(result[user2_id]['firstname'], equal_to(user2.firstname))

    def test_get_by_voicemailid(self):
        user1 = UserFeatures(
            firstname='John',
            lastname='Jackson',
            voicemailid=1
        )
        user2 = UserFeatures(
            firstname='Jack',
            lastname='Johnson',
            voicemailid=1
        )
        user3 = UserFeatures(
            firstname='Christopher',
            lastname='Christopherson',
            voicemailid=2
        )
        self.add_me(user1)
        self.add_me(user2)
        self.add_me(user3)
        result = user_dao.get_by_voicemailid(1)
        result = [user.id for user in result]
        self.assertTrue(user1.id in result)
        self.assertTrue(user2.id in result)
        self.assertFalse(user3.id in result)

    def test_get_user_join_line(self):
        user, line = self._add_user_with_line("my_test", "default")
        line.number = "1234"
        self.add_me(line)

        resultuser, resultline = user_dao.get_user_join_line(user.id)
        self.assertEqual(user.firstname, resultuser.firstname)
        self.assertEqual(line.id, resultline.id)
        self.assertEqual(resultline.number, "1234")

    def test_get_user_join_line_no_result(self):
        result = user_dao.get_user_join_line(1)
        self.assertEqual(result, None)

    def test_get_user_join_line_no_line(self):
        user = self._add_user("test")
        resultuser, resultline = user_dao.get_user_join_line(user.id)
        self.assertEqual(user.firstname, resultuser.firstname)
        self.assertEqual(None, resultline)

    def test_get_all_join_lines(self):
        user1, line1 = self._add_user_with_line("test1", "default")
        user2, line2 = self._add_user_with_line("test2", "default")

        result = user_dao.get_all_join_line()
        self.assertEqual((user1.firstname, line1.id), (result[0][0].firstname, result[0][1].id))
        self.assertEqual((user2.firstname, line2.id), (result[1][0].firstname, result[1][1].id))
