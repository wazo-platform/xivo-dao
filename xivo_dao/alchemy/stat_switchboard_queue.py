# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKeyConstraint, Index, PrimaryKeyConstraint
from sqlalchemy.types import DateTime, Float, Integer

from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.enum import stat_switchboard_endtype
from xivo_dao.helpers.db_manager import Base


class StatSwitchboardQueue(Base):

    __tablename__ = 'stat_switchboard_queue'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        ForeignKeyConstraint(('queue_id',),
                             ('queuefeatures.id',),
                             ondelete='CASCADE'),
        Index('stat_switchboard_queue__idx__queue_id', 'queue_id'),
        Index('stat_switchboard_queue__idx__time', 'time'),
    )

    id = Column(Integer, nullable=False, primary_key=True)
    time = Column(DateTime, nullable=False)
    end_type = Column(stat_switchboard_endtype, nullable=False)
    wait_time = Column(Float, nullable=False)
    queue_id = Column(Integer, nullable=False)

    queue = relationship(QueueFeatures)
