# -*- coding: utf-8 -*-

# Copyright (C) 2012-2015 Avencall
# Copyright (C) 2016 Proformatique Inc.
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
from sqlalchemy.sql import cast, not_

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
    password = Column(String(80))
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
    def timezone(self):
        return self.tz

    @timezone.setter
    def timezone(self, value):
        self.tz = value

    @hybrid_property
    def max_messages(self):
        return self.maxmsg

    @max_messages.setter
    def max_messages(self, value):
        self.maxmsg = value

    @hybrid_property
    def attach_audio(self):
        if self.attach is None:
            return None
        return bool(self.attach)

    @attach_audio.setter
    def attach_audio(self, value):
        self.attach = int(value) if value is not None else None

    @hybrid_property
    def delete_messages(self):
        return bool(self.deletevoicemail)

    @delete_messages.setter
    def delete_messages(self, value):
        self.deletevoicemail = int(value)

    @hybrid_property
    def ask_password(self):
        return not bool(self.skipcheckpass)

    @ask_password.expression
    def ask_password(cls):
        return sql.not_(sql.cast(cls.skipcheckpass, Boolean))

    @ask_password.setter
    def ask_password(self, value):
        self.skipcheckpass = int(not value)

    @hybrid_property
    def enabled(self):
        if self.commented is None:
            return None
        return self.commented == 0

    @enabled.expression
    def enabled(cls):
        return not_(cast(cls.commented, Boolean))

    @enabled.setter
    def enabled(self, value):
        self.commented = int(value == 0) if value is not None else None
