# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from hamcrest import assert_that, equal_to, contains, has_property, all_of, instance_of, contains_inanyorder
from sqlalchemy.exc import SQLAlchemyError
from mock import Mock

from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.helpers.exception import DataError
from xivo_dao.alchemy.voicemail import Voicemail as VoicemailSchema
from xivo_dao.alchemy.incall import Incall as IncallSchema
from xivo_dao.alchemy.dialaction import Dialaction as DialactionSchema
from xivo_dao.resources.voicemail import dao as voicemail_dao
from xivo_dao.resources.voicemail.model import Voicemail
from xivo_dao.tests.helpers.session import mocked_dao_session
from xivo_dao.tests.test_dao import DAOTestCase


class TestSearchVoicemail(DAOTestCase):

    def _has_voicemail(self, voicemail):
        matchers = []
        for field in Voicemail.FIELDS:
            matcher = has_property(field, getattr(voicemail, field))
            matchers.append(matcher)

        return all_of(instance_of(Voicemail), *matchers)

    def test_search_no_voicemails(self):
        result = voicemail_dao.search()

        assert_that(result, all_of(
            has_property('total', 0),
            has_property('items', [])))

    def test_search_one_voicemail(self):
        name = 'myvoicemail'
        context = 'default'
        number = '1000'

        voicemail_row = VoicemailSchema(fullname=name,
                                        context=context,
                                        mailbox=number)
        self.add_me(voicemail_row)

        expected_voicemail = Voicemail(
            id=voicemail_row.uniqueid,
            name=name,
            context=context,
            number=number,
            attach_audio=False,
            delete_messages=False,
            ask_password=True,
        )

        result = voicemail_dao.search()

        assert_that(result.total, equal_to(1))
        assert_that(result.items, contains(self._has_voicemail(expected_voicemail)))

    def test_search_two_voicemails(self):
        context = 'default'

        voicemail_row1 = VoicemailSchema(fullname='voicemail1',
                                         context=context,
                                         mailbox='1000')

        voicemail_row2 = VoicemailSchema(fullname='voicemail2',
                                         context=context,
                                         mailbox='1001')
        self.add_me(voicemail_row1)
        self.add_me(voicemail_row2)

        expected_voicemail1 = Voicemail(
            id=voicemail_row1.uniqueid,
            name='voicemail1',
            context=context,
            number='1000',
            attach_audio=False,
            delete_messages=False,
            ask_password=True,
        )

        expected_voicemail2 = Voicemail(
            id=voicemail_row2.uniqueid,
            name='voicemail2',
            context=context,
            number='1001',
            attach_audio=False,
            delete_messages=False,
            ask_password=True,
        )

        result = voicemail_dao.search()

        assert_that(result.total, equal_to(2))
        assert_that(result.items, contains_inanyorder(
            self._has_voicemail(expected_voicemail1),
            self._has_voicemail(expected_voicemail2)
        ))

    def test_search_with_limit(self):
        context = 'default'

        voicemail_row1 = VoicemailSchema(fullname='voicemail1',
                                         context=context,
                                         mailbox='1000')

        voicemail_row2 = VoicemailSchema(fullname='voicemail2',
                                         context=context,
                                         mailbox='1001')

        self.add_me(voicemail_row1)
        self.add_me(voicemail_row2)

        result = voicemail_dao.search(limit=1)

        assert_that(result.total, equal_to(2))
        assert_that(result.items, contains(instance_of(Voicemail)))

    def test_search_with_order(self):
        context = 'default'

        voicemail_row1 = VoicemailSchema(fullname='voicemail1',
                                         context=context,
                                         mailbox='1001')

        voicemail_row2 = VoicemailSchema(fullname='voicemail2',
                                         context=context,
                                         mailbox='1000')

        self.add_me(voicemail_row1)
        self.add_me(voicemail_row2)

        expected_voicemail1 = Voicemail(
            id=voicemail_row1.uniqueid,
            name='voicemail1',
            context=context,
            number='1001',
            attach_audio=False,
            delete_messages=False,
            ask_password=True,
        )

        expected_voicemail2 = Voicemail(
            id=voicemail_row2.uniqueid,
            name='voicemail2',
            context=context,
            number='1000',
            attach_audio=False,
            delete_messages=False,
            ask_password=True,
        )

        result = voicemail_dao.search(order='name')

        assert_that(result.total, equal_to(2))
        assert_that(result.items, contains(self._has_voicemail(expected_voicemail1),
                                           self._has_voicemail(expected_voicemail2)))

    def test_search_with_order_and_direction(self):
        context = 'default'

        voicemail_row1 = VoicemailSchema(fullname='voicemail1',
                                         context=context,
                                         mailbox='1001')

        voicemail_row2 = VoicemailSchema(fullname='voicemail2',
                                         context=context,
                                         mailbox='1000')

        self.add_me(voicemail_row1)
        self.add_me(voicemail_row2)

        expected_voicemail1 = Voicemail(
            id=voicemail_row1.uniqueid,
            name='voicemail1',
            context=context,
            number='1001',
            attach_audio=False,
            delete_messages=False,
            ask_password=True,
        )

        expected_voicemail2 = Voicemail(
            id=voicemail_row2.uniqueid,
            name='voicemail2',
            context=context,
            number='1000',
            attach_audio=False,
            delete_messages=False,
            ask_password=True,
        )

        result = voicemail_dao.search(order='name', direction='desc')

        assert_that(result.total, equal_to(2))
        assert_that(result.items, contains(self._has_voicemail(expected_voicemail2),
                                           self._has_voicemail(expected_voicemail1)))

    def test_search_with_skip_and_order(self):
        context = 'default'

        voicemail_row1 = VoicemailSchema(fullname='voicemail1',
                                         context=context,
                                         mailbox='1001')

        voicemail_row2 = VoicemailSchema(fullname='voicemail2',
                                         context=context,
                                         mailbox='1000')

        self.add_me(voicemail_row1)
        self.add_me(voicemail_row2)

        expected_voicemail2 = Voicemail(
            id=voicemail_row2.uniqueid,
            name='voicemail2',
            context=context,
            number='1000',
            attach_audio=False,
            delete_messages=False,
            ask_password=True,
        )

        result = voicemail_dao.search(skip=1, order='name')

        assert_that(result.total, equal_to(2))
        assert_that(result.items, contains(self._has_voicemail(expected_voicemail2)))

    def test_search_with_skip_and_limit(self):
        context = 'default'

        voicemail_row1 = VoicemailSchema(fullname='voicemail1',
                                         context=context,
                                         mailbox='1001')

        voicemail_row2 = VoicemailSchema(fullname='voicemail2',
                                         context=context,
                                         mailbox='1000')

        voicemail_row3 = VoicemailSchema(fullname='voicemail3',
                                         context=context,
                                         mailbox='1002')

        self.add_me(voicemail_row1)
        self.add_me(voicemail_row2)
        self.add_me(voicemail_row3)

        expected_voicemail2 = Voicemail(
            id=voicemail_row2.uniqueid,
            name='voicemail2',
            context=context,
            number='1000',
            attach_audio=False,
            delete_messages=False,
            ask_password=True,
        )

        result = voicemail_dao.search(skip=1, limit=1, order='name')

        assert_that(result.total, equal_to(3))
        assert_that(result.items, contains(self._has_voicemail(expected_voicemail2)))

    def test_search_with_search(self):
        context = 'default'

        voicemail_row1 = VoicemailSchema(fullname='voicemail1',
                                         context=context,
                                         mailbox='1001')

        voicemail_row2 = VoicemailSchema(fullname='donotappear',
                                         context=context,
                                         mailbox='1000')

        voicemail_row3 = VoicemailSchema(fullname='voicemail3',
                                         context=context,
                                         mailbox='1002')

        self.add_me(voicemail_row1)
        self.add_me(voicemail_row2)
        self.add_me(voicemail_row3)

        expected_voicemail1 = Voicemail(
            id=voicemail_row1.uniqueid,
            name='voicemail1',
            context=context,
            number='1001',
            attach_audio=False,
            delete_messages=False,
            ask_password=True,
        )

        expected_voicemail3 = Voicemail(
            id=voicemail_row3.uniqueid,
            name='voicemail3',
            context=context,
            number='1002',
            attach_audio=False,
            delete_messages=False,
            ask_password=True,
        )

        result = voicemail_dao.search(search='VOICEMAIL')

        assert_that(result.total, equal_to(2))
        assert_that(result.items, contains(
            self._has_voicemail(expected_voicemail1),
            self._has_voicemail(expected_voicemail3)))

    def test_search_with_all_parameters(self):
        context = 'default'

        voicemail_row1 = VoicemailSchema(fullname='donotappear',
                                         context=context,
                                         mailbox='1001')

        voicemail_row2 = VoicemailSchema(fullname='voicemail2',
                                         context=context,
                                         mailbox='1002')

        voicemail_row3 = VoicemailSchema(fullname='voicemail3',
                                         context=context,
                                         mailbox='1003')

        voicemail_row4 = VoicemailSchema(fullname='voicemail4',
                                         context=context,
                                         mailbox='1004')

        voicemail_row5 = VoicemailSchema(fullname='voicemail5',
                                         context=context,
                                         mailbox='1005')

        self.add_me(voicemail_row1)
        self.add_me(voicemail_row2)
        self.add_me(voicemail_row3)
        self.add_me(voicemail_row4)
        self.add_me(voicemail_row5)

        expected_voicemail4 = Voicemail(
            id=voicemail_row4.uniqueid,
            name='voicemail4',
            context=context,
            number='1004',
            attach_audio=False,
            delete_messages=False,
            ask_password=True,
        )

        expected_voicemail3 = Voicemail(
            id=voicemail_row3.uniqueid,
            name='voicemail3',
            context=context,
            number='1003',
            attach_audio=False,
            delete_messages=False,
            ask_password=True,
        )

        result = voicemail_dao.search(search='VOICEMAIL',
                                      order='name',
                                      direction='desc',
                                      skip=1,
                                      limit=2)

        assert_that(result.total, equal_to(4))
        assert_that(result.items, contains(
            self._has_voicemail(expected_voicemail4),
            self._has_voicemail(expected_voicemail3)))


