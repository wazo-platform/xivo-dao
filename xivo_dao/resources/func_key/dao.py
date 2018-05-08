# -*- coding: utf-8 -*-
# Copyright 2014-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import six

from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.func_key_dest_forward import FuncKeyDestForward
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


class _ForwardTypeConverter(object):

    fwd_types = {
        'unconditional': 'fwdunc',
        'noanswer': 'fwdrna',
        'busy': 'fwdbusy',
    }

    reversed_types = dict((value, key) for key, value in six.iteritems(fwd_types))

    def db_to_model(self, db_type):
        return self.reversed_types[db_type]

    def model_to_db(self, model_type):
        return self.fwd_types[model_type]
