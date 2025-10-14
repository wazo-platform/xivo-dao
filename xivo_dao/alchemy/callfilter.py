# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import column_property, relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.schema import (
    Column,
    ForeignKey,
    Index,
    PrimaryKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.sql import and_, cast, not_, select
from sqlalchemy.sql.expression import true
from sqlalchemy.types import Boolean, Integer, String, Text

from xivo_dao.alchemy.feature_extension import FeatureExtension
from xivo_dao.helpers.db_manager import Base

from . import enum
from .callerid import Callerid


class Callfilter(Base):
    __tablename__ = 'callfilter'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'),
        Index('callfilter__idx__tenant_uuid', 'tenant_uuid'),
    )

    id = Column(Integer, nullable=False)
    tenant_uuid = Column(
        String(36),
        ForeignKey('tenant.uuid', ondelete='CASCADE'),
        nullable=False,
    )
    name = Column(String(128), nullable=False, server_default='')
    type = Column(enum.callfilter_type, nullable=False)
    bosssecretary = Column(enum.callfilter_bosssecretary)
    callfrom = Column(enum.callfilter_callfrom)
    ringseconds = Column(Integer, nullable=False, server_default='0')
    commented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text)

    exten = column_property(
        select(FeatureExtension.exten)
        .where(
            and_(
                FeatureExtension.feature == 'bsfilter',
                FeatureExtension.enabled == true(),
            )
        )
        .correlate_except(FeatureExtension)
        .scalar_subquery()
    )

    callfilter_dialactions = relationship(
        'Dialaction',
        primaryjoin="""and_(
            Dialaction.category == 'callfilter',
            Dialaction.categoryval == cast(Callfilter.id, String
        ))""",
        cascade='all, delete-orphan',
        collection_class=attribute_mapped_collection('event'),
        foreign_keys='Dialaction.categoryval',
        overlaps=(
            'callfilter_dialactions,'
            'dialaction,'
            'dialactions,'
            'group_dialactions,'
            'queue_dialactions,'
            'switchboard_dialactions,'
            'user_dialactions,'
        ),
    )

    caller_id = relationship(
        'Callerid',
        primaryjoin="""and_(
            Callerid.type == 'callfilter',
            Callerid.typeval == Callfilter.id
        )""",
        foreign_keys='Callerid.typeval',
        cascade='all, delete-orphan',
        uselist=False,
        overlaps='caller_id',
    )

    caller_id_mode = association_proxy(
        'caller_id',
        'mode',
        creator=lambda _mode: Callerid(type='callfilter', mode=_mode),
    )
    caller_id_name = association_proxy(
        'caller_id',
        'name',
        creator=lambda _name: Callerid(type='callfilter', name=_name),
    )

    recipients = relationship(
        'Callfiltermember',
        primaryjoin="""and_(
            Callfiltermember.bstype == 'boss',
            Callfiltermember.callfilterid == Callfilter.id
        )""",
        foreign_keys='Callfiltermember.callfilterid',
        order_by='Callfiltermember.priority',
        collection_class=ordering_list('priority', reorder_on_append=True),
        cascade='all, delete-orphan',
        overlaps='surrogates',
    )

    surrogates = relationship(
        'Callfiltermember',
        primaryjoin="""and_(
            Callfiltermember.bstype == 'secretary',
            Callfiltermember.callfilterid == Callfilter.id
        )""",
        foreign_keys='Callfiltermember.callfilterid',
        order_by='Callfiltermember.priority',
        collection_class=ordering_list('priority', reorder_on_append=True),
        cascade='all, delete-orphan',
        overlaps='recipients',
    )

    @property
    def fallbacks(self):
        return self.callfilter_dialactions

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
