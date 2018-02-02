# -*- coding: utf-8 -*-
# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy import text
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.sql import cast, not_
from sqlalchemy.sql.schema import ForeignKeyConstraint
from sqlalchemy.types import Boolean, Integer, String, Text

from xivo_dao.alchemy import enum
from xivo_dao.alchemy.callerid import Callerid
from xivo_dao.alchemy.entity import Entity
from xivo_dao.helpers.db_manager import Base


class Callfilter(Base):

    __tablename__ = 'callfilter'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        ForeignKeyConstraint(('entity_id',),
                             ('entity.id',),
                             ondelete='RESTRICT'),
        UniqueConstraint('name'),
    )

    id = Column(Integer, nullable=False)
    entity_id = Column(Integer, server_default=text('NULL'))
    name = Column(String(128), nullable=False, server_default='')
    type = Column(enum.callfilter_type, nullable=False)
    bosssecretary = Column(enum.callfilter_bosssecretary)
    callfrom = Column(enum.callfilter_callfrom)
    ringseconds = Column(Integer, nullable=False, server_default='0')
    commented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text)

    entity = relationship(Entity)

    caller_id = relationship('Callerid',
                             primaryjoin="""and_(Callerid.type == 'callfilter',
                                                 Callerid.typeval == Callfilter.id)""",
                             foreign_keys='Callerid.typeval',
                             cascade='all, delete-orphan',
                             uselist=False)

    caller_id_mode = association_proxy('caller_id', 'mode',
                                       creator=lambda _mode: Callerid(type='callfilter',
                                                                      mode=_mode))
    caller_id_name = association_proxy('caller_id', 'name',
                                       creator=lambda _name: Callerid(type='callfilter',
                                                                      name=_name))

    @hybrid_property
    def strategy(self):
        if self.bosssecretary == 'bossfirst-serial':
            return 'all-recipients-then-linear-surrogates'
        elif self.bosssecretary == 'bossfirst-simult':
            return 'all-recipients-then-all-surrogates'
        elif self.bosssecretary == 'secretary-serial':
            return 'linear-surrogates-then-all-recipients'
        elif self.bosssecretary == 'secretary-simult':
            return 'all-surrogates-then-all-recipients'
        else:
            return self.bosssecretary

    @strategy.setter
    def strategy(self, value):
        if value == 'all-recipients-then-linear-surrogates':
            self.bosssecretary = 'bossfirst-serial'
        elif value == 'all-recipients-then-all-surrogates':
            self.bosssecretary = 'bossfirst-simult'
        elif value == 'linear-surrogates-then-all-recipients':
            self.bosssecretary = 'secretary-serial'
        elif value == 'all-surrogates-then-all-recipients':
            self.bosssecretary = 'secretary-simult'
        else:
            self.bosssecretary = value

    @hybrid_property
    def surrogates_timeout(self):
        if self.ringseconds == 0:
            return None
        return self.ringseconds

    @surrogates_timeout.setter
    def surrogates_timeout(self, value):
        if value is None:
            self.ringseconds = 0
        else:
            self.ringseconds = value

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
        self.commented = int(value is False)
