# Copyright 2012-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.helpers.db_manager import daosession


@daosession
def get(session, queue_id, tenant_uuids=None):
    query = session.query(QueueFeatures).filter(QueueFeatures.id == queue_id)

    if tenant_uuids is not None:
        query = query.filter(QueueFeatures.tenant_uuid.in_(tenant_uuids))

    result = query.first()
    if result is None:
        raise LookupError('No such queue')
    else:
        return result
