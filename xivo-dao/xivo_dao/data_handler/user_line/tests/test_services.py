# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from mock import patch, Mock, sentinel
from hamcrest import assert_that, equal_to, contains

from xivo_dao.tests.test_case import TestCase
from xivo_dao.data_handler.user_line.model import UserLine
from xivo_dao.data_handler.line_extension.model import LineExtension
from xivo_dao.data_handler.user_line import services as user_line_services


class TestUserLineGetByUserIdAndLineId(TestCase):

    @patch('xivo_dao.data_handler.user_line.dao.get_by_user_id_and_line_id')
    def test_get_by_user_id_and_line_id(self, user_line_get_by_user_id):
        user_id = 123
        line_id = 42
        expected_result = UserLine(user_id=user_id,
                                   line_id=line_id)
        user_line_get_by_user_id.return_value = UserLine(user_id=user_id,
                                                         line_id=line_id)

        result = user_line_services.get_by_user_id_and_line_id(user_id, line_id)

        user_line_get_by_user_id.assert_called_once_with(user_id, line_id)
        assert_that(result, equal_to(expected_result))


class TestFindAllByLineId(TestCase):

    @patch('xivo_dao.data_handler.user_line.dao.find_all_by_line_id')
    def test_find_all_by_line_id(self, find_all_by_line_id):
        user_line = Mock(UserLine, line_id=1)
        find_all_by_line_id.return_value = [user_line]

        result = user_line_services.find_all_by_line_id(1)

        assert_that(result, contains(user_line))


class TestUserLineAssociate(TestCase):

    @patch('xivo_dao.data_handler.user_line.dao.find_main_user_line', Mock(return_value=None))
    @patch('xivo_dao.data_handler.user_line.validator.validate_association')
    @patch('xivo_dao.data_handler.user_line.dao.associate')
    @patch('xivo_dao.data_handler.user_line.notifier.associated')
    @patch('xivo_dao.data_handler.user_line.services.make_user_line_associations')
    def test_associate(self,
                       user_line_associations,
                       notifier_associated,
                       dao_associate,
                       validate_association):
        user_line = UserLine(user_id=1,
                             line_id=2)

        result = user_line_services.associate(user_line)

        assert_that(result, equal_to(user_line))
        validate_association.assert_called_once_with(user_line)
        dao_associate.assert_called_once_with(user_line)
        user_line_associations.assert_called_once_with(user_line)
        notifier_associated.assert_called_once_with(user_line)

    @patch('xivo_dao.data_handler.user_line.dao.find_main_user_line')
    @patch('xivo_dao.data_handler.user_line.validator.validate_association')
    @patch('xivo_dao.data_handler.user_line.dao.associate')
    @patch('xivo_dao.data_handler.user_line.notifier.associated')
    @patch('xivo_dao.data_handler.user_line.services.make_user_line_associations')
    def test_associate_main_user(self,
                                 user_line_associations,
                                 notifier_associated,
                                 dao_associate,
                                 validate_association,
                                 dao_find_main_user_line):
        user_line = UserLine(user_id=1,
                             line_id=2)
        expected_user_line = UserLine(user_id=1,
                                      line_id=2,
                                      main_user=True)

        dao_find_main_user_line.return_value = user_line

        result = user_line_services.associate(user_line)

        assert_that(result, equal_to(expected_user_line))
        validate_association.assert_called_once_with(user_line)
        dao_associate.assert_called_once_with(user_line)
        user_line_associations.assert_called_once_with(user_line)
        notifier_associated.assert_called_once_with(user_line)

    @patch('xivo_dao.data_handler.user_line.dao.find_main_user_line')
    @patch('xivo_dao.data_handler.user_line.validator.validate_association')
    @patch('xivo_dao.data_handler.user_line.dao.associate')
    @patch('xivo_dao.data_handler.user_line.notifier.associated')
    @patch('xivo_dao.data_handler.user_line.services.make_user_line_associations')
    def test_associate_with_main_user_already_associated_to_this_line(self,
                                                                      user_line_associations,
                                                                      notifier_associated,
                                                                      dao_associate,
                                                                      validate_association,
                                                                      dao_find_main_user_line):
        main_user_line = UserLine(user_id=1,
                                  line_id=2)
        secondary_user_line = UserLine(user_id=2,
                                       line_id=2)

        expected_user_line = UserLine(user_id=2,
                                      line_id=2,
                                      main_user=False)

        dao_find_main_user_line.return_value = main_user_line

        result = user_line_services.associate(secondary_user_line)

        assert_that(result, equal_to(expected_user_line))
        validate_association.assert_called_once_with(secondary_user_line)
        dao_associate.assert_called_once_with(secondary_user_line)
        user_line_associations.assert_called_once_with(secondary_user_line)
        notifier_associated.assert_called_once_with(secondary_user_line)


