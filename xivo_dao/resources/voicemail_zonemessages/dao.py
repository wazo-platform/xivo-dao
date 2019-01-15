# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession

from .persistor import VoicemailZoneMessagesPersistor


@daosession
def find_all(session):
    return VoicemailZoneMessagesPersistor(session).find_all()


@daosession
def edit_all(session, voicemail_zonemessages):
    VoicemailZoneMessagesPersistor(session).edit_all(voicemail_zonemessages)
