# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession

from .persistor import Persistor


@daosession
def find_by(session, tenant_uuids=None, **criteria):
    return Persistor(session, tenant_uuids).find_by(criteria)


@daosession
def find_all_by(session, tenant_uuids=None, **criteria):
    return Persistor(session, tenant_uuids).find_all_by(criteria)


@daosession
def get(session, config_uuid, tenant_uuids=None):
    return Persistor(session, tenant_uuids).get_by({'uuid': config_uuid})


@daosession
def create(session, model):
    return Persistor(session).create(model)


@daosession
def edit(session, model):
    Persistor(session).edit(model)


@daosession
def delete(session, model):
    return Persistor(session).delete(model)
