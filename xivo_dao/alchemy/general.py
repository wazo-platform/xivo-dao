# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String, Boolean

from xivo_dao.helpers.db_manager import Base


class General(Base):

    __tablename__ = 'general'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
    )

    id = Column(Integer, nullable=False)
    timezone = Column(String(128))
    configured = Column(Boolean, nullable=False, server_default='False')
