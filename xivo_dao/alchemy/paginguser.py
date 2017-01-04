# -*- coding: utf-8 -*-
#
# Copyright 2014-2017 The Wazo Authors  (see the AUTHORS file)
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

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, PrimaryKeyConstraint, Index
from sqlalchemy.types import Integer

from xivo_dao.helpers.db_manager import Base


class PagingUser(Base):

    __tablename__ = 'paginguser'
    __table_args__ = (
        PrimaryKeyConstraint('pagingid', 'userfeaturesid', 'caller'),
        Index('paginguser__idx__pagingid', 'pagingid'),
    )

    pagingid = Column(Integer, ForeignKey('paging.id'), nullable=False)
    userfeaturesid = Column(Integer, ForeignKey('userfeatures.id'), nullable=False)
    caller = Column(Integer, nullable=False, autoincrement=False)

    paging = relationship('Paging')
    user = relationship('UserFeatures')

    @hybrid_property
    def paging_id(self):
        return self.pagingid

    @paging_id.setter
    def paging_id(self, value):
        self.pagingid = value

    @hybrid_property
    def user_id(self):
        return self.userfeaturesid

    @user_id.setter
    def user_id(self, value):
        self.userfeaturesid = value
