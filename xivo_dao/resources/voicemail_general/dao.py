# Copyright 2017-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession

from .persistor import VoicemailGeneralPersistor


@daosession
def find_all(session):
    return VoicemailGeneralPersistor(session).find_all()


@daosession
def edit_all(session, voicemail_general):
    VoicemailGeneralPersistor(session).edit_all(voicemail_general)
