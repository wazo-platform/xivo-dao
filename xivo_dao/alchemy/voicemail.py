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

from sqlalchemy import sql, Boolean

from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint, \
    Index
from sqlalchemy.types import Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.hybrid import hybrid_property

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
    commented = Column(Integer, nullable=False, server_default='0')

    @hybrid_property
    def id(self):
        return self.uniqueid

    @id.setter
    def id(self, value):
        self.uniqueid = value

    @hybrid_property
    def name(self):
        return self.fullname

    @name.setter
    def name(self, value):
        self.fullname = value

    @hybrid_property
    def number(self):
        return self.mailbox

    @number.setter
    def number(self, value):
        self.mailbox = value

    @hybrid_property
    def ask_password(self):
        return not bool(self.skipcheckpass)

    @ask_password.expression
    def ask_password(cls):
        return sql.not_(sql.cast(cls.skipcheckpass, Boolean))

    @ask_password.setter
    def ask_password(self, value):
        self.skipcheckpass = int(not value)
