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

from mock import patch, Mock
from xivo_dao.helpers.abstract_model import SearchResult
from xivo_dao.data_handler.voicemail import services as voicemail_services
from xivo_dao.data_handler.voicemail.model import Voicemail, VoicemailOrder
from xivo_dao.data_handler.exception import MissingParametersError, \
    InvalidParametersError, ElementAlreadyExistsError, ElementCreationError, \
    ElementDeletionError, NonexistentParametersError


class TestVoicemail(unittest.TestCase):

    @patch('xivo_dao.data_handler.voicemail.dao.find_all')
    def test_find_all(self, mock_find_all):
        voicemails = Mock(SearchResult)
        mock_find_all.return_value = voicemails

        result = voicemail_services.find_all()

        mock_find_all.assert_called_once_with(skip=None, limit=None, order=None, direction=None, search=None)
        self.assertEquals(result, voicemails)

    @patch('xivo_dao.data_handler.voicemail.dao.find_all')
    def test_find_all_with_parameters(self, mock_find_all):
        voicemails = Mock(SearchResult)
        mock_find_all.return_value = voicemails

        result = voicemail_services.find_all(skip=1,
                                             limit=2,
                                             order=VoicemailOrder.number,
                                             direction='asc',
                                             search='toto')

        mock_find_all.assert_called_once_with(skip=1, limit=2,
                                              order=VoicemailOrder.number,
                                              direction='asc',
                                              search='toto')

        self.assertEquals(result, voicemails)

    @patch('xivo_dao.data_handler.voicemail.notifier.deleted')
    @patch('xivo_dao.data_handler.voicemail.dao.delete')
    def test_delete_raises_exception(self, voicemail_dao_delete, voicemail_notifier_deleted):
        voicemail = Mock(Voicemail)
        voicemail.id = 12
        voicemail.number = '42'
        voicemail.context = 'default'

        voicemail_dao_delete.side_effect = ElementDeletionError('voicemail', '')

        self.assertRaises(ElementDeletionError, voicemail_services.delete, voicemail)
        self.assertEquals(voicemail_notifier_deleted.call_count, 0)

    @patch('xivo_dao.data_handler.voicemail.notifier.deleted')
    @patch('xivo_dao.data_handler.voicemail.dao.delete')
    @patch('xivo_dao.helpers.sysconfd_connector.delete_voicemail_storage')
    def test_delete(self, sysconfd_connector_delete_voicemail_storage, voicemail_dao_delete, voicemail_notifier_deleted):
        voicemail_id = 12
        number = '42'
        context = 'default'
        voicemail = Mock(Voicemail)
        voicemail.id = voicemail_id
        voicemail.number = number
        voicemail.context = context

        voicemail_services.delete(voicemail)

        voicemail_dao_delete.assert_called_once_with(voicemail)
        sysconfd_connector_delete_voicemail_storage.assert_called_once_with(number, context)
        voicemail_notifier_deleted.assert_called_once_with(voicemail)

    @patch('xivo_dao.data_handler.voicemail.notifier')
    def test_create_no_properties(self, voicemail_notifier):
        voicemail = Voicemail()

        self.assertRaises(MissingParametersError, voicemail_services.create, voicemail)
        self.assertEquals(voicemail_notifier.created.call_count, 0)

    @patch('xivo_dao.helpers.validator.is_existing_context', Mock(return_value=True))
    @patch('xivo_dao.data_handler.voicemail.notifier.created')
    @patch('xivo_dao.data_handler.voicemail.dao.create')
    def test_create_empty_name(self, voicemail_dao_create, voicemail_notifier_created):
        name = ''
        number = '42'
        context = 'default'

        voicemail = Voicemail(name=name,
                              number=number,
                              context=context)

        self.assertRaises(InvalidParametersError, voicemail_services.create, voicemail)
        self.assertEquals(voicemail_dao_create.call_count, 0)
        self.assertEquals(voicemail_notifier_created.call_count, 0)

    @patch('xivo_dao.helpers.validator.is_existing_context', Mock(return_value=True))
    @patch('xivo_dao.data_handler.voicemail.notifier.created')
    @patch('xivo_dao.data_handler.voicemail.dao.create')
    def test_create_invalid_number(self, voicemail_dao_create, voicemail_notifier_created):
        name = 'voicemail'
        number = 'wrong_number'
        context = 'default'

        voicemail = Voicemail(name=name,
                              number=number,
                              context=context)

        self.assertRaises(InvalidParametersError, voicemail_services.create, voicemail)
        self.assertEquals(voicemail_dao_create.call_count, 0)
        self.assertEquals(voicemail_notifier_created.call_count, 0)

    @patch('xivo_dao.helpers.validator.is_existing_context', Mock(return_value=False))
    @patch('xivo_dao.data_handler.voicemail.notifier.created')
    @patch('xivo_dao.data_handler.voicemail.dao.create')
    def test_create_invalid_context(self, voicemail_dao_create, voicemail_notifier_created):
        name = 'voicemail'
        number = '42'
        context = 'inexistant_context'

        voicemail = Voicemail(name=name,
                              number=number,
                              context=context)

        self.assertRaises(NonexistentParametersError, voicemail_services.create, voicemail)
        self.assertEquals(voicemail_dao_create.call_count, 0)
        self.assertEquals(voicemail_notifier_created.call_count, 0)

    @patch('xivo_dao.helpers.validator.is_existing_context', Mock(return_value=True))
    @patch('xivo_dao.data_handler.voicemail.dao.get_by_number_context', Mock(return_value=Mock()))
    @patch('xivo_dao.data_handler.voicemail.notifier.created')
    @patch('xivo_dao.data_handler.voicemail.dao.create')
    def test_create_same_context_and_number(self, voicemail_dao_create, voicemail_notifier_created):
        name = 'voicemail'
        number = '42'
        context = 'existing_context'

        voicemail = Voicemail(name=name,
                              number=number,
                              context=context)

        voicemail_mock = Mock(Voicemail)
        voicemail_mock.number = '42'
        voicemail_mock.context = 'existing_context'

        self.assertRaises(ElementAlreadyExistsError, voicemail_services.create, voicemail)
        self.assertEquals(voicemail_notifier_created.call_count, 0)

    @patch('xivo_dao.helpers.validator.is_existing_context', Mock(return_value=True))
    @patch('xivo_dao.data_handler.voicemail.dao.get_by_number_context', Mock(return_value=None))
    @patch('xivo_dao.data_handler.voicemail.notifier.created')
    @patch('xivo_dao.data_handler.voicemail.dao.create')
    def test_create(self, voicemail_dao_create, voicemail_notifier_created):
        name = 'voicemail'
        number = '42'
        context = 'default'

        voicemail = Voicemail(name=name,
                              number=number,
                              context=context)

        voicemail_dao_create.return_value = voicemail

        result = voicemail_services.create(voicemail)

        voicemail_dao_create.assert_called_once_with(voicemail)
        self.assertEquals(type(result), Voicemail)
        voicemail_notifier_created.assert_called_once_with(voicemail)

    @patch('xivo_dao.helpers.validator.is_existing_context', Mock(return_value=True))
    @patch('xivo_dao.data_handler.voicemail.dao.get_by_number_context', Mock(return_value=None))
    @patch('xivo_dao.data_handler.voicemail.notifier.created')
    @patch('xivo_dao.data_handler.voicemail.dao.create')
    def test_create_with_error_from_dao(self, voicemail_dao_create, voicemail_notifier_created):
        name = 'toto'
        number = '4692'
        context = 'default'

        voicemail = Voicemail(name=name,
                              number=number,
                              context=context)

        voicemail_dao_create.side_effect = ElementCreationError('voicemail', '')

        self.assertRaises(ElementCreationError, voicemail_dao_create, voicemail)
        self.assertEquals(voicemail_notifier_created.call_count, 0)
