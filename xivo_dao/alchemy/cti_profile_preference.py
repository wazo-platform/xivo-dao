# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column, PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import relationship

from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.alchemy.cti_preference import CtiPreference
from xivo_dao.helpers.db_manager import Base


class CtiProfilePreference(Base):

    __tablename__ = 'cti_profile_preference'
    __table_args__ = (
        PrimaryKeyConstraint('profile_id', 'preference_id'),
        ForeignKeyConstraint(('profile_id',),
                             ('cti_profile.id',),
                             ondelete='CASCADE'),
        ForeignKeyConstraint(('preference_id',),
                             ('cti_preference.id',),
                             ondelete='CASCADE'),
    )

    profile_id = Column(Integer)
    preference_id = Column(Integer)
    value = Column(String(255))

    cti_profile = relationship(CtiProfile)
    cti_preference = relationship(CtiPreference)
