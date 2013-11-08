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

from xivo_dao.data_handler.exception import ElementCreationError
from xivo_dao.data_handler.exception import ElementDeletionError
from xivo_dao.data_handler.exception import ElementEditionError

from xivo_dao.data_handler.voicemail import services as voicemail_services
from xivo_dao.data_handler.voicemail.model import Voicemail, VoicemailOrder
from xivo_dao.helpers.abstract_model import SearchResult


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

    @patch('xivo_dao.data_handler.voicemail.validator.validate_delete')
    @patch('xivo_dao.data_handler.voicemail.notifier.deleted')
    @patch('xivo_dao.data_handler.voicemail.dao.delete')
    @patch('xivo_dao.helpers.sysconfd_connector.delete_voicemail_storage')
    def test_delete_raises_exception(self,
                                     sysconf_delete_voicemail,
                                     voicemail_dao_delete,
                                     voicemail_notifier_deleted,
                                     validate_delete):
        voicemail = Mock(Voicemail)

        voicemail_dao_delete.side_effect = ElementDeletionError('voicemail', '')

        self.assertRaises(ElementDeletionError, voicemail_services.delete, voicemail)
        validate_delete.assert_called_once_with(voicemail)
        self.assertEquals(voicemail_notifier_deleted.call_count, 0)
        self.assertEquals(sysconf_delete_voicemail.call_count, 0)

    @patch('xivo_dao.data_handler.voicemail.validator.validate_delete')
    @patch('xivo_dao.data_handler.voicemail.notifier.deleted')
    @patch('xivo_dao.data_handler.voicemail.dao.delete')
    @patch('xivo_dao.helpers.sysconfd_connector.delete_voicemail_storage')
    def test_delete(self,
                    sysconfd_connector_delete_voicemail_storage,
                    voicemail_dao_delete,
                    voicemail_notifier_deleted,
                    validate_delete):
        voicemail_id = 12
        number = '42'
        context = 'default'

        voicemail = Mock(Voicemail)
        voicemail.id = voicemail_id
        voicemail.number = number
        voicemail.context = context

        voicemail_services.delete(voicemail)

        validate_delete.assert_called_once_with(voicemail)
        voicemail_dao_delete.assert_called_once_with(voicemail)
        sysconfd_connector_delete_voicemail_storage.assert_called_once_with(number, context)
        voicemail_notifier_deleted.assert_called_once_with(voicemail)

    @patch('xivo_dao.data_handler.voicemail.validator.validate_create')
    @patch('xivo_dao.data_handler.voicemail.notifier.created')
    @patch('xivo_dao.data_handler.voicemail.dao.create')
    def test_create(self, voicemail_dao_create, voicemail_notifier_created, validate_create):
        name = 'voicemail'
        number = '42'
        context = 'default'

        voicemail = Voicemail(name=name,
                              number=number,
                              context=context)

        voicemail_dao_create.return_value = voicemail

        result = voicemail_services.create(voicemail)

        validate_create.assert_called_once_with(voicemail)
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

    @patch('xivo_dao.data_handler.voicemail.validator.validate_edit')
    @patch('xivo_dao.data_handler.voicemail.notifier.edited')
    @patch('xivo_dao.data_handler.voicemail.dao.edit')
    def test_edit(self, voicemail_dao_edit, voicemail_notifier_edited, validate_edit):
        name = 'voicemail'
        number = '25880'
        context = 'default'

        voicemail = Voicemail(name=name,
                              number=number,
                              context=context)

        voicemail_services.edit(voicemail)

        validate_edit.assert_called_once_with(voicemail)
        voicemail_dao_edit.assert_called_once_with(voicemail)
        voicemail_notifier_edited.assert_called_once_with(voicemail)

    @patch('xivo_dao.data_handler.voicemail.validator.validate_edit')
    @patch('xivo_dao.data_handler.voicemail.notifier.edited')
    @patch('xivo_dao.data_handler.voicemail.dao.edit')
    def test_edit_with_error_from_dao(self, voicemail_dao_edit, voicemail_notifier_edited, validate_edit):
        name = 'voicemail'
        number = '25880'
        context = 'default'

        voicemail = Voicemail(name=name,
                              number=number,
                              context=context)

        voicemail_dao_edit.side_effect = ElementEditionError('voicemail', '')

        self.assertRaises(ElementEditionError, voicemail_services.edit, voicemail)
        validate_edit.assert_called_once_with(voicemail)
        self.assertEquals(voicemail_notifier_edited.call_count, 0)
