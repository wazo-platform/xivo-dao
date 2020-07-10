# -*- coding: utf-8 -*-
# Copyright 2014-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.sql.schema import PrimaryKeyConstraint, Column
from sqlalchemy.types import String, Boolean

from xivo_dao.helpers.db_manager import Base
from xivo_dao.helpers.uuid import new_uuid


class Infos(Base):

    __tablename__ = 'infos'
    __table_args__ = (
        PrimaryKeyConstraint('uuid'),
    )

    uuid = Column(String(38), nullable=False, default=new_uuid)
    wazo_version = Column(String(64), nullable=False)
    live_reload_enabled = Column(Boolean, nullable=False, server_default='True')
    timezone = Column(String(128))
    configured = Column(Boolean, nullable=False, server_default='False')
