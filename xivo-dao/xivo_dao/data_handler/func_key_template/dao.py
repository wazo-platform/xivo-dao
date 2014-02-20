# -*- coding: utf-8 -*-

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

from xivo_dao.helpers.db_manager import daosession
from xivo_dao.helpers.db_utils import commit_or_abort
from xivo_dao.alchemy.func_key_template import FuncKeyTemplate
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema
from xivo_dao.data_handler.exception import ElementCreationError


@daosession
def create_private_template_for_user(session, user):
    template = FuncKeyTemplate(private=True,
                               name=user.fullname)

    with commit_or_abort(session, ElementCreationError, 'FuncKeyTemplate'):
        session.add(template)

    with commit_or_abort(session, ElementCreationError, 'FuncKeyTemplate'):
        (session
         .query(UserSchema)
         .filter(UserSchema.id == user.id)
         .update({'func_key_private_template_id': template.id}))
