# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from contextlib import contextmanager

from xivo_dao.helpers.db_manager import Session
from xivo_dao.resources.func_key_template.persistor import (
    build_persistor as build_template_persistor,
)
from xivo_dao.resources.user.fixes import UserFixes
from xivo_dao.resources.user.persistor import UserPersistor
from xivo_dao.resources.user.search import user_search
from xivo_dao.resources.user.view import user_view


def persistor(tenant_uuids=None):
    return UserPersistor(Session, user_view, user_search, tenant_uuids)


def search(**parameters):
    tenant_uuids = parameters.pop('tenant_uuids', None)
    return persistor(tenant_uuids).search(parameters)


def search_collated(**parameters):
    tenant_uuids = parameters.pop('tenant_uuids', None)
    return persistor(tenant_uuids).search_collated(parameters)


def get(user_id, tenant_uuids=None):
    return persistor(tenant_uuids).get_by({'id': user_id})


def get_by(tenant_uuids=None, **criteria):
    return persistor(tenant_uuids).get_by(criteria)


def find_by_id_uuid(id, tenant_uuids=None):
    return persistor(tenant_uuids).find_by_id_uuid(id)


def get_by_id_uuid(id, tenant_uuids=None):
    return persistor(tenant_uuids).get_by_id_uuid(id)


def find_all_by_agent_id(agent_id):
    return persistor().find_all_by_agent_id(agent_id)


def find(user_id):
    return persistor().find_by({'id': user_id})


def find_by(**criteria):
    return persistor().find_by(criteria)


def find_all_by(**criteria):
    return persistor().find_all_by(criteria)


def count_all_by(column_name, **criteria):
    return persistor().count_all_by(column_name, criteria)


def create(user):
    return persistor().create(user)


def edit(user):
    persistor().edit(user)
    UserFixes(Session).fix(user.id)


def delete(user):
    persistor().delete(user)
    template_persistor = build_template_persistor(Session)
    template_persistor.delete(user.func_key_template_private)


def associate_all_groups(user, groups):
    persistor().associate_all_groups(user, groups)


def list_outgoing_callerid_associated(user_id):
    return persistor().list_outgoing_callerid_associated(user_id)


@contextmanager
def query_options(*options):
    with UserPersistor.context_query_options(*options):
        yield
