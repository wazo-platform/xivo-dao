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

from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.func_key_dest_forward import FuncKeyDestForward
from xivo_dao.alchemy.func_key_mapping import FuncKeyMapping
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.resources.func_key.model import Forward, ForwardTypeConverter


@daosession
def find_all_forwards(session, user_id, fwd_type):
    type_converter = ForwardTypeConverter()

    query = (session.query(FuncKeyDestForward.number.label('number'),
                           UserFeatures.id.label('user_id'),
                           Extension.typeval.label('type'))
             .join(Extension,
                   FuncKeyDestForward.extension_id == Extension.id)
             .join(FuncKeyMapping,
                   FuncKeyMapping.func_key_id == FuncKeyDestForward.func_key_id)
             .join(UserFeatures,
                   UserFeatures.func_key_private_template_id == FuncKeyMapping.template_id)
             .filter(UserFeatures.id == user_id)
             .filter(Extension.typeval == type_converter.model_to_db(fwd_type))
             )

    return [Forward(user_id=row.user_id,
                    type=type_converter.db_to_model(row.type),
                    number=row.number)
            for row in query]
