# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from mock import Mock, patch
from hamcrest import *

from sqlalchemy.exc import SQLAlchemyError
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.voicemail import Voicemail as VoicemailSchema
from xivo_dao.alchemy.usersip import UserSIP as UserSIPSchema
from xivo_dao.alchemy.userfeatures import test_dependencies
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema
from xivo_dao.alchemy.incall import Incall as IncallSchema
from xivo_dao.alchemy.dialaction import Dialaction as DialactionSchema
from xivo_dao.data_handler.voicemail import dao as voicemail_dao
from xivo_dao.data_handler.voicemail.model import Voicemail, VoicemailOrder
from xivo_dao.data_handler.exception import ElementCreationError, \
    ElementDeletionError, ElementEditionError


class TestFindAllVoicemail(DAOTestCase):

    tables = [
        VoicemailSchema
    ]

    def setUp(self):
        self.empty_tables()

    def _has_voicemail(self, voicemail):
        matchers = []
        for field in Voicemail.FIELDS:
            matcher = has_property(field, getattr(voicemail, field))
            matchers.append(matcher)

        return all_of(instance_of(Voicemail), *matchers)

    def test_find_all_no_voicemails(self):
        result = voicemail_dao.find_all()

        assert_that(result, all_of(
            has_property('total', 0),
            has_property('items', [])))

    def test_find_all_one_voicemail(self):
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
            ask_password=False,
        )

        result = voicemail_dao.find_all()

        assert_that(result.total, equal_to(1))
        assert_that(result.items, contains(self._has_voicemail(expected_voicemail)))

    def test_find_all_two_voicemails(self):
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
            ask_password=False,
        )

        expected_voicemail2 = Voicemail(
            id=voicemail_row2.uniqueid,
            name='voicemail2',
            context=context,
            number='1001',
            attach_audio=False,
            delete_messages=False,
            ask_password=False,
        )

        result = voicemail_dao.find_all()

        assert_that(result.total, equal_to(2))
        assert_that(result.items, contains_inanyorder(
            self._has_voicemail(expected_voicemail1),
            self._has_voicemail(expected_voicemail2)
        ))

    def test_find_all_with_limit(self):
        context = 'default'

        voicemail_row1 = VoicemailSchema(fullname='voicemail1',
                                         context=context,
                                         mailbox='1000')

        voicemail_row2 = VoicemailSchema(fullname='voicemail2',
                                         context=context,
                                         mailbox='1001')

        self.add_me(voicemail_row1)
        self.add_me(voicemail_row2)

        result = voicemail_dao.find_all(limit=1)

        assert_that(result.total, equal_to(2))
        assert_that(result.items, contains(instance_of(Voicemail)))

    def test_find_all_with_order(self):
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
            ask_password=False,
        )

        expected_voicemail2 = Voicemail(
            id=voicemail_row2.uniqueid,
            name='voicemail2',
            context=context,
            number='1000',
            attach_audio=False,
            delete_messages=False,
            ask_password=False,
        )

        result = voicemail_dao.find_all(order=VoicemailOrder.name)

        assert_that(result.total, equal_to(2))
        assert_that(result.items, contains(self._has_voicemail(expected_voicemail1),
                                           self._has_voicemail(expected_voicemail2)))

    def test_find_all_with_order_and_direction(self):
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
            ask_password=False,
        )

        expected_voicemail2 = Voicemail(
            id=voicemail_row2.uniqueid,
            name='voicemail2',
            context=context,
            number='1000',
            attach_audio=False,
            delete_messages=False,
            ask_password=False,
        )

        result = voicemail_dao.find_all(order=VoicemailOrder.name, direction='desc')

        assert_that(result.total, equal_to(2))
        assert_that(result.items, contains(self._has_voicemail(expected_voicemail2),
                                           self._has_voicemail(expected_voicemail1)))

    def test_find_all_with_skip_and_order(self):
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
            ask_password=False,
        )

        result = voicemail_dao.find_all(skip=1, order=VoicemailOrder.name)

        assert_that(result.total, equal_to(2))
        assert_that(result.items, contains(self._has_voicemail(expected_voicemail2)))

    def test_find_all_with_skip_and_limit(self):
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
            ask_password=False,
        )

        result = voicemail_dao.find_all(skip=1, limit=1, order=VoicemailOrder.name)

        assert_that(result.total, equal_to(3))
        assert_that(result.items, contains(self._has_voicemail(expected_voicemail2)))

    def test_find_all_with_search(self):
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
            ask_password=False,
        )

        expected_voicemail3 = Voicemail(
            id=voicemail_row3.uniqueid,
            name='voicemail3',
            context=context,
            number='1002',
            attach_audio=False,
            delete_messages=False,
            ask_password=False,
        )

        result = voicemail_dao.find_all(search='VOICEMAIL')

        assert_that(result.total, equal_to(2))
        assert_that(result.items, contains(
            self._has_voicemail(expected_voicemail1),
            self._has_voicemail(expected_voicemail3)))

    def test_find_all_with_all_parameters(self):
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
            ask_password=False,
        )

        expected_voicemail3 = Voicemail(
            id=voicemail_row3.uniqueid,
            name='voicemail3',
            context=context,
            number='1003',
            attach_audio=False,
            delete_messages=False,
            ask_password=False,
        )

        result = voicemail_dao.find_all(search='VOICEMAIL',
                                        order=VoicemailOrder.name,
                                        direction='desc',
                                        skip=1,
                                        limit=2)

        assert_that(result.total, equal_to(4))
        assert_that(result.items, contains(
            self._has_voicemail(expected_voicemail4),
            self._has_voicemail(expected_voicemail3)))


