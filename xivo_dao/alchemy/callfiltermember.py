# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import column_property, relationship
from sqlalchemy.schema import CheckConstraint, Column, UniqueConstraint
from sqlalchemy.sql.elements import and_
from sqlalchemy.sql.expression import select
from sqlalchemy.types import Enum, Integer, String

from xivo_dao.alchemy import enum
from xivo_dao.alchemy.callfilter import Callfilter
from xivo_dao.helpers.db_manager import Base


class Callfiltermember(Base):
    __tablename__ = 'callfiltermember'
    __table_args__ = (
        UniqueConstraint('callfilterid', 'type', 'typeval'),
        CheckConstraint("bstype in ('boss', 'secretary')"),
    )

    id = Column(Integer, primary_key=True)
    callfilterid = Column(Integer, nullable=False, server_default='0')
    type = Column(
        Enum('user', name='callfiltermember_type', metadata=Base.metadata),
        nullable=False,
    )
    typeval = Column(String(128), nullable=False, server_default='0')
    ringseconds = Column(Integer, nullable=False, server_default='0')
    priority = Column(Integer, nullable=False, server_default='0')
    bstype = Column(enum.generic_bsfilter, nullable=False)
    active = Column(Integer, nullable=False, server_default='0')

    callfilter_exten = column_property(
        select(Callfilter.exten)
        .where(and_(Callfilter.id == callfilterid, bstype == 'secretary'))
        .correlate_except(Callfilter)
        .scalar_subquery()
    )

    func_keys = relationship('FuncKeyDestBSFilter', cascade='all, delete-orphan')

    user = relationship(
        'UserFeatures',
        primaryjoin="""and_(Callfiltermember.type == 'user',
                            Callfiltermember.typeval == cast(UserFeatures.id, String))""",
        foreign_keys='Callfiltermember.typeval',
        overlaps='call_filter_recipients,call_filter_surrogates',
    )

    @hybrid_property
    def timeout(self):
        if self.ringseconds == 0:
            return None
        return self.ringseconds

    @timeout.setter
    def timeout(self, value):
        if value is None:
            self.ringseconds = 0
        else:
            self.ringseconds = value
