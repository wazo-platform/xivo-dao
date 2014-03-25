# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
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

from sqlalchemy.schema import Column
from sqlalchemy.types import String

from xivo_dao.helpers.db_manager import Base


class QueueLog(Base):

    __tablename__ = 'queue_log'

    time = Column(String(26), server_default='', primary_key=True)
    callid = Column(String(32), server_default='', primary_key=True)
    queuename = Column(String(50), nullable=False, server_default='')
    agent = Column(String(50), nullable=False, server_default='')
    event = Column(String(20), nullable=False, server_default='')
    data1 = Column(String(30), server_default='')
    data2 = Column(String(30), server_default='')
    data3 = Column(String(30), server_default='')
    data4 = Column(String(30), server_default='')
    data5 = Column(String(30), server_default='')
