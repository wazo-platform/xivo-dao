# -*- coding: utf-8 -*-

# Copyright (C) 2014-2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo_dao.helpers.db_manager import daosession
from xivo_dao.helpers.db_utils import flush_session

from xivo_dao.alchemy.func_key_template import FuncKeyTemplate as FuncKeyTemplateSchema
from xivo_dao.alchemy.func_key_mapping import FuncKeyMapping as FuncKeyMappingSchema

from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.resources.func_key_template.persistor import build_persistor
from xivo_dao.resources.func_key_template.search import template_search


@daosession
def search(session, **parameters):
    persistor = build_persistor(session)

    query = session.query(FuncKeyTemplateSchema.id)
    rows, total = template_search.search_from_query(query, parameters)

    items = [persistor.get(row.id) for row in rows]
    return SearchResult(total=total, items=items)


@daosession
def create(session, template):
    persistor = build_persistor(session)
    with flush_session(session):
        return persistor.create(template)


@daosession
def get(session, template_id):
    persistor = build_persistor(session)
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


@daosession
def create_private_template(session):
    template = FuncKeyTemplateSchema(private=True)

    with flush_session(session):
        session.add(template)

    return template.id


@daosession
def remove_func_key_from_templates(session, func_key):
    with flush_session(session):
        (session.query(FuncKeyMappingSchema)
         .filter(FuncKeyMappingSchema.func_key_id == func_key.id)
         .delete())


@daosession
def delete_private_template(session, template_id):
    with flush_session(session):
        (session.query(FuncKeyMappingSchema)
         .filter(FuncKeyMappingSchema.template_id == template_id)
         .delete())

        (session.query(FuncKeyTemplateSchema)
         .filter(FuncKeyTemplateSchema.id == template_id)
         .delete())
