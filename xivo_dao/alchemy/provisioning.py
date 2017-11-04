# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class Provisioning(Base):

    __tablename__ = 'provisioning'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
    )

    id = Column(Integer, nullable=False)
    net4_ip = Column(String(39), nullable=False)
    net4_ip_rest = Column(String(39), nullable=False)
    username = Column(String(32), nullable=False)
    password = Column(String(32), nullable=False)
    dhcp_integration = Column(Integer, nullable=False, server_default='0')
    rest_port = Column(Integer, nullable=False)
    http_port = Column(Integer, nullable=False)
    private = Column(Integer, nullable=False, server_default='0')
    secure = Column(Integer, nullable=False, server_default='0')
