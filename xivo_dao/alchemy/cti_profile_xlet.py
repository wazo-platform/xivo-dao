# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column, PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.types import Integer, Boolean
from sqlalchemy.orm import relationship

from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.alchemy.cti_xlet import CtiXlet
from xivo_dao.alchemy.cti_xlet_layout import CtiXletLayout
from xivo_dao.helpers.db_manager import Base


class CtiProfileXlet(Base):

    __tablename__ = 'cti_profile_xlet'
    __table_args__ = (
        PrimaryKeyConstraint('xlet_id', 'profile_id'),
        ForeignKeyConstraint(('xlet_id',),
                             ('cti_xlet.id',),
                             ondelete='CASCADE'),
        ForeignKeyConstraint(('profile_id',),
                             ('cti_profile.id',),
                             ondelete='CASCADE'),
        ForeignKeyConstraint(('layout_id',),
                             ('cti_xlet_layout.id',),
                             ondelete='RESTRICT'),
    )

    xlet_id = Column(Integer)
    profile_id = Column(Integer)
    layout_id = Column(Integer)
    closable = Column(Boolean, server_default='True')
    movable = Column(Boolean, server_default='True')
    floating = Column(Boolean, server_default='True')
    scrollable = Column(Boolean, server_default='True')
    order = Column(Integer)

    cti_xlet = relationship(CtiXlet)
    cti_profile = relationship(CtiProfile)
    cti_xlet_layout = relationship(CtiXletLayout)