class TestGetVoicemail(DAOTestCase):

    def test_get_by_number_context_with_no_voicemail(self):
        self.assertRaises(NotFoundError, voicemail_dao.get_by_number_context, '42', 'my_context')

    def test_get_by_number_context_with_wrong_context(self):
        number = '42'
        context = 'default'

        voicemail_row = VoicemailSchema(context=context,
                                        mailbox=number)
        self.add_me(voicemail_row)

        self.assertRaises(NotFoundError, voicemail_dao.get_by_number_context, number, 'bad_context')

    def test_get_by_number_context_with_one_voicemail(self):
        number = '42'
        context = 'default'
        number_at_context = '42@default'

        voicemail_row = VoicemailSchema(context=context,
                                        mailbox=number)
        self.add_me(voicemail_row)

        result = voicemail_dao.get_by_number_context(number, context)

        self.assertEquals(result.number, number)
        self.assertEquals(result.context, context)
        self.assertEquals(result.number_at_context, number_at_context)

    def test_get_by_number_context_with_two_voicemails(self):
        number = '42'
        context = 'default'
        number_at_context = '42@default'

        first_voicemail = VoicemailSchema(context=context,
                                          mailbox='43')
        second_voicemail = VoicemailSchema(context=context,
                                           mailbox=number)

        self.add_me(first_voicemail)
        self.add_me(second_voicemail)

        result = voicemail_dao.get_by_number_context(number, context)
        self.assertEquals(result.number, number)
        self.assertEquals(result.context, context)
        self.assertEquals(result.number_at_context, number_at_context)

    def test_get_with_no_voicemail(self):
        voicemail_id = 42

        self.assertRaises(NotFoundError, voicemail_dao.get, voicemail_id)

    def test_get_with_one_voicemail(self):
        name = 'voicemail name'
        number = '42'
        context = 'context-42'
        voicemail_row = VoicemailSchema(
            context=context,
            mailbox=number,
            fullname=name,
        )
        self.add_me(voicemail_row)
        voicemail_id = voicemail_row.uniqueid

        expected_voicemail = Voicemail(
            name=name,
            number=number,
            context=context,
            id=voicemail_id,
            attach_audio=False,
            delete_messages=False,
            ask_password=True,
            enabled=True,
            options=[]
        )

        voicemail = voicemail_dao.get(voicemail_id)

        self.assertEquals(expected_voicemail, voicemail)

    def test_get_with_one_voicemail_and_all_properties(self):
        name = 'voicemail name'
        number = '42'
        context = 'context-42'
        options = [['saycid', 'yes'],
                   ['emailsubject', 'subject']]

        voicemail_row = VoicemailSchema(
            fullname=name,
            mailbox=number,
            context=context,
            password='password',
            email='email',
            pager='pager',
            language='fr_FR',
            tz='eu-fr',
            maxmsg=1,
            attach=1,
            deletevoicemail=None,
            skipcheckpass=0,
            options=options
        )

        self.add_me(voicemail_row)

        voicemail = voicemail_dao.get(voicemail_row.uniqueid)

        self.assertEquals(voicemail.id, voicemail_row.uniqueid)
        self.assertEquals(voicemail.name, voicemail_row.fullname)
        self.assertEquals(voicemail.number, voicemail_row.mailbox)
        self.assertEquals(voicemail.context, voicemail_row.context)
        self.assertEquals(voicemail.password, voicemail_row.password)
        self.assertEquals(voicemail.email, voicemail_row.email)
        self.assertEquals(voicemail.pager, voicemail_row.pager)
        self.assertEquals(voicemail.language, voicemail_row.language)
        self.assertEquals(voicemail.timezone, voicemail_row.tz)
        self.assertEquals(voicemail.max_messages, voicemail_row.maxmsg)
        self.assertEquals(voicemail.attach_audio, True)
        self.assertEquals(voicemail.delete_messages, False)
        self.assertEquals(voicemail.ask_password, True)
        self.assertEquals(voicemail.options, options)


