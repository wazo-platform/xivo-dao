# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column, ForeignKeyConstraint, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import relationship

from xivo_dao.alchemy.ctiphonehintsgroup import CtiPhoneHintsGroup
from xivo_dao.alchemy.ctipresences import CtiPresences
from xivo_dao.helpers.db_manager import Base


class CtiProfile(Base):

    __tablename__ = 'cti_profile'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        ForeignKeyConstraint(('presence_id',),
                             ('ctipresences.id',),
                             ondelete='RESTRICT'),
        ForeignKeyConstraint(('phonehints_id',),
                             ('ctiphonehintsgroup.id',),
                             ondelete='RESTRICT'),
    )

    id = Column(Integer)
    name = Column(String(255), nullable=False)
    presence_id = Column(Integer)
    phonehints_id = Column(Integer)

    ctipresences = relationship(CtiPresences)
    ctiphonehintsgroup = relationship(CtiPhoneHintsGroup)
