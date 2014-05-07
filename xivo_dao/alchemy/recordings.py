# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Integer, DateTime
from sqlalchemy.orm import relationship

from xivo_dao.helpers.db_manager import Base


class Recordings(Base):

    __tablename__ = 'recording'

    cid = Column(String(32), primary_key=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    caller = Column(String(32))
    client_id = Column(String(1024))
    callee = Column(String(32))
    filename = Column(String(1024))
    campaign_id = Column(Integer, ForeignKey('record_campaign.id'), nullable=False)
    agent_id = Column(Integer, ForeignKey('agentfeatures.id'), nullable=False)

    record_campaign = relationship("RecordCampaigns", foreign_keys=campaign_id)
    agentfeatures = relationship("AgentFeatures", foreign_keys=agent_id)