class TestCreateVoicemail(DAOTestCase):

    def test_create(self):
        name = 'voicemail'
        number = '42'
        context = 'default'

        voicemail = Voicemail(name=name,
                              number=number,
                              context=context)

        created_voicemail = voicemail_dao.create(voicemail)

        row = (self.session.query(VoicemailSchema)
               .filter(VoicemailSchema.mailbox == number)
               .first())
        self.assertEquals(row.uniqueid, created_voicemail.id)
        self.assertEquals(row.fullname, name)
        self.assertEquals(row.mailbox, number)
        self.assertEquals(row.context, context)
        self.assertEquals(row.options, [])

    def test_create_with_all_parameters(self):
        options = [['saycid', 'yes'],
                   ['emailsubject', 'subject']]

        voicemail = Voicemail(
            name='voicemail',
            number='1000',
            context='context',
            password='password',
            email='email',
            pager='pager',
            language='fr_FR',
            timezone='eu-fr',
            max_messages=1,
            attach_audio=True,
            delete_messages=True,
            ask_password=True,
            enabled=True,
            options=options
        )

        created_voicemail = voicemail_dao.create(voicemail)

        row = (self.session.query(VoicemailSchema)
               .filter(VoicemailSchema.mailbox == voicemail.number)
               .first())

        self.assertEquals(row.uniqueid, created_voicemail.id)
        self.assertEquals(row.fullname, 'voicemail')
        self.assertEquals(row.mailbox, '1000')
        self.assertEquals(row.context, 'context')
        self.assertEquals(row.password, 'password')
        self.assertEquals(row.email, 'email')
        self.assertEquals(row.pager, 'pager')
        self.assertEquals(row.language, 'fr_FR')
        self.assertEquals(row.tz, 'eu-fr')
        self.assertEquals(row.maxmsg, 1)
        self.assertEquals(row.attach, 1)
        self.assertEquals(row.deletevoicemail, 1)
        self.assertEquals(row.skipcheckpass, 0)
        self.assertEquals(row.commented, 0)
        self.assertEquals(row.options, options)

    @mocked_dao_session
    def test_create_with_database_error(self, session):
        session.commit.side_effect = SQLAlchemyError()

        name = 'voicemail'
        number = '42'
        context = 'default'

        voicemail = Voicemail(name=name,
                              number=number,
                              context=context)

        self.assertRaises(DataError, voicemail_dao.create, voicemail)
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()


