# -*- coding: utf-8 -*-
# Copyright (C) 2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class MeetmeGuest(Base):

    __tablename__ = 'meetmeguest'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
    )

    id = Column(Integer, nullable=False)
    meetmefeaturesid = Column(Integer, nullable=False)
    fullname = Column(String(255), nullable=False)
    telephonenumber = Column(String(40))
    email = Column(String(320))
