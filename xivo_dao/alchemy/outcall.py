# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2016 Avencall
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
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.sql import func, cast, not_
from sqlalchemy.types import Integer, String, Text, Boolean

from xivo_dao.helpers.db_manager import Base
from xivo_dao.alchemy.outcalltrunk import OutcallTrunk
from xivo_dao.alchemy.dialpattern import DialPattern


class Outcall(Base):

    __tablename__ = 'outcall'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'),
    )

    id = Column(Integer, nullable=False)
    name = Column(String(128), nullable=False)
    context = Column(String(39))
    useenum = Column(Integer, nullable=False, server_default='0')
    internal = Column(Integer, nullable=False, server_default='0')
    preprocess_subroutine = Column(String(39))
    hangupringtime = Column(Integer, nullable=False, server_default='0')
    commented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text)

    dialpatterns = relationship('DialPattern',
                                primaryjoin="""and_(DialPattern.type == 'outcall',
                                                    DialPattern.typeid == Outcall.id)""",
                                foreign_keys='DialPattern.typeid',
                                cascade='all, delete-orphan')

    extensions = association_proxy('dialpatterns', 'extension',
                                   creator=lambda _extension: DialPattern(type='outcall',
                                                                          exten=_extension.exten,
                                                                          extension=_extension))
    outcall_trunks = relationship('OutcallTrunk',
                                  order_by='OutcallTrunk.priority',
                                  collection_class=ordering_list('priority'),
                                  cascade='all, delete-orphan',
                                  back_populates='outcall')

    trunks = association_proxy('outcall_trunks', 'trunk',
                               creator=lambda _trunk: OutcallTrunk(trunk=_trunk))

    @hybrid_property
    def internal_caller_id(self):
        return self.internal == 1

    @internal_caller_id.expression
    def internal_caller_id(cls):
        return cast(cls.internal, Boolean)

    @internal_caller_id.setter
    def internal_caller_id(self, value):
        self.internal = int(value == 1)

    @hybrid_property
    def ring_time(self):
        if self.hangupringtime == 0:
            return None
        return self.hangupringtime

    @ring_time.expression
    def ring_time(cls):
        return func.nullif(cls.hangupringtime, 0)

    @ring_time.setter
    def ring_time(self, value):
        if value is None:
            self.hangupringtime = 0
        else:
            self.hangupringtime = value

    @hybrid_property
    def enabled(self):
        return self.commented == 0

    @enabled.expression
    def enabled(cls):
        return not_(cast(cls.commented, Boolean))

    @enabled.setter
    def enabled(self, value):
        self.commented = int(value == 0)

    def associate_extension(self, extension, **kwargs):
        extension.type = 'outcall'
        dialpattern = DialPattern(type='outcall',
                                  exten=extension.exten,
                                  **kwargs)
        self.dialpatterns.append(dialpattern)
        index = self.dialpatterns.index(dialpattern)
        self.dialpatterns[index].extension = extension
        self._fix_context()

    def dissociate_extension(self, extension):
        self.extensions.remove(extension)
        extension.type = 'user'
        extension.typeval = '0'
        self._fix_context()

    def _fix_context(self):
        for extension in self.extensions:
            self.context = extension.context
            return
        self.context = None
