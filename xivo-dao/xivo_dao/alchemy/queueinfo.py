# -*- coding: UTF-8 -*-

from xivo_dao.alchemy.base import Base
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String


class QueueInfo(Base):
    __tablename__ = 'queue_info'

    id = Column(Integer, primary_key=True)
    call_time_t = Column(Integer)
    queue_name = Column(String(128), nullable=False, server_default='')
    caller = Column(String(80), nullable=False, server_default='')
    caller_uniqueid = Column(String(32), nullable=False, server_default='')
    call_picker = Column(String(80))
    hold_time = Column(Integer)
    talk_time = Column(Integer)
