# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession

from .persistor import TransportPersistor as Persistor
from .search import transport_search


@daosession
def create(session, transport):
    return Persistor(session, transport_search).create(transport)


@daosession
def delete(session, transport):
    Persistor(session, transport_search).delete(transport)


@daosession
def edit(session, transport):
    Persistor(session, transport_search).edit(transport)


@daosession
def find(session, uuid):
    return Persistor(session, transport_search).find_by({'uuid': uuid})


@daosession
def find_all_by(session, **criteria):
    return Persistor(session, transport_search).find_all_by(criteria)


@daosession
def find_by(session, **criteria):
    return Persistor(session, transport_search).find_by(criteria)


@daosession
def get(session, uuid):
    return Persistor(session, transport_search).get_by({'uuid': uuid})


@daosession
def get_by(session, **criteria):
    return Persistor(session, transport_search).get_by(criteria)


@daosession
def search(session, **parameters):
    return Persistor(session, transport_search).search(parameters)
