# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Avencall
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


from xivo_dao.data_handler import errors
from xivo_dao.data_handler.infos.model import db_converter
from xivo_dao.helpers.db_manager import daosession

from .model import Infos as InfosSchema


@daosession
def get(session):
    row = (session.query(InfosSchema).first())

    if not row:
        raise errors.not_found('Infos')
    return db_converter.to_model(row)