class TestGetVoicemail(DAOTestCase):

    tables = [
        VoicemailSchema,
        UserSIPSchema,
        UserSchema,
    ] + test_dependencies

    def setUp(self):
        self.empty_tables()

    def test_get_by_number_context_with_no_voicemail(self):
        self.assertRaises(LookupError, voicemail_dao.get_by_number_context, '42', 'my_context')

    def test_get_by_number_context_with_wrong_context(self):
        number = '42'
        context = 'default'

        voicemail_row = VoicemailSchema(context=context,
                                        mailbox=number)
        self.add_me(voicemail_row)

        self.assertRaises(LookupError, voicemail_dao.get_by_number_context, number, 'bad_context')

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

        self.assertRaises(LookupError, voicemail_dao.get, voicemail_id)

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
            ask_password=False
        )

        voicemail = voicemail_dao.get(voicemail_id)

        self.assertEquals(expected_voicemail, voicemail)

    def test_get_with_one_voicemail_and_all_properties(self):
        name = 'voicemail name'
        number = '42'
        context = 'context-42'

        voicemail_row = VoicemailSchema(
            fullname=name,
            mailbox=number,
            context=context,
            password='password',
            email='email',
            language='fr_FR',
            tz='eu-fr',
            maxmsg=1,
            attach=1,
            deletevoicemail=None,
            skipcheckpass=0
        )

        self.add_me(voicemail_row)

        voicemail = voicemail_dao.get(voicemail_row.uniqueid)

        self.assertEquals(voicemail.id, voicemail_row.uniqueid)
        self.assertEquals(voicemail.name, voicemail_row.fullname)
        self.assertEquals(voicemail.number, voicemail_row.mailbox)
        self.assertEquals(voicemail.context, voicemail_row.context)
        self.assertEquals(voicemail.password, voicemail_row.password)
        self.assertEquals(voicemail.email, voicemail_row.email)
        self.assertEquals(voicemail.language, voicemail_row.language)
        self.assertEquals(voicemail.timezone, voicemail_row.tz)
        self.assertEquals(voicemail.max_messages, voicemail_row.maxmsg)
        self.assertEquals(voicemail.attach_audio, True)
        self.assertEquals(voicemail.delete_messages, False)
        self.assertEquals(voicemail.ask_password, False)


