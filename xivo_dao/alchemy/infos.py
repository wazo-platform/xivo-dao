# -*- coding: utf-8 -*-
# Copyright 2014-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.sql.schema import PrimaryKeyConstraint, Column
from sqlalchemy.types import String

from xivo_dao.helpers.db_manager import Base
from xivo_dao.helpers.uuid import new_uuid


class Infos(Base):

    __tablename__ = 'infos'
    __table_args__ = (
        PrimaryKeyConstraint('uuid'),
    )

    uuid = Column(String(38), nullable=False, default=new_uuid)
    wazo_version = Column(String(64), nullable=False)
