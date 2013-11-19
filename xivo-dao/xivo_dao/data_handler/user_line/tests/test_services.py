# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import unittest
from mock import patch, Mock
from hamcrest import assert_that, equal_to

from xivo_dao.data_handler.user_line.model import UserLine
from xivo_dao.data_handler.user_line import services as user_line_services


class TestUserLineGetByUserIdAndLineId(unittest.TestCase):

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


class TestUserLineAssociate(unittest.TestCase):

    @patch('xivo_dao.data_handler.user_line.dao.find_main_user', Mock(return_value=None))
    @patch('xivo_dao.data_handler.user_line.validator.validate_association')
    @patch('xivo_dao.data_handler.user_line.dao.associate')
    @patch('xivo_dao.data_handler.user_line.notifier.associated')
    def test_associate(self, notifier_associated, dao_associate, validate_association):
        user_line = UserLine(user_id=1,
                             line_id=2)

        result = user_line_services.associate(user_line)

        assert_that(result, equal_to(user_line))
        validate_association.assert_called_once_with(user_line)
        dao_associate.assert_called_once_with(user_line)
        notifier_associated.assert_called_once_with(user_line)

    @patch('xivo_dao.data_handler.user_line.dao.find_main_user')
    @patch('xivo_dao.data_handler.user_line.validator.validate_association')
    @patch('xivo_dao.data_handler.user_line.dao.associate')
    @patch('xivo_dao.data_handler.user_line.notifier.associated')
    def test_associate_main_user(self, notifier_associated, dao_associate, validate_association, dao_find_main_user):
        user_line = UserLine(user_id=1,
                             line_id=2)
        expected_user_line = UserLine(user_id=1,
                                      line_id=2,
                                      main_user=True)

        dao_find_main_user.return_value = user_line

        result = user_line_services.associate(user_line)

        assert_that(result, equal_to(expected_user_line))
        validate_association.assert_called_once_with(user_line)
        dao_associate.assert_called_once_with(user_line)
        notifier_associated.assert_called_once_with(user_line)

    @patch('xivo_dao.data_handler.user_line.dao.find_main_user')
    @patch('xivo_dao.data_handler.user_line.validator.validate_association')
    @patch('xivo_dao.data_handler.user_line.dao.associate')
    @patch('xivo_dao.data_handler.user_line.notifier.associated')
    def test_associate_with_main_user_already_associated_to_this_line(self,
                                                                      notifier_associated,
                                                                      dao_associate,
                                                                      validate_association,
                                                                      dao_find_main_user):
        main_user_line = UserLine(user_id=1,
                                  line_id=2)
        secondary_user_line = UserLine(user_id=2,
                                       line_id=2)

        expected_user_line = UserLine(user_id=2,
                                      line_id=2,
                                      main_user=False)

        dao_find_main_user.return_value = main_user_line

        result = user_line_services.associate(secondary_user_line)

        assert_that(result, equal_to(expected_user_line))
        validate_association.assert_called_once_with(secondary_user_line)
        dao_associate.assert_called_once_with(secondary_user_line)
        notifier_associated.assert_called_once_with(secondary_user_line)


class TestUserLineDissociate(unittest.TestCase):

    @patch('xivo_dao.data_handler.user_line.dao.dissociate')
    @patch('xivo_dao.data_handler.user_line.notifier.dissociated')
    @patch('xivo_dao.data_handler.user_line.validator.validate_dissociation')
    def test_dissociate(self, validate_dissociation, notifier_dissociated, dao_dissociate):
        user_line = Mock(UserLine)

        user_line_services.dissociate(user_line)

        validate_dissociation.assert_called_once_with(user_line)
        dao_dissociate.assert_called_once_with(user_line)
        notifier_dissociated.assert_called_once_with(user_line)
