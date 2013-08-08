# -*- coding: utf-8 -*-

import unittest

from mock import patch, Mock
from urllib2 import URLError
from xivo_dao.helpers.provd_connector import ProvdError

from xivo_dao.data_handler.line.model import LineSIP, LineOrdering, Line
from xivo_dao.data_handler.line import services as line_services
from xivo_dao.data_handler.exception import MissingParametersError, \
    ElementCreationError, InvalidParametersError


class TestLineServices(unittest.TestCase):

    @patch('xivo_dao.data_handler.line.dao.get')
    def test_get(self, mock_line_get):
        line_id = 1

        line = Mock()
        mock_line_get.return_value = line

        result = line_services.get(line_id)

        mock_line_get.assert_called_once_with(line_id)
        self.assertEquals(result, line)

    @patch('xivo_dao.data_handler.line.dao.get_by_user_id')
    def test_get_by_user_id(self, mock_get_by_user_id):
        user_id = 1

        line = Mock()
        mock_get_by_user_id.return_value = line

        result = line_services.get_by_user_id(user_id)

        mock_get_by_user_id.assert_called_once_with(user_id)
        self.assertEquals(result, line)

    @patch('xivo_dao.data_handler.line.dao.get_by_number_context')
    def test_get_by_number_context(self, mock_get_by_number_context):
        number = '1000'
        context = 'default'

        line = Mock()
        mock_get_by_number_context.return_value = line

        result = line_services.get_by_number_context(number, context)

        mock_get_by_number_context.assert_called_once_with(number, context)
        self.assertEquals(result, line)

    @patch('xivo_dao.data_handler.line.dao.find_all')
    def test_find_all(self, line_dao_find_all):
        first_user = Mock(Line)
        second_user = Mock(Line)
        expected_order = None

        expected = [first_user, second_user]

        line_dao_find_all.return_value = expected

        result = line_services.find_all()

        self.assertEquals(result, expected)

        line_dao_find_all.assert_called_once_with(order=expected_order)

    @patch('xivo_dao.data_handler.line.dao.find_all')
    def test_find_all_order_by_name(self, line_dao_find_all):
        first_user = Mock(Line)
        second_user = Mock(Line)
        expected_order = [LineOrdering.name]

        expected = [first_user, second_user]

        line_dao_find_all.return_value = expected

        result = line_services.find_all(order=[LineOrdering.name])

        self.assertEquals(result, expected)

        line_dao_find_all.assert_called_once_with(order=expected_order)

    @patch('xivo_dao.data_handler.line.dao.find_all_by_name')
    def test_find_all_by_name(self, line_dao_find_all_by_name):
        user = Mock(Line)
        name = 'Lord'

        line_dao_find_all_by_name.return_value = user

        result = line_services.find_all_by_name(name)

        self.assertEquals(result, user)
        line_dao_find_all_by_name.assert_called_once_with(name)

    @patch('xivo_dao.data_handler.line.dao.provisioning_id_exists')
    def test_make_provisioning_id(self, provd_id_exists):
        provd_id_exists.return_value = False

        provd_id = line_services.make_provisioning_id()

        self.assertEquals(len(str(provd_id)), 6)
        self.assertEquals(str(provd_id).startswith('0'), False)

    @patch('xivo_dao.data_handler.context.services.find_by_name', Mock(return_value=Mock()))
    @patch('xivo_dao.data_handler.line.services.make_provisioning_id')
    @patch('xivo_dao.data_handler.line.notifier.created')
    @patch('xivo_dao.data_handler.line.dao.create')
    def test_create(self, line_dao_create, line_notifier_created, make_provisioning_id):
        name = 'line'
        context = 'toto'
        secret = '1234'

        line = LineSIP(name=name, context=context, username=name, secret=secret)

        line_dao_create.return_value = line

        result = line_services.create(line)

        line_dao_create.assert_called_once_with(line)
        line_notifier_created.assert_called_once_with(line)
        make_provisioning_id.assert_called_with()
        self.assertEquals(type(result), LineSIP)

    @patch('xivo_dao.data_handler.line.services.make_provisioning_id')
    @patch('xivo_dao.data_handler.line.dao.create')
    def test_create_with_missing_attributes(self, line_dao_create, make_provisioning_id):
        line = LineSIP(name='lpko')

        self.assertRaises(MissingParametersError, line_services.create, line)
        self.assertEquals(make_provisioning_id.call_count, 0)

    @patch('xivo_dao.data_handler.line.services.make_provisioning_id')
    @patch('xivo_dao.data_handler.line.dao.create')
    def test_create_with_empty_attributes(self, line_dao_create, make_provisioning_id):
        line = LineSIP(context='')

        self.assertRaises(InvalidParametersError, line_services.create, line)
        self.assertEquals(make_provisioning_id.call_count, 0)

    @patch('xivo_dao.data_handler.context.services.find_by_name')
    @patch('xivo_dao.data_handler.line.services.make_provisioning_id')
    @patch('xivo_dao.data_handler.line.dao.create')
    def test_create_with_inexisting_context(self, line_dao_create, make_provisioning_id, find_context_by_name):
        line = LineSIP(context='superdupercontext')
        find_context_by_name.return_value = None

        self.assertRaises(InvalidParametersError, line_services.create, line)
        self.assertEquals(make_provisioning_id.call_count, 0)

    @patch('xivo_dao.data_handler.context.services.find_by_name', Mock(return_value=Mock()))
    @patch('xivo_dao.data_handler.line.services.make_provisioning_id')
    @patch('xivo_dao.data_handler.line.dao.create')
    def test_create_with_error_from_dao(self, line_dao_create, make_provisioning_id):
        name = 'line'
        context = 'toto'
        secret = '1234'

        line = LineSIP(name=name, context=context, username=name, secret=secret)

        error = Exception("message")
        line_dao_create.side_effect = ElementCreationError(error, '')

        self.assertRaises(ElementCreationError, line_services.create, line)
        make_provisioning_id.assert_called_with()

    @patch('xivo_dao.data_handler.device.services.remove_line_from_device')
    @patch('xivo_dao.data_handler.line.notifier.deleted')
    @patch('xivo_dao.data_handler.line.dao.delete')
    def test_delete(self, line_dao_delete, line_notifier_deleted, remove_line_from_device):
        line_id = 1
        username = 'line'
        secret = 'toto'

        line = LineSIP(id=line_id, username=username, secret=secret)

        line_services.delete(line)

        line_dao_delete.assert_called_once_with(line)
        line_notifier_deleted.assert_called_once_with(line)
        self.assertEquals(remove_line_from_device.call_count, 0)

    @patch('xivo_dao.data_handler.device.services.remove_line_from_device')
    @patch('xivo_dao.data_handler.line.notifier.deleted')
    @patch('xivo_dao.data_handler.line.dao.delete')
    def test_delete_with_device(self, line_dao_delete, line_notifier_deleted, remove_line_from_device):
        line_id = 1
        username = 'line'
        secret = 'toto'
        device_id = 15
        num = 1

        line = LineSIP(id=line_id, username=username, secret=secret, device=device_id, num=num)

        line_services.delete(line)

        line_dao_delete.assert_called_once_with(line)
        remove_line_from_device.assert_called_once_with(line.device, line.num)
        line_notifier_deleted.assert_called_once_with(line)

    @patch('xivo_dao.data_handler.device.services.remove_line_from_device')
    @patch('xivo_dao.data_handler.line.notifier.deleted')
    @patch('xivo_dao.data_handler.line.dao.delete')
    def test_delete_with_device_error(self, line_dao_delete, line_notifier_deleted, remove_line_from_device):
        line_id = 1
        username = 'line'
        secret = 'toto'
        device_id = 15
        num = 1

        line = LineSIP(id=line_id, username=username, secret=secret, device=device_id, num=num)

        remove_line_from_device.side_effect = URLError('')

        self.assertRaises(ProvdError, line_services.delete, line)

        line_dao_delete.assert_called_once_with(line)
        remove_line_from_device.assert_called_once_with(line.device, line.num)
        self.assertEquals(line_notifier_deleted.call_count, 0)
