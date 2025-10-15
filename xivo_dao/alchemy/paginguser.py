# Copyright 2014-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Index, PrimaryKeyConstraint
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

    paging = relationship(
        'Paging',
        overlaps='paging,paging_callers,paging_members',
    )
    user = relationship(
        'UserFeatures',
        back_populates='paging_users',
    )

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
