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

import unittest
from mock import patch, Mock

from xivo_dao.data_handler.user_cti_profile import notifier
from xivo_dao.data_handler.user_cti_profile.model import UserCtiProfile


class TestUserVoicemailNotifier(unittest.TestCase):

    @patch('xivo_bus.resources.user_cti_profile.event.UserCtiProfileAssociatedEvent')
    @patch('xivo_dao.helpers.bus_manager.send_bus_command')
    def test_associated(self, send_bus_command, UserCtiProfileAssociatedEvent):
        new_event = UserCtiProfileAssociatedEvent.return_value = Mock()
        user_cti_profile = UserCtiProfile(user_id=1, cti_profile_id=2)

        notifier.associated(user_cti_profile)

        UserCtiProfileAssociatedEvent.assert_called_once_with(user_cti_profile.user_id,
                                                              user_cti_profile.cti_profile_id)
        send_bus_command.assert_called_once_with(new_event)

    @patch('xivo_bus.resources.user_cti_profile.event.UserCtiProfileDissociatedEvent')
    @patch('xivo_dao.helpers.bus_manager.send_bus_command')
    def test_dissociated(self, send_bus_command, UserCtiProfileDissociatedEvent):
        new_event = UserCtiProfileDissociatedEvent.return_value = Mock()
        user_cti_profile = UserCtiProfile(user_id=1, cti_profile_id=2)

        notifier.dissociated(user_cti_profile)

        UserCtiProfileDissociatedEvent.assert_called_once_with(user_cti_profile.user_id,
                                                               user_cti_profile.cti_profile_id)
        send_bus_command.assert_called_once_with(new_event)
