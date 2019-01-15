# -*- coding: utf-8 -*-
# Copyright 2014-2016 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from xivo_dao.alchemy.infos import Infos
from xivo_dao.helpers import errors
from xivo_dao.helpers.db_manager import daosession


@daosession
def get(session):
    row = (session.query(Infos).first())

    if not row:
        raise errors.not_found('Infos')
    return row
