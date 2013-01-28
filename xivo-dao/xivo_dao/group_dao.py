# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
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

from xivo_dao.alchemy.groupfeatures import GroupFeatures
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.helpers.db_manager import DbSession


def get(group_id):
    return DbSession().query(GroupFeatures).filter(GroupFeatures.id == group_id).first()


def get_name(group_id):
    return get(group_id).name


def get_name_number(group_id):
    group = get(group_id)
    return group.name, group.number


def is_user_member_of_group(user_id, group_id):
    row = (DbSession()
           .query(GroupFeatures.id)
           .join((QueueMember, QueueMember.queue_name == GroupFeatures.name))
           .filter(GroupFeatures.id == group_id)
           .filter(QueueMember.usertype == 'user')
           .filter(QueueMember.userid == user_id)
           .first())
    return row is not None


def all():
    return DbSession().query(GroupFeatures).all()
