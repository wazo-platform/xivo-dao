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

from hamcrest import assert_that, all_of, has_property, is_not, has_length
from hamcrest.core import equal_to
from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.alchemy.ctiphonehintsgroup import CtiPhoneHintsGroup
from xivo_dao.alchemy.ctipresences import CtiPresences
from xivo_dao.alchemy.linefeatures import LineFeatures as LineSchema
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema
from xivo_dao.data_handler.line import dao as line_dao
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.usersip import UserSIP as UserSIPSchema
from xivo_dao.alchemy.useriax import UserIAX as UserIAXSchema
from xivo_dao.alchemy.usercustom import UserCustom as UserCustomSchema
from xivo_dao.alchemy.sccpline import SCCPLine as SCCPLineSchema
from xivo_dao.data_handler.line.model import LineSIP, LineSCCP, LineIAX, LineCUSTOM
from sqlalchemy.sql.expression import and_
from xivo_dao.data_handler.exception import ElementNotExistsError, \
    ElementCreationError
from sqlalchemy.exc import SQLAlchemyError
from mock import patch, Mock


class TestLineDao(DAOTestCase):

    tables = [
        UserSchema,
        CtiProfile,
        CtiPresences,
        CtiPhoneHintsGroup,
        Extension,
        LineSchema,
        UserLine,
        UserSIPSchema,
        UserIAXSchema,
        UserCustomSchema,
        SCCPLineSchema
    ]

    def setUp(self):
        self.empty_tables()

    def test_get(self):
        line_name = 'sdklfj'

        line = self.add_line(name=line_name)

        line = line_dao.get(line.id)

        assert_that(line.name, equal_to(line_name))

    def test_get_no_line(self):
        self.assertRaises(ElementNotExistsError, line_dao.get, 666)

    def test_get_by_user_id(self):
        line_name = 'sdklfj'

        line = self.add_line(name=line_name)
        user = self.add_user()
        self.add_user_line(user_id=user.id,
                           line_id=line.id)

        line = line_dao.get_by_user_id(user.id)

        assert_that(line.name, equal_to(line_name))

    def test_get_by_user_id_no_user(self):
        self.assertRaises(ElementNotExistsError, line_dao.get_by_user_id, 666)

    def test_get_by_user_id_commented(self):
        line_name = 'sdklfj'

        line = self.add_line(name=line_name, commented=1)
        user = self.add_user()
        self.add_user_line(user_id=user.id, line_id=line.id)

        self.assertRaises(ElementNotExistsError, line_dao.get_by_user_id, user.id)

    def test_get_by_number_context(self):
        line_name = 'sdklfj'
        number = '1235'
        context = 'notdefault'

        line = self.add_line(name=line_name, number=number, context=context)
        self.add_extension(exten=number,
                           context=context,
                           type='user',
                           typeval=str(line.id))


        line = line_dao.get_by_number_context(number, context)

        assert_that(line.name, equal_to(line_name))
        assert_that(line.number, equal_to(number))
        assert_that(line.context, equal_to(context))

    def test_get_by_number_context_no_line(self):
        self.assertRaises(ElementNotExistsError, line_dao.get_by_number_context, '1234', 'default')

    def test_get_by_number_context_commented(self):
        line_name = 'sdklfj'
        number = '1235'
        context = 'notdefault'

        line = self.add_line(name=line_name, commented=1)
        self.add_extension(exten=number,
                           context=context,
                           type='user',
                           typeval=str(line.id))

        self.assertRaises(ElementNotExistsError, line_dao.get_by_number_context, number, context)

    def test_provisioning_id_exists(self):
        provd_id = 123456
        self.add_line(provisioningid=provd_id)

        result = line_dao.provisioning_id_exists(provd_id)

        assert_that(result, equal_to(True))

    def test_provisioning_id_does_not_exist(self):
        result = line_dao.provisioning_id_exists(123456)

        assert_that(result, equal_to(False))

    def test_create_sip_line_with_no_extension(self):
        line = LineSIP(protocol='sip',
                       context='default',
                       provisioningid=123456)

        line_created = line_dao.create(line)

        assert_that(line_created, is_not(has_property('number')))

    def test_generate_random_hash_no_sip_user(self):
        generated_hash = line_dao.generate_random_hash(self.session, UserSIPSchema.name)

        assert_that(generated_hash, has_length(8))

    @patch('xivo_dao.data_handler.line.dao._random_hash')
    def test_generate_random_hash_same_sip_user(self, random_hash):
        existing_hash = 'abcd'
        expected_hash = 'abcdefgh'
        self.add_usersip(name=existing_hash)

        random_hash.side_effect = [existing_hash, expected_hash]

        generated_hash = line_dao.generate_random_hash(self.session, UserSIPSchema.name)

        assert_that(generated_hash, equal_to(expected_hash))

    @patch('xivo_dao.helpers.db_manager.AsteriskSession')
    def test_create_sip_line_with_error_from_dao(self, Session):
        session = Mock()
        session.commit.side_effect = SQLAlchemyError()
        Session.return_value = session

        name = 'line'
        context = 'toto'
        secret = '1234'

        line = LineSIP(name=name,
                       context=context,
                       username=name, secret=secret)

        self.assertRaises(ElementCreationError, line_dao.create, line)
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()

    def test_create_sip_line(self):
        line = LineSIP(protocol='sip',
                       context='default',
                       number='1000',
                       provisioningid=123456)

        line_created = line_dao.create(line)

        result_protocol = (self.session.query(UserSIPSchema)
                           .filter(UserSIPSchema.id == line_created.protocolid)
                           .first())
        result_line = (self.session.query(LineSchema)
                       .filter(LineSchema.id == line_created.id)
                       .first())
        result_extension = (self.session.query(Extension)
                            .filter(and_(Extension.context == line_created.context,
                                         Extension.exten == line_created.number))
                            .first())

        assert_that(result_line, all_of(
            has_property('protocol', 'sip'),
            has_property('protocolid', result_protocol.id),
            has_property('context', 'default'),
            has_property('number', '1000')
        ))

        assert_that(result_extension, all_of(
            has_property('exten', '1000'),
            has_property('context', 'default'),
            has_property('type', 'user'),
            has_property('commented', 0)
        ))

        assert_that(result_protocol, has_property('type', 'friend'))

    def test_create_sccp_not_implemented(self):
        line = LineSCCP(protocol='sccp',
                        context='default',
                        number='1000')

        self.assertRaises(NotImplementedError, line_dao.create, line)

    def test_create_iax_not_implemented(self):
        line = LineIAX(protocol='iax',
                       context='default',
                       number='1000')

        self.assertRaises(NotImplementedError, line_dao.create, line)

    def test_create_custom_not_implemented(self):
        line = LineCUSTOM(protocol='custom',
                          context='default',
                          number='1000')

        self.assertRaises(NotImplementedError, line_dao.create, line)

    @patch('xivo_dao.helpers.db_manager.AsteriskSession')
    def test_create_database_error(self, Session):
        session = Mock()
        session.commit.side_effect = SQLAlchemyError()
        Session.return_value = session

        name = 'line'
        context = 'toto'
        secret = '1234'

        line = LineSIP(name=name,
                       context=context,
                       username=name,
                       secret=secret)

        self.assertRaises(ElementCreationError, line_dao.create, line)

    def test_delete_sip_line(self):
        number = '1234'
        context = 'lakokj'
        user = self.add_user(firstname='toto')
        exten = self.add_extension(exten=number,
                                      context=context,
                                      type='user',
                                      typeval=user.id)
        line_sip = self.add_usersip(id=3456)
        line = self.add_line(protocol='sip',
                                protocolid=line_sip.id,
                                iduserfeatures=user.id,
                                number=number,
                                context=context)

        line = line_dao.get(line.id)

        line_dao.delete(line)

        row = (self.session.query(LineSchema)
               .filter(LineSchema.id == line.id)
               .first())

        assert_that(row, equal_to(None))

        row = (self.session.query(UserSIPSchema)
               .filter(UserSIPSchema.id == line.protocolid)
               .first())

        assert_that(row, equal_to(None))

        row = (self.session.query(Extension)
               .filter(Extension.id == exten.id)
               .first())

        assert_that(row, equal_to(None))

        row = (self.session.query(UserSchema)
               .filter(UserSchema.id == user.id)
               .first())

        self.assertNotEquals(row, None)