class TestMakeUserLineAssociation(TestCase):

    @patch('xivo_dao.data_handler.user_line.dao.find_main_user_line')
    @patch('xivo_dao.data_handler.line_extension.dao.find_by_line_id')
    @patch('xivo_dao.data_handler.user_line_extension.helper.make_associations')
    def test_make_user_line_associations_with_extension(self,
                                                        make_associations,
                                                        line_extension,
                                                        find_main_user_line):
        user_line = Mock(user_id=sentinel.user_id,
                         line_id=sentinel.line_id)
        main_user_line = Mock(user_id=sentinel.main_user_id,
                              line_id=sentinel.line_id)

        line_extension.return_value = Mock(line_id=sentinel.line_id,
                                           extension_id=sentinel.extension_id)
        find_main_user_line.return_value = main_user_line

        user_line_services.make_user_line_associations(user_line)

        find_main_user_line.assert_called_once_with(sentinel.line_id)
        line_extension.assert_called_once_with(sentinel.line_id)
        make_associations.assert_called_once_with(sentinel.main_user_id, sentinel.line_id, sentinel.extension_id)

    @patch('xivo_dao.data_handler.user_line.dao.find_main_user_line')
    @patch('xivo_dao.data_handler.line_extension.dao.find_by_line_id')
    @patch('xivo_dao.data_handler.user_line_extension.helper.make_associations')
    def test_make_user_line_associations_without_extension(self,
                                                           make_associations,
                                                           line_extension,
                                                           find_main_user_line):
        user_line = Mock(user_id=sentinel.user_id,
                         line_id=sentinel.line_id)
        main_user_line = Mock(user_id=sentinel.main_user_id,
                              line_id=sentinel.line_id)

        line_extension.return_value = None
        find_main_user_line.return_value = main_user_line

        user_line_services.make_user_line_associations(user_line)

        find_main_user_line.assert_called_once_with(sentinel.line_id)
        line_extension.assert_called_once_with(sentinel.line_id)
        make_associations.assert_called_once_with(sentinel.main_user_id, sentinel.line_id, None)


class TestUserLineDissociate(TestCase):

    @patch('xivo_dao.data_handler.user_line.services.delete_user_line_associations')
    @patch('xivo_dao.data_handler.user_line.dao.dissociate')
    @patch('xivo_dao.data_handler.user_line.notifier.dissociated')
    @patch('xivo_dao.data_handler.user_line.validator.validate_dissociation')
    def test_dissociate(self,
                        validate_dissociation,
                        notifier_dissociated,
                        dao_dissociate,
                        delete_user_line_associations):
        user_line = Mock(UserLine)

        user_line_services.dissociate(user_line)

        validate_dissociation.assert_called_once_with(user_line)
        dao_dissociate.assert_called_once_with(user_line)
        notifier_dissociated.assert_called_once_with(user_line)
        delete_user_line_associations.assert_called_once_with(user_line)