class TestEditVoicemail(DAOTestCase):

    def test_edit(self):
        number = '42'
        context = 'default'
        expected_name = 'totitu'

        voicemail = self.add_voicemail(mailbox=number,
                                       context=context)

        voicemail = voicemail_dao.get(voicemail.uniqueid)
        voicemail.name = expected_name

        voicemail_dao.edit(voicemail)

        row = (self.session.query(VoicemailSchema)
               .filter(VoicemailSchema.uniqueid == voicemail.id)
               .first())

        self.assertEquals(row.uniqueid, voicemail.id)
        self.assertEquals(row.fullname, expected_name)
        self.assertEquals(row.mailbox, number)
        self.assertEquals(row.context, context)

    def test_edit_with_all_parameters(self):
        expected_options = [['envelope', 'yes'],
                            ['minsecs', '10']]

        voicemail_row = self.add_voicemail(
            mailbox='1000',
            context='default',
            password='password',
            email='email@email',
            pager='pager@email',
            language='fr_FR',
            tz='eu-fr',
            attach=0,
            deletevoicemail=0,
            maxmsg=0,
            skipcheckpass=0,
            commented=0,
            options=[['saycid', 'yes']]
        )

        voicemail = voicemail_dao.get(voicemail_row.uniqueid)

        voicemail.name = 'newname'
        voicemail.number = '1001'
        voicemail.password = 'newpassword'
        voicemail.email = 'newemail@email.com'
        voicemail.pager = 'newpager@email.com'
        voicemail.language = 'en_US'
        voicemail.timezone = 'en-ca'
        voicemail.max_messages = 10
        voicemail.attach_audio = True
        voicemail.delete_messages = True
        voicemail.ask_password = False
        voicemail.enabled = False
        voicemail.options = expected_options

        voicemail_dao.edit(voicemail)

        row = (self.session.query(VoicemailSchema)
               .filter(VoicemailSchema.uniqueid == voicemail.id)
               .first())

        self.assertEquals(row.uniqueid, voicemail.id)
        self.assertEquals(row.fullname, voicemail.name)
        self.assertEquals(row.mailbox, voicemail.number)
        self.assertEquals(row.context, voicemail.context)
        self.assertEquals(row.password, voicemail.password)
        self.assertEquals(row.email, voicemail.email)
        self.assertEquals(row.pager, voicemail.pager)
        self.assertEquals(row.language, voicemail.language)
        self.assertEquals(row.tz, voicemail.timezone)
        self.assertEquals(row.maxmsg, voicemail.max_messages)
        self.assertEquals(row.attach, voicemail.attach_audio)
        self.assertEquals(row.deletevoicemail, voicemail.delete_messages)
        self.assertEquals(row.skipcheckpass, 1)
        self.assertEquals(row.commented, 1)
        self.assertEquals(row.options, expected_options)

    @mocked_dao_session
    def test_edit_with_database_error(self, session):
        session.commit.side_effect = SQLAlchemyError()

        name = 'voicemail'
        number = '42'
        context = 'default'

        voicemail = Voicemail(name=name,
                              number=number,
                              context=context)

        self.assertRaises(DataError, voicemail_dao.edit, voicemail)
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()


