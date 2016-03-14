# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
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

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, Index, ForeignKeyConstraint
from sqlalchemy.types import DateTime, Integer, Text, UnicodeText

from xivo_dao.alchemy.call_log import CallLog
from xivo_dao.helpers.db_manager import Base


class CEL(Base):

    __tablename__ = 'cel'
    __table_args__ = (
        ForeignKeyConstraint(('call_log_id',),
                             ('call_log.id',),
                             ondelete='SET NULL'),
        Index('cel__idx__call_log_id', 'call_log_id'),
        Index('cel__idx__eventtime', 'eventtime'),
        Index('cel__idx__linkedid', 'linkedid'),
    )

    id = Column(Integer, primary_key=True, nullable=False)
    eventtype = Column(Text, nullable=False)
    eventtime = Column(DateTime, nullable=False)
    userdeftype = Column(Text, nullable=False)
    cid_name = Column(UnicodeText, nullable=False)
    cid_num = Column(UnicodeText, nullable=False)
    cid_ani = Column(Text, nullable=False)
    cid_rdnis = Column(Text, nullable=False)
    cid_dnid = Column(Text, nullable=False)
    exten = Column(UnicodeText, nullable=False)
    context = Column(Text, nullable=False)
    channame = Column(UnicodeText, nullable=False)
    appname = Column(Text, nullable=False)
    appdata = Column(Text, nullable=False)
    amaflags = Column(Integer, nullable=False)
    accountcode = Column(Text, nullable=False)
    peeraccount = Column(Text, nullable=False)
    uniqueid = Column(Text, nullable=False)
    linkedid = Column(Text, nullable=False)
    userfield = Column(Text, nullable=False)
    peer = Column(Text, nullable=False)
    call_log_id = Column(Integer)

    call_log = relationship(CallLog)
