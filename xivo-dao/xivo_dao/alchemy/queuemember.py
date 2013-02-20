# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

# vim: set fileencoding=utf-8 :
# XiVO CTI Server

# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from xivo_dao.helpers.db_manager import Base, Type
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, Enum


class QueueMember(Base):
    __tablename__ = 'queuemember'

    queue_name = Column(String(128), primary_key=True)
    interface = Column(String(128), primary_key=True)
    penalty = Column(Integer, nullable=False, server_default='0')
    call_limit = Column('call-limit', Integer, nullable=False, server_default='0')
    paused = Column(Integer)
    commented = Column(Integer, nullable=False, server_default='0')
    usertype = Column(Enum('user', 'agent', name='queuemember_usertype', metadata=Type.metadata), nullable=False)
    userid = Column(Integer, nullable=False)
    channel = Column(String(25), nullable=False)
    category = Column(Enum('queue', 'group', name='queue_category', metadata=Type.metadata), nullable=False)
    skills = Column(String(64), nullable=False, server_default='')
    state_interface = Column(String(128), nullable=False, server_default='')
    position = Column(Integer, nullable=False, server_default='0')
