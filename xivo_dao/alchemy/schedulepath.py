# -*- coding: utf-8 -*-
# Copyright 2007-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Index, PrimaryKeyConstraint
from sqlalchemy.types import Integer

from xivo_dao.helpers.db_manager import Base
from . import enum


class SchedulePath(Base):

    __tablename__ = 'schedule_path'
    __table_args__ = (
        PrimaryKeyConstraint('schedule_id', 'path', 'pathid'),
        Index('schedule_path_path', 'path', 'pathid'),
    )

    schedule_id = Column(Integer, ForeignKey('schedule.id'))
    path = Column(enum.schedule_path_type, nullable=False)
    pathid = Column(Integer, autoincrement=False)

    incall = relationship('Incall',
                          primaryjoin="""and_(SchedulePath.path == 'incall',
                                              SchedulePath.pathid == Incall.id)""",
                          foreign_keys='SchedulePath.pathid',
                          viewonly=True,
                          back_populates='schedule_paths')

    group = relationship('GroupFeatures',
                         primaryjoin="""and_(SchedulePath.path == 'group',
                                             SchedulePath.pathid == GroupFeatures.id)""",
                         foreign_keys='SchedulePath.pathid',
                         viewonly=True,
                         back_populates='schedule_paths')

    outcall = relationship('Outcall',
                           primaryjoin="""and_(SchedulePath.path == 'outcall',
                                               SchedulePath.pathid == Outcall.id)""",
                           foreign_keys='SchedulePath.pathid',
                           viewonly=True,
                           back_populates='schedule_paths')

    queue = relationship('QueueFeatures',
                         primaryjoin="""and_(SchedulePath.path == 'queue',
                                             SchedulePath.pathid == QueueFeatures.id)""",
                         foreign_keys='SchedulePath.pathid',
                         viewonly=True,
                         back_populates='schedule_paths')

    user = relationship('UserFeatures',
                        primaryjoin="""and_(SchedulePath.path == 'user',
                                            SchedulePath.pathid == UserFeatures.id)""",
                        foreign_keys='SchedulePath.pathid',
                        viewonly=True,
                        back_populates='schedule_paths')

    schedule = relationship('Schedule',
                            back_populates='schedule_paths')
