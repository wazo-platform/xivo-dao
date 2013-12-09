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

import unittest
from mock import Mock, patch, sentinel
from hamcrest import assert_that, equal_to

from xivo_dao.data_handler.line_extension.model import LineExtension
from xivo_dao.data_handler.line_extension import services as line_extension_service


class TestLineExtensionService(unittest.TestCase):

    @patch('xivo_dao.data_handler.line_extension.notifier.associated')
    @patch('xivo_dao.data_handler.line_extension.dao.associate')
    @patch('xivo_dao.data_handler.line_extension.validator.validate_associate')
    @patch('xivo_dao.data_handler.line_extension.services.make_line_extension_associations')
    def test_associate(self,
                       line_extension_associations,
                       validate_associate,
                       dao_associate,
                       notifier_associated):

        line_extension = Mock(LineExtension)
        created_line_extension = dao_associate.return_value = Mock(LineExtension)

        result = line_extension_service.associate(line_extension)

        assert_that(result, equal_to(created_line_extension))
        validate_associate.assert_called_once_with(line_extension)
        dao_associate.assert_called_once_with(line_extension)
        line_extension_associations.assert_called_once_with(created_line_extension)
        notifier_associated.assert_called_once_with(created_line_extension)

    @patch('xivo_dao.data_handler.line_extension.dao.get_by_line_id')
    def test_get_by_line_id(self, dao_get_by_line_id):
        line_extension = Mock(LineExtension, line_id=1)
        dao_get_by_line_id.return_value = line_extension

        result = line_extension_service.get_by_line_id(1)

        assert_that(result, equal_to(line_extension))
        dao_get_by_line_id.assert_called_once_with(1)

    @patch('xivo_dao.data_handler.line_extension.dao.find_by_line_id')
    def test_find_by_line_id(self, dao_find_by_line_id):
        line_extension = Mock(LineExtension, line_id=1)
        dao_find_by_line_id.return_value = line_extension

        result = line_extension_service.find_by_line_id(1)

        assert_that(result, equal_to(line_extension))
        dao_find_by_line_id.assert_called_once_with(1)

    @patch('xivo_dao.data_handler.line_extension.dao.dissociate')
    @patch('xivo_dao.data_handler.line_extension.notifier.dissociated')
    @patch('xivo_dao.data_handler.line_extension.validator.validate_dissociation')
    def test_dissociate(self, validate_dissociation, notifier_dissociated, dao_dissociate):
        line_extension = Mock(LineExtension)

        line_extension_service.dissociate(line_extension)

        validate_dissociation.assert_called_once_with(line_extension)
        dao_dissociate.assert_called_once_with(line_extension)
        notifier_dissociated.assert_called_once_with(line_extension)


class TestMakeLineExtensionAssociation(unittest.TestCase):
    @patch('xivo_dao.data_handler.user_line.dao.find_main_user_line')
    @patch('xivo_dao.data_handler.user_line_extension.helper.make_associations')
    def test_make_line_extension_associations_with_user(self, make_associations, user_line):
        line_extension = Mock(line_id=sentinel.line_id,
                              extension_id=sentinel.extension_id)
        user_line.return_value = Mock(user_id=sentinel.user_id,
                                      line_id=sentinel.line_id)

        line_extension_service.make_line_extension_associations(line_extension)

        user_line.assert_called_once_with(sentinel.line_id)
        make_associations.assert_called_once_with(sentinel.user_id, sentinel.line_id, sentinel.extension_id)

    @patch('xivo_dao.data_handler.user_line.dao.find_main_user_line')
    @patch('xivo_dao.data_handler.user_line_extension.helper.make_associations')
    def test_make_line_extension_associations_without_user(self, make_associations, user_line):
        line_extension = Mock(line_id=sentinel.line_id,
                              extension_id=sentinel.extension_id)
        user_line.return_value = None

        line_extension_service.make_line_extension_associations(line_extension)

        user_line.assert_called_once_with(sentinel.line_id)
        assert_that(make_associations.call_count, equal_to(0))
