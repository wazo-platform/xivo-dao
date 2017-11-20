# -*- coding: utf-8 -*-
# Copyright (C) 2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class Monitoring(Base):

    __tablename__ = 'monitoring'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
    )

    id = Column(Integer, nullable=False)
    maintenance = Column(Integer, nullable=False, server_default='0')
    alert_emails = Column(String(4096))
    dahdi_monitor_ports = Column(String(255))
    max_call_duration = Column(Integer)
