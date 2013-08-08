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

from xivo_dao.alchemy.context import Context as ContextSchema
from xivo_dao.alchemy.entity import Entity as EntitySchema
from xivo_dao.helpers.db_manager import daosession, xivo_daosession


@daosession
def create(session, context):
    context_row = context.to_data_source(ContextSchema)
    context_row.entity = _get_default_entity_name()
    context_row.commented = 0
    context_row.description = getattr(context, 'description', '')

    session.begin()
    session.add(context_row)
    session.commit()


@xivo_daosession
def _get_default_entity_name(session):
    entity = session.query(EntitySchema).first()
    return entity.name