class TestCreateVoicemail(DAOTestCase):

    tables = [
        VoicemailSchema,
    ]

    def setUp(self):
        self.empty_tables()

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

    @patch('xivo_dao.helpers.db_manager.AsteriskSession')
    def test_create_with_database_error(self, Session):
        session = Mock()
        session.commit.side_effect = SQLAlchemyError()
        Session.return_value = session

        name = 'voicemail'
        number = '42'
        context = 'default'

        voicemail = Voicemail(name=name,
                              number=number,
                              context=context)

        self.assertRaises(ElementCreationError, voicemail_dao.create, voicemail)
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()


class TestEditVoicemail(DAOTestCase):

    tables = [
        VoicemailSchema,
    ]

    def setUp(self):
        self.empty_tables()

    def test_edit(self):
        number = '42'
        context = 'default'
        expected_name = 'totitu'

        voicemail = self.add_voicemail(number=number,
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
        voicemail_row = self.add_voicemail(
            number='1000',
            context='default',
            password='password',
            email='email@email',
            language='fr_FR',
            tz='eu-fr',
            attach=0,
            deletevoicemail=0,
            maxmsg=0,
            skipcheckpass=0
        )

        voicemail = voicemail_dao.get(voicemail_row.uniqueid)

        voicemail.name = 'newname'
        voicemail.number = '1001'
        voicemail.password = 'newpassword'
        voicemail.email = 'newemail@email.com'
        voicemail.language = 'en_US'
        voicemail.timezone = 'en-ca'
        voicemail.max_messages = 10
        voicemail.attach_audio = True
        voicemail.delete_messages = True
        voicemail.ask_password = True

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
        self.assertEquals(row.language, voicemail.language)
        self.assertEquals(row.tz, voicemail.timezone)
        self.assertEquals(row.maxmsg, voicemail.max_messages)
        self.assertEquals(row.attach, voicemail.attach_audio)
        self.assertEquals(row.deletevoicemail, voicemail.delete_messages)
        self.assertEquals(row.skipcheckpass, voicemail.ask_password)

    @patch('xivo_dao.helpers.db_manager.AsteriskSession')
    def test_edit_with_database_error(self, Session):
        session = Mock()
        session.commit.side_effect = SQLAlchemyError()
        Session.return_value = session

        name = 'voicemail'
        number = '42'
        context = 'default'

        voicemail = Voicemail(name=name,
                              number=number,
                              context=context)

        self.assertRaises(ElementEditionError, voicemail_dao.edit, voicemail)
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()


class VoicemailTestCase(DAOTestCase):

    def setUp(self):
        self.empty_tables()

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

    tables = [
        VoicemailSchema,
        IncallSchema,
        DialactionSchema
    ]

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

    @patch('xivo_dao.helpers.db_manager.AsteriskSession')
    def test_delete_with_database_error(self, Session):
        session = Mock()
        session.commit.side_effect = SQLAlchemyError()
        Session.return_value = session

        voicemail = self.mock_voicemail(number='42', context='default')
        voicemail.id = 1

        self.assertRaises(ElementDeletionError, voicemail_dao.delete, voicemail)
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


class TestIsVoicemailLinked(VoicemailTestCase):

    tables = [
        VoicemailSchema,
        UserSchema,
    ] + test_dependencies

    def test_is_voicemail_linked_no_links(self):
        voicemail = self.create_voicemail(number='42', context='default')

        result = voicemail_dao.is_voicemail_linked(voicemail)

        self.assertFalse(result)

    def test_is_voicemail_linked_with_user(self):
        voicemail = self.create_voicemail(number='42', context='default')
        self.create_user_with_voicemail(voicemail,
                                        firstname='Joe')

        result = voicemail_dao.is_voicemail_linked(voicemail)

        self.assertTrue(result)

    def create_user_with_voicemail(self, voicemail, firstname='John', lastname='Doe'):
        user_row = self.add_user(firstname=firstname,
                                 lastname=lastname)
        self.link_user_and_voicemail(user_row, voicemail.id)
