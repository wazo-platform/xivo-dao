# -*- coding: UTF-8 -*-
# Copyright (C) 2015 Avencall
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.helpers.db_manager import daosession


@daosession
def exists(session, queue_id):
    query = (session.query(QueueFeatures)
             .filter(QueueFeatures.id == queue_id)
             )

    return query.count() > 0


@daosession
def find_by(session, name):
    query = (session.query(QueueFeatures)
             .filter_by(name=name)
             )

    return query.first()
