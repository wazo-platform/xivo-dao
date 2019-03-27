# -*- coding: utf-8 -*-
# Copyright (C) 2014-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class Provisioning(Base):

    __tablename__ = 'provisioning'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
    )

    id = Column(Integer, nullable=False)
    net4_ip = Column(String(39))
    net4_ip_rest = Column(String(39))
    dhcp_integration = Column(Integer, nullable=False, server_default='0')
    rest_port = Column(Integer, nullable=False)
    http_port = Column(Integer, nullable=False)
