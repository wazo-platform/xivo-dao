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

from hamcrest import assert_that
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
from xivo_dao.data_handler.line.model import LineSIP
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

        line_id = self.add_line(name=line_name)

        line = line_dao.get(line_id)

        assert_that(line.name, equal_to(line_name))

    def test_get_no_line(self):
        self.assertRaises(ElementNotExistsError, line_dao.get, 666)

    def test_get_by_user_id(self):
        line_name = 'sdklfj'

        line_id = self.add_line(name=line_name)
        user_id = self.add_user()
        self.add_user_line(user_id=user_id, line_id=line_id)

        line = line_dao.get_by_user_id(user_id)

        assert_that(line.name, equal_to(line_name))

    def test_get_by_user_id_no_user(self):
        self.assertRaises(ElementNotExistsError, line_dao.get_by_user_id, 666)

    def test_get_by_user_id_commented(self):
        line_name = 'sdklfj'

        line_id = self.add_line(name=line_name, commented=1)
        user_id = self.add_user()
        self.add_user_line(user_id=user_id, line_id=line_id)

        self.assertRaises(ElementNotExistsError, line_dao.get_by_user_id, user_id)

    def test_get_by_number_context(self):
        line_name = 'sdklfj'
        number = '1235'
        context = 'notdefault'

        line_id = self.add_line(name=line_name, number=number, context=context)
        self.add_extension(exten=number, context=context, type='user', typeval=str(line_id))

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

        line_id = self.add_line(name=line_name, commented=1)
        self.add_extension(exten=number, context=context, type='user', typeval=str(line_id))

        self.assertRaises(ElementNotExistsError, line_dao.get_by_number_context, number, context)

    def test_is_exist_provisioning_id(self):
        provd_id = 123456
        self.add_line(provisioningid=provd_id)

        result = line_dao.is_exist_provisioning_id(provd_id)

        self.assertEquals(result, True)

    def test_is_not_exist_provisioning_id(self):
        result = line_dao.is_exist_provisioning_id(123456)

        self.assertEquals(result, False)

    def test_create_sip_line_with_no_extension(self):
        line = LineSIP(protocol='sip',
                       context='default',
                       provisioningid=123456)

        line_created = line_dao.create(line)

        assert_that(hasattr(line_created, 'number'), equal_to(False))

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

        self.assertEquals(result_line.protocol, 'sip')
        self.assertEquals(result_line.protocolid, result_protocol.id)
        self.assertEquals(result_line.context, 'default')
        self.assertEquals(result_line.number, '1000')
        self.assertEquals(result_extension.exten, '1000')
        self.assertEquals(result_extension.context, 'default')
        self.assertEquals(result_extension.type, 'user')
        self.assertEquals(result_extension.commented, 0)
        self.assertEquals(result_protocol.type, 'friend')

    def test_delete_sip_line(self):
        number = '1234'
        context = 'lakokj'
        user_id = self.add_user(firstname='toto')
        exten_id = self.add_extension(exten=number,
                                      context=context,
                                      type='user',
                                      typeval=user_id)
        line_sip = self._insert_usersip(3456)
        line_id = self.add_line(protocol='sip',
                                protocolid=line_sip.id,
                                iduserfeatures=user_id,
                                number=number,
                                context=context)

        line = line_dao.get(line_id)

        line_dao.delete(line)

        row = (self.session.query(LineSchema)
               .filter(LineSchema.id == line_id)
               .first())
        self.assertEquals(row, None)

        row = (self.session.query(UserSIPSchema)
               .filter(UserSIPSchema.id == line.protocolid)
               .first())
        self.assertEquals(row, None)

        row = (self.session.query(Extension)
               .filter(Extension.id == exten_id)
               .first())
        self.assertEquals(row, None)

        row = (self.session.query(UserSchema)
               .filter(UserSchema.id == user_id)
               .first())
        self.assertNotEquals(row, None)

    def _insert_usersip(self, usersip_id):
        usersip = UserSIPSchema()
        usersip.id = usersip_id
        usersip.name = 'abcd'
        usersip.type = 'friend'

        self.session.begin()
        self.session.add(usersip)
        self.session.commit()

        return usersip

    def _insert_sccpline(self, sccpline_id):
        sccpline = SCCPLineSchema()
        sccpline.id = sccpline_id
        sccpline.name = '1234'
        sccpline.context = 'test'
        sccpline.cid_name = 'Tester One'
        sccpline.cid_num = '1234'

        self.session.begin()
        self.session.add(sccpline)
        self.session.commit()

        return sccpline
