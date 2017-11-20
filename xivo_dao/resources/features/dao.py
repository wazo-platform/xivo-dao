# -*- coding: UTF-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.features import Features

from xivo_dao.helpers import errors
from xivo_dao.helpers.db_manager import daosession

from xivo_dao.resources.features.database import transfer_converter


@daosession
def find_all_transfer_extensions(session):
    query = (session.query(Features.id,
                           Features.var_name,
                           Features.var_val)
             .filter(Features.commented == 0)
             .filter(Features.var_name.in_(transfer_converter.var_names()))
             )

    return [transfer_converter.to_model(row) for row in query]


@daosession
def find_park_position_range(session):
    query = (session.query(Features.var_val)
             .filter(Features.commented == 0)
             .filter(Features.var_name == 'parkpos')
             )

    raw_range = query.scalar()
    if not raw_range:
        return None

    return tuple(int(x) for x in raw_range.split("-"))


@daosession
def get_value(session, feature_id):
    value = (session.query(Features.var_val)
             .filter(Features.id == feature_id)
             .scalar())

    if not value:
        raise errors.not_found('Features', id=feature_id)

    return value
