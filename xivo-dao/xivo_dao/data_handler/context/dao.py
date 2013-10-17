# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from xivo_dao.alchemy.contextnumbers import ContextNumbers as ContextNumberSchema
from xivo_dao.alchemy.entity import Entity as EntitySchema
from xivo_dao.data_handler.context.model import db_converter
from xivo_dao.helpers.db_manager import daosession, xivo_daosession


@daosession
def create(session, context):
    context_row = db_converter.to_source(context)
    context_row.entity = _get_default_entity_name()

    session.begin()
    session.add(context_row)
    session.commit()


@xivo_daosession
def _get_default_entity_name(session):
    entity = session.query(EntitySchema).first()
    return entity.name


@daosession
def context_ranges(session, context_name, context_type):
    rows = (session.query(
        ContextNumberSchema.numberbeg,
        ContextNumberSchema.numberend)
        .filter(ContextNumberSchema.context == context_name)
        .filter(ContextNumberSchema.type == context_type)
        .all())

    ranges = []

    for row in rows:
        minimum, maximum = _convert_minimum_maximum(row)
        ranges.append((minimum, maximum))

    return ranges


def _convert_minimum_maximum(row):
    minimum = int(row.numberbeg)
    if row.numberend:
        maximum = int(row.numberend)
    else:
        maximum = None

    return minimum, maximum
