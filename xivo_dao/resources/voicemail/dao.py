# -*- coding: utf-8 -*-
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

from .persistor import VoicemailPersistor
from .search import voicemail_search

from xivo_dao.helpers.db_manager import daosession


@daosession
def search(session, **parameters):
    return VoicemailPersistor(session, voicemail_search).search(parameters)


@daosession
def get(session, voicemail_id):
    return VoicemailPersistor(session, voicemail_search).get_by({'id': voicemail_id})


@daosession
def get_by(session, **criteria):
    return VoicemailPersistor(session, voicemail_search).get_by(criteria)


@daosession
def find(session, voicemail_id):
    return VoicemailPersistor(session, voicemail_search).find_by({'id': voicemail_id})


@daosession
def find_by(session, **criteria):
    return VoicemailPersistor(session, voicemail_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return VoicemailPersistor(session, voicemail_search).find_all_by(criteria)


@daosession
def create(session, voicemail):
    return VoicemailPersistor(session, voicemail_search).create(voicemail)


@daosession
def edit(session, voicemail):
    VoicemailPersistor(session, voicemail_search).edit(voicemail)


@daosession
def delete(session, voicemail):
    VoicemailPersistor(session, voicemail_search).delete(voicemail)
