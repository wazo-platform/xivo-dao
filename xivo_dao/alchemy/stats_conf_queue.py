# Copyright 2014-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text
from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import Integer, SmallInteger

from xivo_dao.helpers.db_manager import Base


class StatsConfQueue(Base):

    __tablename__ = 'stats_conf_queue'
    __table_args__ = (
        PrimaryKeyConstraint('stats_conf_id', 'queuefeatures_id'),
    )

    stats_conf_id = Column(Integer, nullable=False, autoincrement=False)
    queuefeatures_id = Column(Integer, nullable=False, autoincrement=False)
    qos = Column(SmallInteger, nullable=False, server_default=text('0'))
