# -*- coding: utf-8 -*-

import unittest

from mock import patch, Mock
from xivo_dao.data_handler.line.model import LineSIP
from xivo_dao.data_handler.line import services as line_services
from xivo_dao.data_handler.exception import MissingParametersError, \
    ElementAlreadyExistsError, InvalidParametersError, ElementCreationError


class TestLineServices(unittest.TestCase):

    @patch('xivo_dao.data_handler.line.notifier.created')
    @patch('xivo_dao.data_handler.line.dao.create')
    def test_create(self, line_dao_create, line_notifier_created):
        name = 'line'
        context = 'toto'
        secret = '1234'

        line = LineSIP(name=name, context=context, username=name, secret=secret)

        line_dao_create.return_value = line

        result = line_services.create(line)

        line_dao_create.assert_called_once_with(line)
        self.assertEquals(type(result), LineSIP)
        line_notifier_created.assert_called_once_with(line)

    @patch('xivo_dao.data_handler.line.dao.create')
    def test_create_with_missing_attributes(self, line_dao_create):
        line = LineSIP(name='lpko')

        self.assertRaises(MissingParametersError, line_services.create, line)

    @patch('xivo_dao.data_handler.line.dao.create')
    def test_create_with_error_from_dao(self, line_dao_create):
        name = 'line'
        context = 'toto'
        secret = '1234'

        line = LineSIP(name=name, context=context, username=name, secret=secret)

        error = Exception("message")
        line_dao_create.side_effect = ElementCreationError(error, '')

        self.assertRaises(ElementCreationError, line_services.create, line)

    @patch('xivo_dao.data_handler.device.services.remove_line_from_device')
    @patch('xivo_dao.data_handler.line.notifier.deleted')
    @patch('xivo_dao.data_handler.line.dao.delete')
    def test_delete(self, line_dao_delete, line_notifier_deleted, remove_line_from_device):
        line = LineSIP(id=1, username='line', secret='toto')

        line_services.delete(line)

        line_dao_delete.assert_called_once_with(line)
        line_notifier_deleted.assert_called_once_with(line)
        self.assertEquals(remove_line_from_device.call_count, 0)

    @patch('xivo_dao.data_handler.device.services.remove_line_from_device')
    @patch('xivo_dao.data_handler.line.notifier.deleted')
    @patch('xivo_dao.data_handler.line.dao.delete')
    def test_delete_with_device(self, line_dao_delete, line_notifier_deleted, remove_line_from_device):
        line = LineSIP(id=1, username='line', secret='toto', deviceid=15, num=1)

        line_services.delete(line)

        line_dao_delete.assert_called_once_with(line)
        remove_line_from_device.assert_called_once_with(line.deviceid, line.num)
        line_notifier_deleted.assert_called_once_with(line)
