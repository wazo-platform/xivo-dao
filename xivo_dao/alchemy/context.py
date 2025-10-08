# Copyright 2012-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship
from sqlalchemy.schema import (
    Column,
    ForeignKeyConstraint,
    Index,
    PrimaryKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.sql import cast, not_, text
from sqlalchemy.types import Boolean, Integer, String, Text

from xivo_dao.alchemy.contextnumbers import ContextNumbers
from xivo_dao.helpers.db_manager import Base

from .contextinclude import ContextInclude


class Context(Base):
    __tablename__ = 'context'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'),
        UniqueConstraint('uuid'),
        ForeignKeyConstraint(
            ('tenant_uuid',),
            ('tenant.uuid',),
            ondelete='CASCADE',
        ),
        Index('context__idx__tenant_uuid', 'tenant_uuid'),
    )

    id = Column(Integer)
    uuid = Column(UUID(as_uuid=True), server_default=text('uuid_generate_v4()'))
    tenant_uuid = Column(String(36), nullable=False)
    name = Column(String(79), nullable=False)
    displayname = Column(String(128))
    contexttype = Column(String(40), nullable=False, server_default='internal')
    commented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text)

    context_numbers_user = relationship(
        ContextNumbers,
        primaryjoin="""and_(
            ContextNumbers.type == 'user',
            ContextNumbers.context == Context.name)""",
        foreign_keys='ContextNumbers.context',
        cascade='all, delete-orphan',
        overlaps=(
            'context_numbers_group,'
            'context_numbers_queue,'
            'context_numbers_meetme,'
            'context_numbers_incall,'
        ),
    )

    context_numbers_group = relationship(
        ContextNumbers,
        primaryjoin="""and_(
            ContextNumbers.type == 'group',
            ContextNumbers.context == Context.name)""",
        foreign_keys='ContextNumbers.context',
        cascade='all, delete-orphan',
        overlaps=(
            'context_numbers_user,'
            'context_numbers_queue,'
            'context_numbers_meetme,'
            'context_numbers_incall,'
        ),
    )

    context_numbers_queue = relationship(
        ContextNumbers,
        primaryjoin="""and_(
            ContextNumbers.type == 'queue',
            ContextNumbers.context == Context.name)""",
        foreign_keys='ContextNumbers.context',
        cascade='all, delete-orphan',
        overlaps=(
            'context_numbers_user,'
            'context_numbers_group,'
            'context_numbers_meetme,'
            'context_numbers_incall,'
        ),
    )

    context_numbers_meetme = relationship(
        ContextNumbers,
        primaryjoin="""and_(
            ContextNumbers.type == 'meetme',
            ContextNumbers.context == Context.name)""",
        foreign_keys='ContextNumbers.context',
        cascade='all, delete-orphan',
        overlaps=(
            'context_numbers_user,'
            'context_numbers_group,'
            'context_numbers_queue,'
            'context_numbers_incall,'
        ),
    )

    context_numbers_incall = relationship(
        ContextNumbers,
        primaryjoin="""and_(
            ContextNumbers.type == 'incall',
            ContextNumbers.context == Context.name)""",
        foreign_keys='ContextNumbers.context',
        cascade='all, delete-orphan',
        overlaps=(
            'context_numbers_user,'
            'context_numbers_group,'
            'context_numbers_queue,'
            'context_numbers_meetme,'
        ),
    )

    context_includes_children = relationship(
        'ContextInclude',
        primaryjoin='ContextInclude.include == Context.name',
        foreign_keys='ContextInclude.include',
        cascade='all, delete-orphan',
        back_populates='included_context',
    )

    context_include_parents = relationship(
        'ContextInclude',
        primaryjoin='ContextInclude.context == Context.name',
        foreign_keys='ContextInclude.context',
        order_by='ContextInclude.priority',
        collection_class=ordering_list('priority', reorder_on_append=True),
        cascade='all, delete-orphan',
    )

    contexts = association_proxy(
        'context_include_parents',
        'included_context',
        creator=lambda _context: ContextInclude(included_context=_context),
    )

    tenant = relationship('Tenant', viewonly=True)

    @hybrid_property
    def label(self):
        return self.displayname

    @label.setter
    def label(self, value):
        self.displayname = value

    @hybrid_property
    def type(self):
        return self.contexttype

    @type.setter
    def type(self, value):
        self.contexttype = value

    @hybrid_property
    def enabled(self):
        return self.commented == 0

    @enabled.expression
    def enabled(cls):
        return not_(cast(cls.commented, Boolean))

    @enabled.setter
    def enabled(self, value):
        self.commented = int(value is False)

    @hybrid_property
    def user_ranges(self):
        return self.context_numbers_user

    @user_ranges.setter
    def user_ranges(self, user_ranges):
        for user_range in user_ranges:
            user_range.type = 'user'
        self.context_numbers_user = user_ranges

    @hybrid_property
    def group_ranges(self):
        return self.context_numbers_group

    @group_ranges.setter
    def group_ranges(self, group_ranges):
        for group_range in group_ranges:
            group_range.type = 'group'
        self.context_numbers_group = group_ranges

    @hybrid_property
    def queue_ranges(self):
        return self.context_numbers_queue

    @queue_ranges.setter
    def queue_ranges(self, queue_ranges):
        for queue_range in queue_ranges:
            queue_range.type = 'queue'
        self.context_numbers_queue = queue_ranges

    @hybrid_property
    def conference_room_ranges(self):
        return self.context_numbers_meetme

    @conference_room_ranges.setter
    def conference_room_ranges(self, conference_room_ranges):
        for conference_room_range in conference_room_ranges:
            conference_room_range.type = 'meetme'
        self.context_numbers_meetme = conference_room_ranges

    @hybrid_property
    def incall_ranges(self):
        return self.context_numbers_incall

    @incall_ranges.setter
    def incall_ranges(self, incall_ranges):
        for incall_range in incall_ranges:
            incall_range.type = 'incall'
        self.context_numbers_incall = incall_ranges
