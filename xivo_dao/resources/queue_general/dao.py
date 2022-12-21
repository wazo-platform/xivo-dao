# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession

from .persistor import QueueGeneralPersistor


@daosession
def find_all(session):
    return QueueGeneralPersistor(session).find_all()


@daosession
def edit_all(session, queue_general):
    QueueGeneralPersistor(session).edit_all(queue_general)
