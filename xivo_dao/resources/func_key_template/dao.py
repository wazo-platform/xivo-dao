# Copyright 2014-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession
from xivo_dao.helpers.db_utils import flush_session

from xivo_dao.resources.func_key_template.persistor import build_persistor


@daosession
def search(session, tenant_uuids=None, **parameters):
    persistor = build_persistor(session, tenant_uuids=tenant_uuids)
    return persistor.search(parameters)


@daosession
def create(session, template):
    persistor = build_persistor(session)
    with flush_session(session):
        return persistor.create(template)


@daosession
def get(session, template_id, tenant_uuids=None):
    persistor = build_persistor(session, tenant_uuids=tenant_uuids)
    return persistor.get(template_id)


@daosession
def edit(session, template):
    persistor = build_persistor(session)
    with flush_session(session):
        return persistor.edit(template)


@daosession
def delete(session, template):
    persistor = build_persistor(session)
    return persistor.delete(template)
