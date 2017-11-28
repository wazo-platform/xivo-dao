# -*- coding: utf-8 -*-
# Copyright 2012-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy import sql
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint, \
    Index
from sqlalchemy.types import Integer, String, Enum, Boolean
from sqlalchemy.ext.hybrid import hybrid_property

from xivo_dao.helpers.db_manager import Base
from xivo_dao.alchemy import enum


class UserCustom(Base):

    __tablename__ = 'usercustom'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('interface', 'intfsuffix', 'category'),
        Index('usercustom__idx__category', 'category'),
        Index('usercustom__idx__context', 'context'),
        Index('usercustom__idx__name', 'name'),
    )

    id = Column(Integer, nullable=False)
    name = Column(String(40))
    context = Column(String(39))
    interface = Column(String(128), nullable=False)
    intfsuffix = Column(String(32), nullable=False, server_default='')
    commented = Column(Integer, nullable=False, server_default='0')
    protocol = Column(enum.trunk_protocol, nullable=False, server_default='custom')
    category = Column(Enum('user', 'trunk',
                           name='usercustom_category',
                           metadata=Base.metadata),
                      nullable=False)

    line = relationship('LineFeatures',
                        primaryjoin="""and_(
                            LineFeatures.protocol == 'custom',
                            LineFeatures.protocolid == UserCustom.id
                        )""",
                        foreign_keys='LineFeatures.protocolid',
                        uselist=False,
                        back_populates='endpoint_custom')

    trunk = relationship('TrunkFeatures',
                         primaryjoin="""and_(
                             TrunkFeatures.protocol == 'custom',
                             TrunkFeatures.protocolid == UserCustom.id
                         )""",
                         uselist=False,
                         foreign_keys='TrunkFeatures.protocolid',
                         back_populates='endpoint_custom')

    @hybrid_property
    def enabled(self):
        return not bool(self.commented)

    @enabled.expression
    def enabled(cls):
        return sql.not_(sql.cast(cls.commented, Boolean))

    @enabled.setter
    def enabled(self, value):
        if value is None:
            self.commented = None
        else:
            self.commented = int(value is False)

    def endpoint_protocol(self):
        return 'custom'

    def same_protocol(self, protocol, protocolid):
        return protocol == 'custom' and self.id == int(protocolid)
