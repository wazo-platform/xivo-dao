# Copyright 2014-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import or_

from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.func_key_dest_forward import FuncKeyDestForward
from xivo_dao.alchemy.func_key_dest_user import FuncKeyDestUser
from xivo_dao.alchemy.func_key_mapping import FuncKeyMapping
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.helpers.db_manager import daosession


@daosession
def find_all_forwards(session, user_id, fwd_type):
    type_converter = _ForwardTypeConverter()

    query = (
        session.query(FuncKeyDestForward.number.label('number'))
        .join(Extension,
              FuncKeyDestForward.extension_id == Extension.id)
        .join(FuncKeyMapping,
              FuncKeyMapping.func_key_id == FuncKeyDestForward.func_key_id)
        .join(UserFeatures,
              UserFeatures.func_key_private_template_id == FuncKeyMapping.template_id)
        .filter(UserFeatures.id == user_id)
        .filter(Extension.typeval == type_converter.model_to_db(fwd_type))
    )
    return query.all()


@daosession
def find_users_having_user_destination(session, destination_user):
    query = (
        session.query(UserFeatures)
        .join(FuncKeyMapping,
              or_(FuncKeyMapping.template_id == UserFeatures.func_key_private_template_id,
                  FuncKeyMapping.template_id == UserFeatures.func_key_template_id))
        .join(FuncKeyDestUser, FuncKeyMapping.func_key_id == FuncKeyDestUser.func_key_id)
        .filter(FuncKeyDestUser.user_id == str(destination_user.id))
    )
    return query.all()


class _ForwardTypeConverter:

    fwd_types = {
        'unconditional': 'fwdunc',
        'noanswer': 'fwdrna',
        'busy': 'fwdbusy',
    }

    reversed_types = {value: key for key, value in fwd_types.items()}

    def db_to_model(self, db_type):
        return self.reversed_types[db_type]

    def model_to_db(self, model_type):
        return self.fwd_types[model_type]
