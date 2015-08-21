# -*- coding: utf-8 -*-

# Copyright (C) 2012-2015 Avencall
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

from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint, \
    Index
from sqlalchemy.types import Integer, String
from sqlalchemy.dialects.postgresql import ARRAY

from xivo_dao.helpers.db_manager import Base


class Voicemail(Base):

    __tablename__ = 'voicemail'
    __table_args__ = (
        PrimaryKeyConstraint('uniqueid'),
        UniqueConstraint('mailbox', 'context'),
        Index('voicemail__idx__context', 'context'),
    )

    uniqueid = Column(Integer)
    context = Column(String(39), nullable=False)
    mailbox = Column(String(40), nullable=False)
    password = Column(String(80), nullable=False, server_default='')
    fullname = Column(String(80), nullable=False, server_default='')
    email = Column(String(80))
    pager = Column(String(80))
    language = Column(String(20))
    tz = Column(String(80))
    attach = Column(Integer)
    deletevoicemail = Column(Integer, nullable=False, server_default='0')
    maxmsg = Column(Integer)
    skipcheckpass = Column(Integer, nullable=False, server_default='0')
    options = Column(ARRAY(String, dimensions=2),
                     nullable=False, server_default='{}')
