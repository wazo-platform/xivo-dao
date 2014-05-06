# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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
from mock import Mock, patch

from xivo_dao.data_handler.context.model import Context
from xivo_dao.data_handler.line_extension.model import LineExtension
from xivo_dao.data_handler.line_extension.handler import LineExtensionHandler


class TestLineExtensionHandler(unittest.TestCase):
    pass


class TestGivenEmptyRegistry(TestLineExtensionHandler):

    def setUp(self):
        self.handler = LineExtensionHandler(Mock(), Mock(), {})

    def test_when_associating_then_raises_error(self):
        self.assertRaises(NotImplementedError, self.handler.associate, Mock())

    def test_when_dissociating_then_raises_error(self):
        self.assertRaises(NotImplementedError, self.handler.associate, Mock())

    def test_when_validating_then_raises_error(self):
        self.assertRaises(NotImplementedError, self.handler.validate, Mock())


class TestGivenUnknownContextType(TestLineExtensionHandler):

    def setUp(self):
        self.context_dao = Mock()
        self.context_dao.get_by_extension_id.return_value = Mock(Context, type='unknown')
        self.line_extension = LineExtension(extension_id=1)
        self.handler = LineExtensionHandler(self.context_dao, Mock(), {})

    def test_when_associating_then_raises_error(self):
        self.assertRaises(NotImplementedError, self.handler.associate, self.line_extension)
        self.context_dao.get_by_extension_id.assert_called_once_with(self.line_extension.extension_id)

    def test_when_dissociating_then_raises_error(self):
        self.assertRaises(NotImplementedError, self.handler.dissociate, self.line_extension)
        self.context_dao.get_by_extension_id.assert_called_once_with(self.line_extension.extension_id)

    def test_when_validating_then_raises_error(self):
        self.assertRaises(NotImplementedError, self.handler.validate, self.line_extension)
        self.context_dao.get_by_extension_id.assert_called_once_with(self.line_extension.extension_id)


class TestGivenKnownContextType(TestLineExtensionHandler):

    def setUp(self):
        self.context_dao = Mock()
        self.internal_handler = Mock()
        self.validator = Mock()
        self.line_extension = Mock(LineExtension, extension_id=1)

        self.context_dao.get_by_extension_id.return_value = Mock(Context, type='internal')
        registry = {'internal': self.internal_handler}

        self.handler = LineExtensionHandler(self.context_dao, self.validator, registry)

    def test_when_associating_then_calls_registry(self):
        self.handler.associate(self.line_extension)
        self.internal_handler.associate.assert_called_once_with(self.line_extension)

    def test_when_associating_then_validates_model(self):
        with patch.object(self.handler, 'validate') as mock_validate:
            self.handler.associate(self.line_extension)
            mock_validate.assert_called_once_with(self.line_extension)

    def test_when_validating_then_calls_approprite_validators(self):
        self.handler.validate(self.line_extension)

        self.validator.validate_model.assert_called_once_with(self.line_extension)
        self.validator.validate_line.assert_called_once_with(self.line_extension)
        self.validator.validate_extension.assert_called_once_with(self.line_extension)

    def test_when_validating_then_calls_validator_from_registry(self):
        self.handler.validate(self.line_extension)

        self.internal_handler.validate.assert_called_once_with(self.line_extension)

    def test_when_dissociating_then_calls_registry(self):
        self.handler.dissociate(self.line_extension)

        self.internal_handler.dissociate.assert_called_once_with(self.line_extension)

    def test_when_dissociating_then_validates_model(self):
        with patch.object(self.handler, 'validate') as mock_validate:
            self.handler.dissociate(self.line_extension)
            mock_validate.assert_called_once_with(self.line_extension)
