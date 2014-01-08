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

from xivo_dao.data_handler.exception import InvalidParametersError

from hamcrest import assert_that, equal_to, has_property
from mock import Mock, patch, sentinel
from unittest import TestCase

from .. import helper


class TestULEHelper(TestCase):

    @patch('xivo.caller_id.assemble_caller_id')
    @patch('xivo_dao.data_handler.extension.dao.find')
    @patch('xivo_dao.data_handler.extension.dao.associate_to_user')
    @patch('xivo_dao.data_handler.line.dao.get')
    @patch('xivo_dao.data_handler.line.dao.associate_extension')
    @patch('xivo_dao.data_handler.line.dao.update_xivo_userid')
    @patch('xivo_dao.data_handler.line.dao.edit')
    @patch('xivo_dao.data_handler.user.dao.get')
    def test_make_associations_with_extension(self,
                                              user_get,
                                              line_edit,
                                              line_update_xivo_userid,
                                              line_associate_extension,
                                              line_get,
                                              extension_associate,
                                              extension_find,
                                              caller_id):
        user = user_get.return_value = Mock()
        line = line_get.return_value = Mock()
        extension = extension_find.return_value = Mock()
        caller_id.return_value = sentinel.caller_id

        helper.make_associations(sentinel.user_id, sentinel.line_id, sentinel.extension_id)

        line_edit.assert_called_once_with(line)
        extension_associate.assert_called_once_with(user, extension)
        assert_that(line, has_property('callerid', sentinel.caller_id))
        extension_associate.assert_called_once_with(user, extension)
        line_associate_extension.assert_called_once_with(extension, line.id)
        line_update_xivo_userid.assert_called_once_with(line, user)
        caller_id.assert_called_once_with(user.fullname, extension.exten)

    @patch('xivo.caller_id.assemble_caller_id')
    @patch('xivo_dao.data_handler.extension.dao.find')
    @patch('xivo_dao.data_handler.extension.dao.associate_to_user')
    @patch('xivo_dao.data_handler.line.dao.get')
    @patch('xivo_dao.data_handler.line.dao.edit')
    @patch('xivo_dao.data_handler.line.dao.update_xivo_userid')
    @patch('xivo_dao.data_handler.user.dao.get')
    def test_make_associations_without_extension(self,
                                                 user_get,
                                                 line_update_xivo_userid,
                                                 line_edit,
                                                 line_get,
                                                 extension_associate,
                                                 extension_find,
                                                 caller_id):
        user = user_get.return_value = Mock()
        line = line_get.return_value = Mock(number=sentinel.number,
                                            context=sentinel.context)
        extension_find.return_value = None
        caller_id.return_value = sentinel.caller_id

        helper.make_associations(sentinel.user_id, sentinel.line_id, sentinel.extension_id)

        assert_that(extension_associate.call_count, equal_to(0))
        assert_that(line, has_property('number', sentinel.number))
        assert_that(line, has_property('context', sentinel.context))
        assert_that(line, has_property('callerid', sentinel.caller_id))
        line_edit.assert_called_once_with(line)
        assert_that(line_update_xivo_userid.call_count, equal_to(0))
        caller_id.assert_called_once_with(user.fullname, None)

    @patch('xivo_dao.data_handler.extension.dao.dissociate_extension')
    @patch('xivo_dao.data_handler.line.dao.dissociate_extension')
    @patch('xivo_dao.data_handler.extension.dao.get')
    def test_delete_extension_associations(self,
                                           extension_get,
                                           line_dissociate,
                                           extension_dissociate):
        extension = extension_get.return_value = Mock(id=1)
        line = Mock(id=2)

        helper.delete_extension_associations(line.id, extension.id)

        extension_get.assert_called_once_with(extension.id)
        line_dissociate.assert_called_once_with(extension)
        extension_dissociate.assert_called_once_with(extension)

    @patch('xivo_dao.data_handler.line.dao.get')
    def test_validate_no_device_when_no_device_associated(self, line_get):
        line_get.return_value = Mock(device=None)

        helper.validate_no_device(sentinel.line_id)

        line_get.assert_called_once_with(sentinel.line_id)

    @patch('xivo_dao.data_handler.line.dao.get')
    def test_validate_no_device_when_device_associated(self, line_get):
        line_get.return_value = Mock(device='1234abcdefghijklmnopquesrtlkjh')

        self.assertRaises(InvalidParametersError, helper.validate_no_device, sentinel.line_id)

        line_get.assert_called_once_with(sentinel.line_id)
