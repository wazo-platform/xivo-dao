# -*- coding: utf-8 -*-

# Copyright (C) 2012-2015 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.groupfeatures import GroupFeatures
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.helpers.db_manager import daosession


@daosession
def get(session, group_id):
    return session.query(GroupFeatures).filter(GroupFeatures.id == group_id).first()


def get_name_number(group_id):
    group = get(group_id)
    return group.name, group.number


@daosession
def is_user_member_of_group(session, user_id, group_id):
    row = (session
           .query(GroupFeatures.id)
           .join((QueueMember, QueueMember.queue_name == GroupFeatures.name))
           .filter(GroupFeatures.id == group_id)
           .filter(QueueMember.usertype == 'user')
           .filter(QueueMember.userid == user_id)
           .first())
    return row is not None


@daosession
def all(session):
    return session.query(GroupFeatures).all()
