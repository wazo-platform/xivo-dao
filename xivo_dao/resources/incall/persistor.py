# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.incall import Incall

from xivo_dao.resources.utils.search import CriteriaBuilderMixin
from xivo_dao.helpers.db_utils import flush_session

from xivo_dao.resources.extension import dao as extension_dao
from xivo_dao.resources.incall.model import db_converter as incall_db_converter


class IncallPersistor(CriteriaBuilderMixin):

    _search_table = Incall

    def __init__(self, session):
        self.session = session

    def create(self, incall):
        extension = extension_dao.get(incall.extension_id)

        with flush_session(self.session):
            incall.id = self._create_incall(incall, extension)
            self._update_extension(incall)
            self._create_dialaction(incall)

        return incall

    def _create_incall(self, incall, extension):
        incall_row = incall_db_converter.to_incall(incall, extension)
        self.session.add(incall_row)
        self.session.flush()
        return incall_row.id

    def _update_extension(self, incall):
        (self.session.query(Extension)
         .filter(Extension.id == incall.extension_id)
         .update({'type': 'incall', 'typeval': str(incall.id)})
         )

    def _create_dialaction(self, incall):
        dialaction_row = incall_db_converter.to_dialaction(incall)
        self.session.add(dialaction_row)

    def delete(self, incall):
        incall_query = (self.session.query(Incall)
                        .filter(Incall.id == incall.id))

        dialaction_query = (self.session.query(Dialaction)
                            .filter(Dialaction.category == 'incall')
                            .filter(Dialaction.categoryval == str(incall.id)))

        extension_query = (self.session.query(Extension)
                           .filter(Extension.id == incall.extension_id))

        incall_query.delete()
        dialaction_query.delete()
        extension_query.update({'type': 'user', 'typeval': '0'})
        self.session.flush()
