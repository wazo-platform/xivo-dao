# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column, PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.types import Integer
from sqlalchemy.orm import relationship

from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.alchemy.cti_service import CtiService
from xivo_dao.helpers.db_manager import Base


class CtiProfileService(Base):

    __tablename__ = 'cti_profile_service'
    __table_args__ = (
        PrimaryKeyConstraint('profile_id', 'service_id'),
        ForeignKeyConstraint(('profile_id',),
                             ('cti_profile.id',),
                             ondelete='CASCADE'),
        ForeignKeyConstraint(('service_id',),
                             ('cti_service.id',),
                             ondelete='CASCADE'),
    )

    profile_id = Column(Integer)
    service_id = Column(Integer)

    cti_profile = relationship(CtiProfile)
    cti_service = relationship(CtiService)
