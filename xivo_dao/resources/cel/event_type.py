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


class CELEventType(object):
    eventtype_list = (
        answer,
        app_end,
        app_start,
        attended_transfer,
        blind_transfer,
        bridge_end,  # removed in asterisk 12
        bridge_start,  # removed in asterisk 12
        bridge_enter,
        bridge_exit,
        chan_start,
        chan_end,
        forward,
        hangup,
        linkedid_end,
        pickup,
        transfer,  # removed in asterisk 12
        xivo_user_fwd,
        xivo_from_s,
    ) = (
        'ANSWER',
        'APP_END',
        'APP_START',
        'ATTENDEDTRANSFER',
        'BLINDTRANSFER',
        'BRIDGE_END',
        'BRIDGE_START',
        'BRIDGE_ENTER',
        'BRIDGE_EXIT',
        'CHAN_START',
        'CHAN_END',
        'FORWARD',
        'HANGUP',
        'LINKEDID_END',
        'PICKUP',
        'TRANSFER',
        'XIVO_USER_FWD',
        'XIVO_FROM_S',
    )
