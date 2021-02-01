# -*- coding: utf-8 -*-
# Copyright 2013-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


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
        mixmonitor_start,
        mixmonitor_stop,
        pickup,
        transfer,  # removed in asterisk 12
        xivo_user_fwd,
        xivo_from_s,
        xivo_incall,
        xivo_outcall,
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
        'MIXMONITOR_START',
        'MIXMONITOR_STOP',
        'PICKUP',
        'TRANSFER',
        'XIVO_USER_FWD',
        'XIVO_FROM_S',
        'XIVO_INCALL',
        'XIVO_OUTCALL',
    )
