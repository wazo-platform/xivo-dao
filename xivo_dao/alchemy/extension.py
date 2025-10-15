# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.orm.attributes import get_history
from sqlalchemy.schema import (
    Column,
    ForeignKeyConstraint,
    Index,
    PrimaryKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.sql import cast, func, not_, select
from sqlalchemy.types import Boolean, Integer, String

from xivo_dao.alchemy import enum
from xivo_dao.alchemy.context import Context
from xivo_dao.helpers.db_manager import Base, IntAsString


class Extension(Base):
    __tablename__ = 'extensions'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('exten', 'context'),
        Index('extensions__idx__context', 'context'),
        Index('extensions__idx__exten', 'exten'),
        Index('extensions__idx__type', 'type'),
        Index('extensions__idx__typeval', 'typeval'),
        ForeignKeyConstraint(
            ('context',),
            ('context.name',),
            ondelete='CASCADE',
        ),
    )

    id = Column(Integer)
    commented = Column(Integer, nullable=False, server_default='0')
    context = Column(String(79), nullable=False, server_default='')
    exten = Column(String(40), nullable=False, server_default='')
    type = Column(enum.extenumbers_type, nullable=False)
    typeval = Column(IntAsString(255), nullable=False, server_default='')

    context_rel = relationship(
        'Context',
        primaryjoin='''Extension.context == Context.name''',
        foreign_keys='Extension.context',
    )

    def get_old_context(self):
        context_history = get_history(self, 'context')
        if context_history[2]:
            return context_history[2][0]
        return self.context

    @hybrid_property
    def tenant_uuid(self):
        if self.context_rel:
            return self.context_rel.tenant_uuid

        return None

    @tenant_uuid.expression
    def tenant_uuid(cls):
        return func.coalesce(
            select(Context.tenant_uuid)
            .where(Context.name == cls.context)
            .label('type'),
            None,
        )

    @hybrid_property
    def context_type(self):
        if self.context_ref:
            return self.context_rel.type

    @context_type.expression
    def context_type(cls):
        return func.coalesce(
            select(Context.contexttype)
            .where(Context.name == cls.context)
            .label('type'),
            'internal',
        )

    dialpattern = relationship(
        'DialPattern',
        primaryjoin="""and_(
            Extension.type == 'outcall',
            Extension.typeval == cast(DialPattern.id, String)
        )""",
        foreign_keys='Extension.typeval',
        viewonly=True,
    )

    outcall = association_proxy('dialpattern', 'outcall')

    line_extensions = relationship('LineExtension', viewonly=True)

    lines = association_proxy('line_extensions', 'line')

    group = relationship(
        'GroupFeatures',
        primaryjoin="""and_(
            Extension.type == 'group',
            Extension.typeval == cast(GroupFeatures.id, String)
        )""",
        foreign_keys='Extension.typeval',
        viewonly=True,
    )

    queue = relationship(
        'QueueFeatures',
        primaryjoin="""and_(
            Extension.type == 'queue',
            Extension.typeval == cast(QueueFeatures.id, String)
        )""",
        foreign_keys='Extension.typeval',
        viewonly=True,
    )

    incall = relationship(
        'Incall',
        primaryjoin="""and_(
            Extension.type == 'incall',
            Extension.typeval == cast(Incall.id, String)
        )""",
        foreign_keys='Extension.typeval',
        viewonly=True,
    )

    conference = relationship(
        'Conference',
        primaryjoin="""and_(
            Extension.type == 'conference',
            Extension.typeval == cast(Conference.id, String)
        )""",
        foreign_keys='Extension.typeval',
        viewonly=True,
    )

    parking_lot = relationship(
        'ParkingLot',
        primaryjoin="""and_(
            Extension.type == 'parking',
            Extension.typeval == cast(ParkingLot.id, String)
        )""",
        foreign_keys='Extension.typeval',
        viewonly=True,
    )

    @property
    def name(self):
        return self.typeval

    @hybrid_property
    def legacy_commented(self):
        return bool(self.commented)

    @legacy_commented.expression
    def legacy_commented(cls):
        return cast(cls.commented, Boolean)

    @legacy_commented.setter
    def legacy_commented(self, value):
        if value is not None:
            value = int(value)
        self.commented = value

    @hybrid_property
    def enabled(self):
        return self.commented == 0

    @enabled.expression
    def enabled(cls):
        return not_(cast(cls.commented, Boolean))

    @enabled.setter
    def enabled(self, value):
        self.commented = int(value is False)

    def is_pattern(self):
        return self.exten.startswith('_')
