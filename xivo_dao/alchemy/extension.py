# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.schema import Column, UniqueConstraint, Index, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String, Boolean
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import cast, not_

from xivo_dao.helpers.db_manager import Base, IntAsString
from xivo_dao.alchemy import enum


class Extension(Base):

    __tablename__ = 'extensions'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('exten', 'context'),
        Index('extensions__idx__context', 'context'),
        Index('extensions__idx__exten', 'exten'),
        Index('extensions__idx__type', 'type'),
        Index('extensions__idx__typeval', 'typeval'),
    )

    id = Column(Integer)
    commented = Column(Integer, nullable=False, server_default='0')
    context = Column(String(39), nullable=False, server_default='')
    exten = Column(String(40), nullable=False, server_default='')
    type = Column(enum.extenumbers_type, nullable=False)
    typeval = Column(IntAsString(255), nullable=False, server_default='')

    dialpattern = relationship('DialPattern',
                               primaryjoin="""and_(Extension.type == 'outcall',
                                                   Extension.typeval == cast(DialPattern.id, String))""",
                               foreign_keys='Extension.typeval',
                               viewonly=True,
                               back_populates='extension')

    outcall = association_proxy('dialpattern', 'outcall')

    line_extensions = relationship('LineExtension',
                                   cascade='all, delete-orphan',
                                   viewonly=True,
                                   back_populates='extension')

    lines = association_proxy('line_extensions', 'line')

    group = relationship('GroupFeatures',
                         primaryjoin="""and_(Extension.type == 'group',
                                             Extension.typeval == cast(GroupFeatures.id, String))""",
                         foreign_keys='Extension.typeval',
                         viewonly=True,
                         back_populates='extensions')

    incall = relationship('Incall',
                          primaryjoin="""and_(Extension.type == 'incall',
                                              Extension.typeval == cast(Incall.id, String))""",
                          foreign_keys='Extension.typeval',
                          viewonly=True,
                          back_populates='extensions')

    conference = relationship('Conference',
                              primaryjoin="""and_(Extension.type == 'conference',
                                                  Extension.typeval == cast(Conference.id, String))""",
                              foreign_keys='Extension.typeval',
                              viewonly=True,
                              back_populates='extensions')

    parking_lot = relationship('ParkingLot',
                               primaryjoin="""and_(Extension.type == 'parking',
                                                   Extension.typeval == cast(ParkingLot.id, String))""",
                               foreign_keys='Extension.typeval',
                               viewonly=True,
                               back_populates='extensions')

    @property
    def name(self):
        return self.typeval

    def clean_exten(self):
        return self.exten.strip('._')

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
