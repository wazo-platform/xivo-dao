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
from xivo_dao.alchemy.sccpdevice import SCCPDevice as SCCPDeviceSchema
from xivo_dao.alchemy.userfeatures import test_dependencies
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema
from xivo_dao.data_handler.voicemail import dao as voicemail_dao
from xivo_dao.data_handler.voicemail.model import Voicemail, VoicemailOrder
from xivo_dao.data_handler.exception import ElementCreationError, \
    ElementDeletionError


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


class TestVoicemailDeleteSIP(DAOTestCase):

    tables = [
        VoicemailSchema,
        UserSIPSchema,
        SCCPDeviceSchema,
        UserSchema,
    ] + test_dependencies

    def setUp(self):
        self.empty_tables()

    @patch('xivo_dao.helpers.sysconfd_connector.delete_voicemail_storage')
    def test_delete_from_sip_user(self, delete_voicemail_storage):
        voicemail = Mock(Voicemail)
        voicemail.number = '42'
        voicemail.context = 'default'
        voicemail.number_at_context = '42@default'

        user_id, user_sip_id, voicemail_id = self._prepare_database(voicemail)
        voicemail.id = voicemail_id

        voicemail_dao.delete(voicemail)

        self._check_user_table(user_id)
        self._check_user_sip_table(user_sip_id)
        self._check_voicemail_table(voicemail_id)
        delete_voicemail_storage.assert_called_once_with(voicemail.context, voicemail.number)

    @patch('xivo_dao.helpers.sysconfd_connector.delete_voicemail_storage')
    @patch('xivo_dao.helpers.db_manager.AsteriskSession')
    def test_delete_with_database_error(self, Session, delete_voicemail_storage):
        session = Mock()
        session.commit.side_effect = SQLAlchemyError()
        Session.return_value = session

        voicemail = Mock(Voicemail)
        voicemail.number = '42'
        voicemail.context = 'default'
        voicemail.number_at_context = '42@default'
        voicemail.id = 1

        self.assertRaises(ElementDeletionError, voicemail_dao.delete, voicemail)
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()
        delete_voicemail_storage.assert_called_once_with(voicemail.context, voicemail.number)

    def _prepare_database(self, voicemail):
        voicemail_row = VoicemailSchema(context=voicemail.context,
                                        mailbox=voicemail.number)

        self.add_me(voicemail_row)

        user_row = UserSchema(firstname='John',
                              lastname='Doe',
                              voicemailtype='asterisk',
                              voicemailid=voicemail_row.uniqueid,
                              language='fr_FR')

        self.add_me(user_row)

        user_sip_row = UserSIPSchema(name='bla',
                                     type='friend',
                                     mailbox='42@default')

        self.add_me(user_sip_row)

        return (user_row.id, user_sip_row.id, voicemail_row.uniqueid)

    def _check_user_table(self, user_id):
        user_row = (self.session.query(UserSchema)
                    .filter(UserSchema.id == user_id)
                    .first())

        self.assertEquals(user_row.voicemailid, None)

    def _check_user_sip_table(self, user_sip_id):

        user_sip_row = (self.session.query(UserSIPSchema)
                        .filter(UserSIPSchema.id == user_sip_id)
                        .first())

        self.assertEquals(user_sip_row.mailbox, None)

    def _check_voicemail_table(self, voicemail_id):

        voicemail_row = (self.session.query(VoicemailSchema)
                         .filter(VoicemailSchema.uniqueid == voicemail_id)
                         .first())

        self.assertEquals(voicemail_row, None)


class TestVoicemailDeleteSCCP(DAOTestCase):

    tables = [
        VoicemailSchema,
        UserSIPSchema,
        SCCPDeviceSchema,
        UserSchema,
    ] + test_dependencies

    def setUp(self):
        self.empty_tables()

    @patch('xivo_dao.helpers.sysconfd_connector.delete_voicemail_storage')
    def test_delete_from_sccp_user(self, delete_voicemail_storage):
        voicemail = Mock(Voicemail)
        voicemail.number = '42'
        voicemail.context = 'default'
        voicemail.number_at_context = '42@default'

        user_id, sccp_device_id, voicemail_id = self._prepare_database(voicemail)
        voicemail.id = voicemail_id

        voicemail_dao.delete(voicemail)

        self._check_user_table(user_id)
        self._check_voicemail_table(voicemail_id)
        delete_voicemail_storage.assert_called_once_with(voicemail.context, voicemail.number)

    def _prepare_database(self, voicemail):
        voicemail_row = VoicemailSchema(context=voicemail.context,
                                        mailbox=voicemail.number)

        self.add_me(voicemail_row)

        user_row = UserSchema(firstname='John',
                              lastname='Doe',
                              voicemailtype='asterisk',
                              voicemailid=voicemail_row.uniqueid,
                              language='fr_FR')

        self.add_me(user_row)

        sccp_device_row = SCCPDeviceSchema(name='SEPabcd',
                                           device='SEPabcd',
                                           voicemail='42')

        self.add_me(sccp_device_row)

        return (user_row.id, sccp_device_row.id, voicemail_row.uniqueid)

    def _check_user_table(self, user_id):
        user_row = (self.session.query(UserSchema)
                    .filter(UserSchema.id == user_id)
                    .first())

        self.assertEquals(user_row.voicemailid, None)

    def _check_voicemail_table(self, voicemail_id):

        voicemail_row = (self.session.query(VoicemailSchema)
                         .filter(VoicemailSchema.uniqueid == voicemail_id)
                         .first())

        self.assertEquals(voicemail_row, None)
