# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import Session
from xivo_dao.resources.utils.search import SearchResult

from .fixes import ExtensionFixes
from .persistor import ExtensionPersistor


def persistor(tenant_uuids=None):
    return ExtensionPersistor(Session, tenant_uuids)


def get_by(tenant_uuids=None, **criteria):
    return persistor(tenant_uuids).get_by(criteria)


def find_by(tenant_uuids=None, **criteria):
    return persistor(tenant_uuids).find_by(criteria)


def find_all_by(tenant_uuids=None, **criteria):
    return persistor(tenant_uuids).find_all_by(criteria)


def get(id, tenant_uuids=None):
    return persistor(tenant_uuids).get_by({'id': id})


def find(id, tenant_uuids=None):
    return persistor(tenant_uuids).find_by({'id': id})


def search(tenant_uuids=None, **parameters):
    total, items = persistor(tenant_uuids).search(parameters)
    return SearchResult(total, items)


def create(extension):
    return persistor().create(extension)


def edit(extension):
    persistor().edit(extension)
    ExtensionFixes(Session).fix(extension.id)


def delete(extension):
    persistor().delete(extension)


def associate_incall(incall, extension):
    persistor().associate_incall(incall, extension)
    ExtensionFixes(Session).fix(extension.id)


def dissociate_incall(incall, extension):
    persistor().dissociate_incall(incall, extension)
    ExtensionFixes(Session).fix(extension.id)


def associate_group(group, extension):
    persistor().associate_group(group, extension)


def dissociate_group(group, extension):
    persistor().dissociate_group(group, extension)


def associate_queue(queue, extension):
    persistor().associate_queue(queue, extension)
    queue.fix_extension()


def dissociate_queue(queue, extension):
    persistor().dissociate_queue(queue, extension)
    queue.fix_extension()


def associate_conference(conference, extension):
    persistor().associate_conference(conference, extension)


def dissociate_conference(conference, extension):
    persistor().dissociate_conference(conference, extension)


def associate_parking_lot(parking_lot, extension):
    persistor().associate_parking_lot(parking_lot, extension)


def dissociate_parking_lot(parking_lot, extension):
    persistor().dissociate_parking_lot(parking_lot, extension)
