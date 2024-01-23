# Copyright 2012-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import (
    Column,
    Index,
    ForeignKey,
    PrimaryKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.sql import func, cast, not_
from sqlalchemy.types import Integer, String, Enum, Boolean

from xivo_dao.helpers.db_manager import Base

from . import enum


class UserCustom(Base):
    __tablename__ = 'usercustom'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('interface', 'intfsuffix', 'category'),
        Index('usercustom__idx__category', 'category'),
        Index('usercustom__idx__context', 'context'),
        Index('usercustom__idx__name', 'name'),
        Index('usercustom__idx__tenant_uuid', 'tenant_uuid'),
    )

    id = Column(Integer, nullable=False)
    tenant_uuid = Column(
        String(36),
        ForeignKey('tenant.uuid', ondelete='CASCADE'),
        nullable=False,
    )
    name = Column(String(40))
    context = Column(String(79))
    interface = Column(String(128), nullable=False)
    intfsuffix = Column(String(32), nullable=False, server_default='')
    commented = Column(Integer, nullable=False, server_default='0')
    protocol = Column(enum.trunk_protocol, nullable=False, server_default='custom')
    category = Column(
        Enum('user', 'trunk', name='usercustom_category', metadata=Base.metadata),
        nullable=False,
    )

    line = relationship('LineFeatures', uselist=False, viewonly=True)
    trunk = relationship('TrunkFeatures', uselist=False, viewonly=True)

    @hybrid_property
    def enabled(self):
        return not bool(self.commented)

    @enabled.expression
    def enabled(cls):
        return not_(cast(cls.commented, Boolean))

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

    @hybrid_property
    def interface_suffix(self):
        if self.intfsuffix == '':
            return None
        return self.intfsuffix

    @interface_suffix.expression
    def interface_suffix(cls):
        return func.nullif(cls.intfsuffix, '')

    @interface_suffix.setter
    def interface_suffix(self, value):
        if value is None:
            self.intfsuffix = ''
        else:
            self.intfsuffix = value
