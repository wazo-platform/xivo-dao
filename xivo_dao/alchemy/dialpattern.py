# Copyright 2012-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class DialPattern(Base):
    __tablename__ = 'dialpattern'
    __table_args__ = (PrimaryKeyConstraint('id'),)

    id = Column(Integer)
    type = Column(String(32), nullable=False)
    typeid = Column(Integer, nullable=False)
    externprefix = Column(String(64))
    prefix = Column(String(32))
    exten = Column(String(40), nullable=False)
    stripnum = Column(Integer)
    callerid = Column(String(80))

    extension = relationship(
        'Extension',
        primaryjoin="""and_(Extension.type == 'outcall',
                            Extension.typeval == cast(DialPattern.id, String))""",
        foreign_keys='Extension.typeval',
        uselist=False,
        passive_deletes='all',
    )

    outcall = relationship(
        'Outcall',
        primaryjoin="""and_(DialPattern.type == 'outcall',
                            DialPattern.typeid == Outcall.id)""",
        foreign_keys='DialPattern.typeid',
        uselist=False,
        overlaps='dialpatterns',
    )

    @hybrid_property
    def external_prefix(self):
        return self.externprefix

    @external_prefix.setter
    def external_prefix(self, value):
        self.externprefix = value

    @hybrid_property
    def strip_digits(self):
        return self.stripnum

    @strip_digits.setter
    def strip_digits(self, value):
        if value is None:
            value = 0  # set default value
        self.stripnum = value

    @hybrid_property
    def caller_id(self):
        return self.callerid

    @caller_id.setter
    def caller_id(self, value):
        self.callerid = value
