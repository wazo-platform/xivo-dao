# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.schema import Column, UniqueConstraint, Index, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String, Boolean
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import cast

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
