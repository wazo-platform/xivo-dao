# Copyright 2017-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession

from .persistor import IAXGeneralPersistor


@daosession
def find_all(session):
    return IAXGeneralPersistor(session).find_all()


@daosession
def edit_all(session, iax_general):
    IAXGeneralPersistor(session).edit_all(iax_general)
