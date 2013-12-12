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

from hamcrest import assert_that, equal_to, all_of, has_property, is_not, has_length, none
from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.alchemy.ctiphonehintsgroup import CtiPhoneHintsGroup
from xivo_dao.alchemy.ctipresences import CtiPresences
from xivo_dao.alchemy.linefeatures import LineFeatures as LineSchema
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema
from xivo_dao.data_handler.line import dao as line_dao
from xivo_dao.data_handler.extension import dao as extension_dao
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.usersip import UserSIP as UserSIPSchema
from xivo_dao.alchemy.useriax import UserIAX as UserIAXSchema
from xivo_dao.alchemy.usercustom import UserCustom as UserCustomSchema
from xivo_dao.alchemy.sccpline import SCCPLine as SCCPLineSchema
from xivo_dao.data_handler.line.model import LineSIP, LineSCCP, LineIAX, LineCUSTOM, \
    LineOrdering
from xivo_dao.data_handler.exception import ElementNotExistsError, \
    ElementCreationError, ElementDeletionError, ElementEditionError
from sqlalchemy.exc import SQLAlchemyError
from mock import patch, Mock
from hamcrest.library.collection.issequence_containinginorder import contains
from hamcrest.library.collection.issequence_containing import has_items


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

        line_sip = self.add_usersip(name=line_name)
        line = self.add_line(protocolid=line_sip.id,
                             name=line_name)

        line = line_dao.get(line.id)

        assert_that(line.name, equal_to(line_name))

    def test_get_custom_line(self):
        line_interface = '123456789'
        line_name = 'custom/abcd'

        line_custom = self.add_usercustom(interface=line_interface,
                                          protocol='custom',
                                          context='default',
                                          category='user',
                                          commented=0)

        line = self.add_line(protocol='custom', protocolid=line_custom.id, name=line_name)

        line = line_dao.get(line.id)

        assert_that(line.name, equal_to(line_interface))

    def test_get_no_line(self):
        self.assertRaises(ElementNotExistsError, line_dao.get, 666)

    def test_get_by_user_id(self):
        line_name = 'sdklfj'
        line_sip = self.add_usersip(name=line_name)

        self.add_user_line_with_exten(exten='7777')
        user_line = self.add_user_line_with_exten(protocolid=line_sip.id,
                                                  name_line=line_name)
        self.add_user_line_with_exten(exten='6666')

        line = line_dao.get_by_user_id(user_line.user.id)

        assert_that(line.name, equal_to(line_name))

    def test_get_by_user_id_no_user(self):
        self.assertRaises(ElementNotExistsError, line_dao.get_by_user_id, 666)

    def test_get_by_user_id_commented(self):
        line_name = 'sdklfj'

        self.add_user_line_with_exten(exten='7777')
        user_line = self.add_user_line_with_exten(name_line=line_name,
                                                  commented_line=1)
        self.add_user_line_with_exten(exten='6666')

        self.assertRaises(ElementNotExistsError, line_dao.get_by_user_id, user_line.user.id)

    def test_get_by_number_context(self):
        line_name = 'sdklfj'
        exten = '1235'
        context = 'notdefault'
        line_sip = self.add_usersip(name=line_name,
                                    context=context)

        self.add_user_line_with_exten(exten='7777')
        self.add_user_line_with_exten(protocolid=line_sip.id,
                                      name_line=line_name,
                                      exten=exten,
                                      context=context)
        self.add_user_line_with_exten(exten='6666')

        line = line_dao.get_by_number_context(exten, context)

        assert_that(line.name, equal_to(line_name))
        assert_that(line.number, equal_to(exten))
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

    def test_find_all_no_lines(self):
        expected = []
        lines = line_dao.find_all()

        assert_that(lines, equal_to(expected))

    def test_find_all_one_line(self):
        name = 'Pascal'
        line_sip = self.add_usersip(name=name)
        line = self.add_line(protocolid=line_sip.id,
                             name=name)

        lines = line_dao.find_all()

        assert_that(lines, has_length(1))
        line_found = lines[0]
        assert_that(line_found, has_property('id', line.id))
        assert_that(line_found, has_property('name', name))

    def test_find_all_two_lines(self):
        name1 = 'Pascal'
        name2 = 'George'

        line_sip1 = self.add_usersip(name=name1)
        line1 = self.add_line(protocolid=line_sip1.id,
                              name=name1)
        line_sip1 = self.add_usersip(name=name2)
        line2 = self.add_line(protocolid=line_sip1.id,
                              name=name2)

        lines = line_dao.find_all()

        assert_that(lines, has_length(2))
        assert_that(lines, has_items(
            all_of(
                has_property('id', line1.id),
                has_property('name', name1)),
            all_of(
                has_property('id', line2.id),
                has_property('name', name2))
        ))

    def test_find_all_default_order_by_name_context(self):
        line_sip = self.add_usersip(name='xxx')
        line1 = self.add_line(protocolid=line_sip.id,
                              name='xxx', context='f')
        line_sip = self.add_usersip(name='vvv')
        line2 = self.add_line(protocolid=line_sip.id,
                              name='vvv', context='a')
        line_sip = self.add_usersip(name='aaa')
        line3 = self.add_line(protocolid=line_sip.id,
                              name='aaa', context='a')

        lines = line_dao.find_all()

        assert_that(lines, has_length(3))
        assert_that(lines[0].id, equal_to(line3.id))
        assert_that(lines[1].id, equal_to(line2.id))
        assert_that(lines[2].id, equal_to(line1.id))

    def test_find_all_order_by_name(self):
        line_sip = self.add_usersip()
        line_last = self.add_line(protocolid=line_sip.id,
                                  name='Bob',
                                  context='Alzard')
        line_sip = self.add_usersip()
        line_first = self.add_line(protocolid=line_sip.id,
                                   name='Albert',
                                   context='Breton')

        lines = line_dao.find_all(order=[LineOrdering.name])

        assert_that(lines[0].id, equal_to(line_first.id))
        assert_that(lines[1].id, equal_to(line_last.id))

    def test_find_all_order_by_context(self):
        line_sip = self.add_usersip()
        line_last = self.add_line(protocolid=line_sip.id,
                                  name='Albert',
                                  context='Breton')
        line_sip = self.add_usersip()
        line_first = self.add_line(protocolid=line_sip.id,
                                   name='Bob',
                                   context='Alzard')

        lines = line_dao.find_all(order=[LineOrdering.context])

        assert_that(lines[0].id, equal_to(line_first.id))
        assert_that(lines[1].id, equal_to(line_last.id))

    def test_find_all_by_name_no_line(self):
        result = line_dao.find_all_by_name('abc')

        assert_that(result, equal_to([]))

    def test_find_all_by_name_not_right_name(self):
        name = 'Lord'
        wrong_name = 'Gregory'

        self.add_line(name=name)

        result = line_dao.find_all_by_name(wrong_name)

        assert_that(result, equal_to([]))

    def test_find_all_by_name(self):
        name = 'ddd'
        line_sip = self.add_usersip(name=name)
        line = self.add_line(protocolid=line_sip.id,
                             name=name,
                             context='sss')

        result = line_dao.find_all_by_name(name)

        assert_that(result, contains(
            all_of(
                has_property('id', line.id),
                has_property('name', name)
            )
        ))

    def test_find_all_by_name_no_lines(self):
        result = line_dao.find_all_by_name('')

        assert_that(result, has_length(0))

    def test_find_all_by_name_partial(self):
        name = 'Lord'
        partial_fullname = 'rd'

        line_sip = self.add_usersip(name=name)
        line = self.add_line(protocolid=line_sip.id,
                             name=name)

        result = line_dao.find_all_by_name(partial_fullname)

        assert_that(result, has_length(1))
        assert_that(result, contains(
            all_of(
                has_property('id', line.id),
                has_property('name', name),
            )))

    def test_find_all_by_name_two_lines_default_order(self):
        search_term = 'lord'

        line_sip = self.add_usersip(name='Lordy')
        line_last = self.add_line(protocolid=line_sip.id,
                                  name='Lordy',
                                  context='z')
        line_sip = self.add_usersip(name='lord')
        line_first = self.add_line(protocolid=line_sip.id,
                                   name='lord',
                                   context='a')
        line_sip = self.add_usersip(name='Toto')
        self.add_line(protocolid=line_sip.id,
                      name='Toto',
                      context='a')

        result = line_dao.find_all_by_name(search_term)

        assert_that(result, has_length(2))
        assert_that(result, contains(
            has_property('id', line_first.id),
            has_property('id', line_last.id),
        ))

    def test_find_all_by_device_id_no_lines(self):
        result = line_dao.find_all_by_device_id('1')

        assert_that(result, has_length(0))

    def test_find_all_by_device_id(self):
        device_id = u'222'

        line_sip = self.add_usersip(name='lord')
        line = self.add_line(protocolid=line_sip.id,
                             name=line_sip.name,
                             context=line_sip.context,
                             device=device_id)

        result = line_dao.find_all_by_device_id(device_id)

        assert_that(result, has_length(1))
        assert_that(result, contains(
            has_property('id', line.id)
        ))
        assert_that(result, contains(
            has_property('device', device_id)
        ))

    def test_find_all_by_device_id_some_lines_no_device(self):

        line_sip = self.add_usersip(name='Lordy')
        self.add_line(protocolid=line_sip.id,
                      name=line_sip.name,
                      context=line_sip.context)
        line_sip = self.add_usersip(name='Toto')
        self.add_line(protocolid=line_sip.id,
                      name=line_sip.name,
                      context=line_sip.context)

        result = line_dao.find_all_by_device_id('54')

        assert_that(result, has_length(0))

    def test_find_all_by_device_id_some_lines(self):
        device_id = u'222'

        line_sip = self.add_usersip(name='Lordy')
        self.add_line(protocolid=line_sip.id,
                      name=line_sip.name,
                      context=line_sip.context)
        line_sip = self.add_usersip(name='Toto')
        self.add_line(protocolid=line_sip.id,
                      name=line_sip.name,
                      context=line_sip.context)
        line_sip = self.add_usersip(name='lord')
        line = self.add_line(protocolid=line_sip.id,
                             name=line_sip.name,
                             context=line_sip.context,
                             device=device_id)

        result = line_dao.find_all_by_device_id(device_id)

        assert_that(result, has_length(1))
        assert_that(result, contains(
            has_property('id', line.id)
        ))
        assert_that(result, contains(
            has_property('device', device_id)
        ))

    def test_find_by_user_id_no_lines(self):
        result = line_dao.find_by_user_id(1)

        assert_that(result, equal_to(None))

    def test_find_by_user_id_not_found(self):
        line_sip = self.add_usersip()
        self.add_user_line_with_exten(protocolid=line_sip.id,
                                      name_line=line_sip.name,
                                      context=line_sip.context)

        line_sip = self.add_usersip()
        self.add_user_line_with_exten(protocolid=line_sip.id,
                                      name_line=line_sip.name,
                                      context=line_sip.context)

        result = line_dao.find_by_user_id(1)

        assert_that(result, equal_to(None))

    def test_find_by_user_id(self):
        line_sip = self.add_usersip()
        self.add_user_line_with_exten(protocolid=line_sip.id,
                                      name_line=line_sip.name,
                                      context=line_sip.context)

        line_sip = self.add_usersip()
        expected_ule = self.add_user_line_with_exten(protocolid=line_sip.id,
                                                     name_line=line_sip.name,
                                                     context=line_sip.context)

        result = line_dao.find_by_user_id(expected_ule.user.id)

        assert_that(result, all_of(
            has_property('id', expected_ule.line.id),
            has_property('name', expected_ule.line.name),
            has_property('context', expected_ule.line.context)
        ))

    def test_provisioning_id_exists(self):
        provd_id = 123456
        self.add_line(provisioningid=provd_id)

        result = line_dao.provisioning_id_exists(provd_id)

        assert_that(result, equal_to(True))

    def test_provisioning_id_does_not_exist(self):
        result = line_dao.provisioning_id_exists(123456)

        assert_that(result, equal_to(False))

    def test_edit(self):
        username = 'toto'
        secret = 'kiki'
        expected_name = 'huhu'
        expected_context = 'popo'
        line_sip = self.add_usersip(name=username,
                                    username=username,
                                    secret=secret)
        line = self.add_line(protocolid=line_sip.id,
                             name=username,
                             context=line_sip.context)

        expected_line = line_dao.get(line.id)
        expected_line.name = expected_name
        expected_line.username = expected_name
        expected_line.context = expected_context

        line_dao.edit(expected_line)

        line_row = (self.session.query(LineSchema)
                    .filter(LineSchema.id == expected_line.id)
                    .first())

        line_sip_row = (self.session.query(UserSIPSchema)
                        .filter(UserSIPSchema.id == expected_line.protocolid)
                        .first())

        self.assertEquals(line_row.name, expected_name)
        self.assertEquals(line_row.context, expected_context)
        self.assertEquals(line_sip_row.name, expected_name)
        self.assertEquals(line_sip_row.context, expected_context)

    def test_edit_with_unknown_line(self):
        line_sip = self.add_usersip()
        line = LineSIP(id=123,
                       username='unknown',
                       protocolid=line_sip.id)

        self.assertRaises(ElementNotExistsError, line_dao.edit, line)

    @patch('xivo_dao.helpers.db_manager.AsteriskSession')
    def test_edit_with_database_error(self, Session):
        session = Mock()
        session.commit.side_effect = SQLAlchemyError()
        Session.return_value = session

        line_sip = self.add_usersip()
        line = LineSIP(id=123,
                       username='toto',
                       secret='kiki',
                       protocolid=line_sip.id)

        self.assertRaises(ElementEditionError, line_dao.edit, line)
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()

    def test_update_xivo_userid_sip(self):
        username = 'toto'
        secret = 'kiki'
        line_sip = self.add_usersip(name=username,
                                    username=username,
                                    secret=secret)
        line = self.add_line(protocolid=line_sip.id,
                             name=username,
                             context=line_sip.context)
        main_user = Mock(id=12)

        line_dao.update_xivo_userid(line, main_user)

        line_sip_row = (self.session.query(UserSIPSchema)
                        .filter(UserSIPSchema.id == line_sip.id)
                        .first())
        self.assertEquals(line_sip_row.setvar, 'XIVO_USERID=12')

    @patch('xivo_dao.helpers.db_manager.AsteriskSession')
    def test_update_xivo_userid_sip_db_error(self, Session):
        session = Session.return_value = Mock()
        session.commit.side_effect = SQLAlchemyError()
        username = 'toto'
        secret = 'kiki'
        line_sip = self.add_usersip(name=username,
                                    username=username,
                                    secret=secret)
        line = self.add_line(protocolid=line_sip.id,
                             name=username,
                             context=line_sip.context)
        main_user = Mock(id=12)

        self.assertRaises(ElementEditionError, line_dao.update_xivo_userid, line, main_user)

    @patch('xivo_dao.helpers.db_manager.AsteriskSession')
    def test_update_xivo_userid_not_sip(self, Session):
        session = Session.return_value = Mock()
        line = Mock(protocol='sccp')
        main_user = Mock(id=12)

        line_dao.update_xivo_userid(line, main_user)

        assert_that(session.commit.call_count, equal_to(0))

    def test_delete_user_references_sip(self):
        line_sip = self.add_usersip(name='toto',
                                    username='toto',
                                    secret='secret',
                                    callerid='"Toto toto <1234>"',
                                    setvar='XIVO_USERID=1')
        line = self.add_line(protocol='sip',
                             protocolid=line_sip.id,
                             name=line_sip.username,
                             context=line_sip.context)

        line_dao.delete_user_references(line.id)

        updated_row = (self.session.query(UserSIPSchema)
                       .filter(UserSIPSchema.id == line_sip.id)
                       .first())

        assert_that(updated_row.callerid, none())
        assert_that(updated_row.setvar, equal_to(''))

    def test_delete_user_references_not_sip(self):
        line_sccp_row = self.add_sccpline()
        line_row = self.add_line(protocol='sccp',
                                 protocolid=line_sccp_row.id)

        line_dao.delete_user_references(line_row.id)

        updated_row = (self.session.query(SCCPLineSchema)
                       .get(line_sccp_row.id))

        assert_that(updated_row.cid_name, is_not(equal_to('')))

    @patch('xivo_dao.helpers.db_manager.AsteriskSession')
    def test_delete_user_references_db_error(self, Session):
        session = Session.return_value = Mock()
        session.commit.side_effect = SQLAlchemyError()
        session.query.return_value.get.return_value = Mock(protocol='sip')

        self.assertRaises(ElementEditionError, line_dao.delete_user_references, 1)

    def test_reset_device(self):
        line = self.add_line(device='1234')

        line_dao.reset_device(line.device)

        result = (self.session.query(LineSchema)
                  .filter(LineSchema.id == line.id)
                  .first())

        assert_that(result.device, equal_to(''))

    def test_generate_random_hash_no_sip_user(self):
        generated_hash = line_dao.generate_random_hash(self.session, UserSIPSchema.name)

        assert_that(generated_hash, has_length(8))

    @patch('xivo_dao.data_handler.line.dao.random_hash')
    def test_generate_random_hash_same_sip_user(self, random_hash):
        existing_hash = 'abcd'
        expected_hash = 'abcdefgh'
        self.add_usersip(name=existing_hash)

        random_hash.side_effect = [existing_hash, expected_hash]

        generated_hash = line_dao.generate_random_hash(self.session, UserSIPSchema.name)

        assert_that(generated_hash, equal_to(expected_hash))

    def test_random_hash_no_uppercase_letters(self):
        generated_hash = line_dao.random_hash()

        uppercase = [x for x in generated_hash if x.isupper()]
        assert_that(uppercase, contains(), "generated hash isn't supposed to have uppercase characters")
        assert_that(generated_hash, has_length(8))

    def test_create_sip_line_with_no_extension(self):
        line = LineSIP(protocol='sip',
                       context='default',
                       provisioning_extension=123456)

        line_created = line_dao.create(line)

        assert_that(line_created, is_not(has_property('number')))

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
                       username=name,
                       secret=secret)

        self.assertRaises(ElementCreationError, line_dao.create, line)
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()

    def test_create_sip_line(self):
        line = LineSIP(context='default',
                       provisioning_extension=123456)

        line_created = line_dao.create(line)

        result_protocol = (self.session.query(UserSIPSchema)
                           .filter(UserSIPSchema.id == line_created.protocolid)
                           .first())
        result_line = (self.session.query(LineSchema)
                       .filter(LineSchema.id == line_created.id)
                       .first())

        assert_that(result_line, all_of(
            has_property('protocol', 'sip'),
            has_property('protocolid', result_protocol.id),
            has_property('context', 'default'),
            has_property('provisioningid', line.provisioning_extension)
        ))

        assert_that(result_protocol, has_property('type', 'friend'))

    def test_create_sccp_not_implemented(self):
        line = LineSCCP(context='default',
                        number='1000')

        self.assertRaises(NotImplementedError, line_dao.create, line)

    def test_create_iax_not_implemented(self):
        line = LineIAX(context='default',
                       number='1000')

        self.assertRaises(NotImplementedError, line_dao.create, line)

    def test_create_custom_not_implemented(self):
        line = LineCUSTOM(context='default',
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

    def test_delete_sip_line_associated(self):
        number = '1234'
        context = 'lakokj'

        line_sip = self.add_usersip()
        user_line = self.add_user_line_with_exten(protocolid=line_sip.id,
                                                  exten=number,
                                                  context=context)

        line = line_dao.get(user_line.line.id)

        self.assertRaises(ElementDeletionError, line_dao.delete, line)

    def test_delete_sip_line_not_associated(self):
        number = '1234'
        context = 'lakokj'

        line_sip = self.add_usersip()
        line = self.add_line(number=number,
                             context=context,
                             protocol='sip',
                             protocolid=line_sip.id)

        line_dao.delete(line)

        row = (self.session.query(LineSchema)
               .filter(LineSchema.id == line.id)
               .first())

        assert_that(row, equal_to(None))

        row = (self.session.query(UserSIPSchema)
               .filter(UserSIPSchema.id == line.protocolid)
               .first())

        assert_that(row, equal_to(None))

    def test_dissociate_extension(self):
        exten = '1000'
        context = 'default'
        type = 'user'
        provisioningid = 12

        line_row = self.add_line(context=context,
                                 provisioningid=provisioningid,
                                 number=exten)

        extension_row = self.add_extension(exten=exten,
                                           context=context,
                                           type=type,
                                           typeval=str(line_row.id))

        extension = extension_dao.get(extension_row.id)

        line_dao.dissociate_extension(extension)

        line_row = self.session.query(LineSchema).get(line_row.id)

        self.assertEquals(line_row.number, '')
        self.assertEquals(line_row.context, '')
        self.assertEquals(line_row.provisioningid, 0)

    def test_associate_extension(self):
        exten = '1000'
        context = 'default'
        provisioningid = 123456

        line_row = self.add_line(provisioningid=provisioningid)

        extension_row = self.add_extension(exten=exten,
                                           context=context,
                                           typeval=str(line_row.id))

        extension = extension_dao.get(extension_row.id)

        line_dao.associate_extension(extension, line_row.id)

        line_row = self.session.query(LineSchema).get(line_row.id)

        self.assertEquals(line_row.number, exten)
        self.assertEquals(line_row.context, context)
        self.assertEquals(line_row.provisioningid, provisioningid)
