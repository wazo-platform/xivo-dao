# -*- coding: utf-8 -*-

import unittest

from mock import patch
from xivo_dao.data_handler.extension.model import Extension
from xivo_dao.data_handler.extension import services as extension_services
from xivo_dao.data_handler.exception import MissingParametersError, \
    InvalidParametersError, ElementCreationError


class TestExtension(unittest.TestCase):

    def test_create_no_properties(self):
        extension = Extension(exten='1234')

        self.assertRaises(MissingParametersError, extension_services.create, extension)

    @patch('xivo_dao.data_handler.extension.notifier.created')
    @patch('xivo_dao.data_handler.extension.dao.create')
    def test_create_empty_exten(self, extension_dao_create, extension_notifier_created):
        exten = ''
        context = 'toto'

        extension = Extension(exten=exten,
                              context=context,
                              type='user',
                              typeval='0')

        self.assertRaises(InvalidParametersError, extension_services.create, extension)

    @patch('xivo_dao.data_handler.extension.notifier.created')
    @patch('xivo_dao.data_handler.extension.dao.create')
    def test_create_empty_context(self, extension_dao_create, extension_notifier_created):
        exten = '1324'
        context = ''

        extension = Extension(exten=exten,
                              context=context,
                              type='user',
                              typeval='0')

        self.assertRaises(InvalidParametersError, extension_services.create, extension)

    @patch('xivo_dao.data_handler.extension.notifier.created')
    @patch('xivo_dao.data_handler.extension.dao.create')
    def test_create(self, extension_dao_create, extension_notifier_created):
        exten = 'extension'
        context = 'toto'

        extension = Extension(exten=exten,
                              context=context,
                              type='user',
                              typeval='0')

        extension_dao_create.return_value = extension

        result = extension_services.create(extension)

        extension_dao_create.assert_called_once_with(extension)
        self.assertEquals(type(result), Extension)
        extension_notifier_created.assert_called_once_with(extension)

    @patch('xivo_dao.data_handler.extension.dao.create')
    def test_create_with_error_from_dao(self, extension_dao_create):
        exten = 'extension'
        context = 'toto'

        extension = Extension(exten=exten,
                              context=context,
                              type='user',
                              typeval='0')

        error = Exception("message")
        extension_dao_create.side_effect = ElementCreationError(error, '')

        self.assertRaises(ElementCreationError, extension_services.create, extension)

    @patch('xivo_dao.data_handler.line.dao.unassociate_extension')
    @patch('xivo_dao.data_handler.extension.notifier.deleted')
    @patch('xivo_dao.data_handler.extension.dao.delete')
    def test_delete(self, extension_dao_delete, extension_notifier_deleted, unassociate_extension):
        exten = 'extension'
        context = 'toto'
        extension = Extension(id=1,
                              exten=exten,
                              context=context,
                              type='user',
                              typeval='0')

        extension_services.delete(extension)

        unassociate_extension.assert_called_once_with(extension)
        extension_dao_delete.assert_called_once_with(extension)
        extension_notifier_deleted.assert_called_once_with(extension)
