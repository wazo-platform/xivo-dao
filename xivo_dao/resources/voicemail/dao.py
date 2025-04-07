# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession

from .persistor import VoicemailPersistor
from .search import voicemail_search


@daosession
def search(session, tenant_uuids=None, **parameters):
    return VoicemailPersistor(session, voicemail_search, tenant_uuids).search(
        parameters
    )


@daosession
def get(session, voicemail_id, tenant_uuids=None):
    return VoicemailPersistor(session, voicemail_search, tenant_uuids).get_by(
        {'id': voicemail_id}
    )


@daosession
def get_by(session, tenant_uuids=None, **criteria):
    return VoicemailPersistor(session, voicemail_search, tenant_uuids).get_by(criteria)


@daosession
def find(session, voicemail_id, tenant_uuids=None):
    return VoicemailPersistor(session, voicemail_search, tenant_uuids).find_by(
        {'id': voicemail_id}
    )


@daosession
def find_by(session, tenant_uuids=None, **criteria):
    return VoicemailPersistor(session, voicemail_search, tenant_uuids).find_by(criteria)


@daosession
def find_all_by(session, tenant_uuids=None, **criteria):
    return VoicemailPersistor(session, voicemail_search, tenant_uuids).find_all_by(
        criteria
    )


@daosession
def create(session, voicemail):
    return VoicemailPersistor(session, voicemail_search).create(voicemail)


@daosession
def edit(session, voicemail):
    VoicemailPersistor(session, voicemail_search).edit(voicemail)


@daosession
def delete(session, voicemail):
    VoicemailPersistor(session, voicemail_search).delete(voicemail)
