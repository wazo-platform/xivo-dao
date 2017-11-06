# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.helpers.db_manager import Base

from sqlalchemy.schema import Column, ForeignKey, ForeignKeyConstraint, CheckConstraint
from sqlalchemy.types import Integer
from sqlalchemy.orm import relationship


class FuncKeyDestQueue(Base):

    __tablename__ = 'func_key_dest_queue'
    __table_args__ = (
        ForeignKeyConstraint(['func_key_id', 'destination_type_id'],
                             ['func_key.id', 'func_key.destination_type_id']),
        CheckConstraint('destination_type_id = 3')
    )

    func_key_id = Column(Integer, primary_key=True)
    destination_type_id = Column(Integer, primary_key=True, server_default="3")
    queue_id = Column(Integer, ForeignKey('queuefeatures.id'), primary_key=True)

    func_key = relationship(FuncKey)
    queue = relationship(QueueFeatures)
