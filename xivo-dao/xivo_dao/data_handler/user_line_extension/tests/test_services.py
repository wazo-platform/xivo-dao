# -*- coding: utf-8 -*-

import unittest

from mock import patch, Mock
from xivo_dao.data_handler.user_line_extension.model import UserLineExtension
from xivo_dao.data_handler.user_line_extension import services as user_line_extension_services
from xivo_dao.data_handler.exception import MissingParametersError, \
    InvalidParametersError, ElementCreationError


class TestUserLineExtensionServices(unittest.TestCase):

    def test_create_no_properties(self):
        user_line_extension = UserLineExtension()

        self.assertRaises(MissingParametersError, user_line_extension_services.create, user_line_extension)

    @patch('xivo_dao.data_handler.user_line_extension.notifier.created')
    @patch('xivo_dao.data_handler.user_line_extension.dao.create')
    def test_create_invalid_exten_id(self, user_line_extension_dao_create, user_line_extension_notifier_created):
        ule = UserLineExtension(user_id=5898,
                                line_id=52,
                                extension_id='tot',
                                main_user=True,
                                main_line=False)

        self.assertRaises(InvalidParametersError, user_line_extension_services.create, ule)

    @patch('xivo_dao.data_handler.user_line_extension.notifier.created')
    @patch('xivo_dao.data_handler.user_line_extension.dao.create')
    def test_create_invalid_main_line(self, user_line_extension_dao_create, user_line_extension_notifier_created):
        ule = UserLineExtension(user_id=5898,
                                line_id=52,
                                extension_id=445,
                                main_user=True,
                                main_line='ok')

        self.assertRaises(InvalidParametersError, user_line_extension_services.create, ule)

    @patch('xivo_dao.data_handler.user_line_extension.notifier.created')
    @patch('xivo_dao.data_handler.user_line_extension.dao.create')
    def test_create_invalid_main_user(self, user_line_extension_dao_create, user_line_extension_notifier_created):
        ule = UserLineExtension(user_id=5898,
                                line_id=52,
                                extension_id=445,
                                main_user='oui',
                                main_line=False)

        self.assertRaises(InvalidParametersError, user_line_extension_services.create, ule)

    @patch('xivo_dao.data_handler.user_line_extension.notifier.created')
    @patch('xivo_dao.data_handler.user_line_extension.dao.create')
    def test_create_without_line_id(self, user_line_extension_dao_create, user_line_extension_notifier_created):
        ule = UserLineExtension(user_id=5898,
                                extension_id=52,
                                main_user=True,
                                main_line=False)

        self.assertRaises(MissingParametersError, user_line_extension_services.create, ule)

    @patch('xivo_dao.data_handler.user_line_extension.notifier.created')
    @patch('xivo_dao.data_handler.user_line_extension.dao.create')
    def test_create(self, user_line_extension_dao_create, user_line_extension_notifier_created):
        ule = UserLineExtension(user_id=5898,
                                line_id=52,
                                extension_id=52,
                                main_user=True,
                                main_line=False)

        user_line_extension_dao_create.return_value = ule

        result = user_line_extension_services.create(ule)

        user_line_extension_dao_create.assert_called_once_with(ule)
        self.assertEquals(type(result), UserLineExtension)
        user_line_extension_notifier_created.assert_called_once_with(ule)

    @patch('xivo_dao.data_handler.user_line_extension.dao.create')
    def test_create_with_error_from_dao(self, user_line_extension_dao_create):
        ule = UserLineExtension(user_id=5898,
                                line_id=52,
                                extension_id=52,
                                main_user=True,
                                main_line=False)

        error = Exception("message")
        user_line_extension_dao_create.side_effect = ElementCreationError(error, '')

        self.assertRaises(ElementCreationError, user_line_extension_services.create, ule)

    @patch('xivo_dao.data_handler.user_line_extension.notifier.edited')
    @patch('xivo_dao.data_handler.user_line_extension.dao.edit')
    def test_edit(self, user_dao_edit, user_notifier_edited):
        ule = UserLineExtension(user_id=5898,
                                line_id=52,
                                extension_id=52,
                                main_user=True,
                                main_line=False)

        user_line_extension_services.edit(ule)

        user_dao_edit.assert_called_once_with(ule)
        user_notifier_edited.assert_called_once_with(ule)

    @patch('xivo_dao.data_handler.user.services.delete', Mock(return_value=None))
    @patch('xivo_dao.data_handler.line.services.delete', Mock(return_value=None))
    @patch('xivo_dao.data_handler.extension.services.delete', Mock(return_value=None))
    @patch('xivo_dao.data_handler.extension.services.get')
    @patch('xivo_dao.data_handler.user.services.get')
    @patch('xivo_dao.data_handler.line.services.get')
    @patch('xivo_dao.data_handler.user_line_extension.notifier.deleted')
    @patch('xivo_dao.data_handler.user_line_extension.dao.delete')
    def test_delete(self, user_line_extension_dao_delete, user_line_extension_notifier_deleted, line_get, user_get, extension_get):
        ule = UserLineExtension(user_id=5898,
                                line_id=52,
                                extension_id=52,
                                main_user=True,
                                main_line=False)

        user_line_extension_services.delete(ule)

        user_line_extension_dao_delete.assert_called_once_with(ule)
        user_line_extension_notifier_deleted.assert_called_once_with(ule)
        line_get.assert_called_once_with(ule.line_id)
        user_get.assert_called_once_with(ule.user_id)
        extension_get.assert_called_once_with(ule.extension_id)
