# -*- coding: utf-8 -*-
# Copyright 2012-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy import sql, Boolean

from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.orm.attributes import get_history
from sqlalchemy.schema import (Column,
                               Index,
                               PrimaryKeyConstraint,
                               UniqueConstraint)
from sqlalchemy.sql import cast, not_
from sqlalchemy.types import Integer, String

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

    users = relationship('UserFeatures',
                         back_populates='voicemail')

    ivr_dialactions = relationship('Dialaction',
                                   primaryjoin="""and_(Dialaction.action == 'voicemail',
                                                       Dialaction.actionarg1 == cast(Voicemail.id, String),
                                                       Dialaction.category.in_(['ivr', 'ivr_choice']))""",
                                   foreign_keys='Dialaction.actionarg1',
                                   cascade='all, delete-orphan')

    def get_old_number_context(self):
        number_history = get_history(self, 'mailbox')
        context_history = get_history(self, 'context')

        old_number = self.number
        if number_history[2]:
            old_number = number_history[2][0]

        old_context = self.context
        if context_history[2]:
            old_context = context_history[2][0]

        return old_number, old_context

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
        self.commented = int(value is False) if value is not None else None
