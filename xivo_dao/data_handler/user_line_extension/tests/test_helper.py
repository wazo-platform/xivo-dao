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
from xivo_dao.data_handler.line.model import LineSIP
from xivo_dao.data_handler.extension.model import Extension

from mock import Mock, patch, sentinel
from unittest import TestCase

from .. import helper


class TestULEHelper(TestCase):

    @patch('xivo_dao.data_handler.extension.dao.dissociate_extension')
    @patch('xivo_dao.data_handler.line.dao.dissociate_extension')
    @patch('xivo_dao.data_handler.extension.dao.get')
    def test_delete_extension_associations(self,
                                           extension_get,
                                           line_dissociate,
                                           extension_dissociate):
        extension = extension_get.return_value = Mock(Extension, id=1)

        helper.delete_extension_associations(extension.id)

        extension_get.assert_called_once_with(extension.id)
        line_dissociate.assert_called_once_with(extension)
        extension_dissociate.assert_called_once_with(extension)

    @patch('xivo_dao.data_handler.line.dao.get')
    def test_validate_no_device_when_no_device_associated(self, line_get):
        line_get.return_value = Mock(LineSIP, device_id=None)

        helper.validate_no_device(sentinel.line_id)

        line_get.assert_called_once_with(sentinel.line_id)

    @patch('xivo_dao.data_handler.line.dao.get')
    def test_validate_no_device_when_device_associated(self, line_get):
        line_get.return_value = Mock(LineSIP, device_id='1234abcdefghijklmnopquesrtlkjh')

        self.assertRaises(InvalidParametersError, helper.validate_no_device, sentinel.line_id)

        line_get.assert_called_once_with(sentinel.line_id)