class VoicemailTestCase(DAOTestCase):

    def create_voicemail(self, number, context):
        voicemail = self.mock_voicemail(number, context)
        voicemail_id = self.prepare_database(voicemail)
        voicemail.id = voicemail_id

        return voicemail

    def mock_voicemail(self, number, context):
        voicemail = Mock(Voicemail)
        voicemail.number = number
        voicemail.context = context
        voicemail.number_at_context = '%s@%s' % (number, context)
        return voicemail

    def prepare_database(self, voicemail):
        voicemail_row = VoicemailSchema(context=voicemail.context,
                                        mailbox=voicemail.number)

        self.add_me(voicemail_row)


class TestVoicemailDelete(VoicemailTestCase):

    def test_delete(self):
        voicemail = self.create_voicemail(number='42', context='default')
        voicemail_dao.delete(voicemail)

        self.check_voicemail_table(voicemail.id)

    def test_delete_with_dialaction(self):
        voicemail = self.create_voicemail(number='42', context='default')
        incall = self.create_incall_for_voicemail(voicemail, did='42', context='from-extern')

        voicemail_dao.delete(voicemail)

        self.check_voicemail_table(voicemail.id)
        self.check_incall_associated_to_nothing(incall.id)

    @mocked_dao_session
    def test_delete_with_database_error(self, session):
        session.commit.side_effect = SQLAlchemyError()

        voicemail = self.mock_voicemail(number='42', context='default')
        voicemail.id = 1

        self.assertRaises(DataError, voicemail_dao.delete, voicemail)
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()

    def create_incall_for_voicemail(self, voicemail, did, context):
        incall_row = IncallSchema(exten=did,
                                  context=context,
                                  description='')
        self.add_me(incall_row)

        dial_action_row = DialactionSchema(event='answer',
                                           category='incall',
                                           categoryval=str(incall_row.id),
                                           action='voicemail',
                                           actionarg1=str(voicemail.id),
                                           linked=1)
        self.add_me(dial_action_row)

        return incall_row

    def check_voicemail_table(self, voicemail_id):
        voicemail_row = (self.session.query(VoicemailSchema)
                         .filter(VoicemailSchema.uniqueid == voicemail_id)
                         .first())

        self.assertEquals(voicemail_row, None)

    def check_incall_associated_to_nothing(self, incall_id):
        count = (self.session.query(DialactionSchema)
                 .filter(DialactionSchema.category == 'incall')
                 .filter(DialactionSchema.categoryval == str(incall_id))
                 .filter(DialactionSchema.linked == 0)
                 .count())

        self.assertTrue(count > 0, "incall still associated to a dialaction")


