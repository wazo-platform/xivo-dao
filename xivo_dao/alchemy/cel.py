# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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
from sqlalchemy.types import DateTime, Integer, String

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
        Index('cel__idx__uniqueid', 'uniqueid'),
    )

    id = Column(Integer, primary_key=True, nullable=False)
    eventtype = Column(String(30), nullable=False)
    eventtime = Column(DateTime, nullable=False)
    userdeftype = Column(String(255), nullable=False)
    cid_name = Column(String(80, convert_unicode=True), nullable=False)
    cid_num = Column(String(80, convert_unicode=True), nullable=False)
    cid_ani = Column(String(80), nullable=False)
    cid_rdnis = Column(String(80), nullable=False)
    cid_dnid = Column(String(80), nullable=False)
    exten = Column(String(80, convert_unicode=True), nullable=False)
    context = Column(String(80), nullable=False)
    channame = Column(String(80, convert_unicode=True), nullable=False)
    appname = Column(String(80), nullable=False)
    appdata = Column(String(512), nullable=False)
    amaflags = Column(Integer, nullable=False)
    accountcode = Column(String(20), nullable=False)
    peeraccount = Column(String(20), nullable=False)
    uniqueid = Column(String(150), nullable=False)
    linkedid = Column(String(150), nullable=False)
    userfield = Column(String(255), nullable=False)
    peer = Column(String(80), nullable=False)
    call_log_id = Column(Integer)

    call_log = relationship('CallLog')
