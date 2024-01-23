# Copyright 2017-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession

from .persistor import RegisterIAXPersistor
from .search import register_iax_search


@daosession
def search(session, **parameters):
    return RegisterIAXPersistor(session, register_iax_search).search(parameters)


@daosession
def get(session, register_iax_id):
    return RegisterIAXPersistor(session, register_iax_search).get_by(
        {'id': register_iax_id}
    )


@daosession
def find(session, register_iax_id):
    return RegisterIAXPersistor(session, register_iax_search).find_by(
        {'id': register_iax_id}
    )


@daosession
def create(session, register):
    return RegisterIAXPersistor(session, register_iax_search).create(register)


@daosession
def edit(session, register):
    RegisterIAXPersistor(session, register_iax_search).edit(register)


@daosession
def delete(session, register):
    RegisterIAXPersistor(session, register_iax_search).delete(register)