class TestFindEnabledVoicemails(DAOTestCase):

    def build_voicemail(self, **kwargs):
        voicemail_row = self.add_voicemail(**kwargs)

        return Voicemail(id=voicemail_row.uniqueid,
                         name=voicemail_row.fullname,
                         number=voicemail_row.mailbox,
                         context=voicemail_row.context,
                         attach_audio=bool(voicemail_row.attach),
                         delete_messages=bool(voicemail_row.deletevoicemail),
                         ask_password=not bool(voicemail_row.skipcheckpass),
                         enabled=not bool(voicemail_row.commented),
                         options=voicemail_row.options)

    def test_given_no_voicemails_then_returns_empty_list(self):
        result = voicemail_dao.find_enabled_voicemails()

        assert_that(result, contains())

    def test_given_one_enabled_voicemail_then_returns_list_with_one_item(self):
        expected = contains(self.build_voicemail())

        result = voicemail_dao.find_enabled_voicemails()
        assert_that(result, expected)

    def test_given_one_disabled_voicemail_then_returns_empty_list(self):
        self.build_voicemail(commented=1)

        result = voicemail_dao.find_enabled_voicemails()
        assert_that(result, contains())

    def test_given_multiple_voicemails_when_queried_then_results_sorted_by_context_and_number(self):
        voicemail1 = self.build_voicemail(mailbox='1001', context='vmctx')
        voicemail2 = self.build_voicemail(mailbox='1000', context='vmctx')
        voicemail3 = self.build_voicemail(mailbox='1001', context='default')
        voicemail4 = self.build_voicemail(mailbox='1000', context='default')

        result = voicemail_dao.find_enabled_voicemails()
        assert_that(result, contains(voicemail4, voicemail3, voicemail2, voicemail1))