class DeleteUserLineAssociations(TestCase):

    @patch('xivo_dao.data_handler.line.dao.delete_user_references')
    @patch('xivo_dao.data_handler.user_line_extension.helper.delete_extension_associations')
    @patch('xivo_dao.data_handler.user_line.dao.find_main_user_line')
    @patch('xivo_dao.data_handler.line_extension.dao.find_by_line_id')
    def test_no_extension_no_main_user(self,
                                       find_by_line_id,
                                       find_main_user_line,
                                       delete_extension_associations,
                                       delete_user_references):
        user_line = Mock(UserLine, user_id=1, line_id=2)

        find_by_line_id.return_value = None
        find_main_user_line.return_value = None

        user_line_services.delete_user_line_associations(user_line)

        find_by_line_id.assert_called_once_with(user_line.line_id)
        delete_user_references.assert_called_once_with(user_line.line_id)
        self.assertNotCalled(delete_extension_associations)

    @patch('xivo_dao.data_handler.line.dao.delete_user_references')
    @patch('xivo_dao.data_handler.user_line_extension.helper.delete_extension_associations')
    @patch('xivo_dao.data_handler.user_line.dao.find_main_user_line')
    @patch('xivo_dao.data_handler.line_extension.dao.find_by_line_id')
    def test_no_extension_with_main_user(self,
                                         find_by_line_id,
                                         find_main_user_line,
                                         delete_extension_associations,
                                         delete_user_references):
        user_line = Mock(UserLine, user_id=1, line_id=2)

        find_by_line_id.return_value = None
        find_main_user_line.return_value = user_line

        user_line_services.delete_user_line_associations(user_line)

        find_by_line_id.assert_called_once_with(user_line.line_id)
        find_main_user_line.assert_called_once_with(user_line.line_id)
        self.assertNotCalled(delete_extension_associations)
        self.assertNotCalled(delete_user_references)

    @patch('xivo_dao.data_handler.line.dao.delete_user_references')
    @patch('xivo_dao.data_handler.user_line_extension.helper.delete_extension_associations')
    @patch('xivo_dao.data_handler.user_line.dao.find_main_user_line')
    @patch('xivo_dao.data_handler.line_extension.dao.find_by_line_id')
    def test_with_extension_with_main_user(self,
                                           find_by_line_id,
                                           find_main_user_line,
                                           delete_extension_associations,
                                           delete_user_references):
        user_line = Mock(UserLine, user_id=1, line_id=2)
        line_extension = Mock(LineExtension, line_id=2, extension_id=3)

        find_by_line_id.return_value = line_extension
        find_main_user_line.return_value = user_line

        user_line_services.delete_user_line_associations(user_line)

        find_by_line_id.assert_called_once_with(user_line.line_id)
        find_main_user_line.assert_called_once_with(user_line.line_id)
        self.assertNotCalled(delete_extension_associations)
        self.assertNotCalled(delete_user_references)

    @patch('xivo_dao.data_handler.line.dao.delete_user_references')
    @patch('xivo_dao.data_handler.user_line_extension.helper.delete_extension_associations')
    @patch('xivo_dao.data_handler.user_line.dao.find_main_user_line')
    @patch('xivo_dao.data_handler.line_extension.dao.find_by_line_id')
    def test_with_extension_no_main_user(self,
                                         find_by_line_id,
                                         find_main_user_line,
                                         delete_extension_associations,
                                         delete_user_references):
        user_line = Mock(UserLine, user_id=1, line_id=2)
        line_extension = Mock(LineExtension, line_id=2, extension_id=3)

        find_by_line_id.return_value = line_extension
        find_main_user_line.return_value = None

        user_line_services.delete_user_line_associations(user_line)

        find_by_line_id.assert_called_once_with(user_line.line_id)
        find_main_user_line.assert_called_once_with(user_line.line_id)
        delete_extension_associations.assert_called_once_with(user_line.line_id, line_extension.extension_id)
        delete_user_references.assert_called_once_with(user_line.line_id)
