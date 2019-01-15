# -*- coding: utf-8 -*-
# Copyright (C) 2007-2015 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column, PrimaryKeyConstraint, Index, UniqueConstraint
from sqlalchemy.types import Integer, String, Text, Enum

from xivo_dao.helpers.db_manager import Base


class MeetmeFeatures(Base):

    __tablename__ = 'meetmefeatures'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('meetmeid'),
        UniqueConstraint('name'),
        Index('meetmefeatures__idx__context', 'context'),
        Index('meetmefeatures__idx__number', 'confno'),
    )

    id = Column(Integer, nullable=False)
    meetmeid = Column(Integer, nullable=False)
    name = Column(String(80), nullable=False)
    confno = Column(String(40), nullable=False)
    context = Column(String(39), nullable=False)
    admin_typefrom = Column(Enum('none', 'internal', 'external', 'undefined',
                                 name='meetmefeatures_admin_typefrom',
                                 metadata=Base.metadata))
    admin_internalid = Column(Integer)
    admin_externalid = Column(String(40))
    admin_identification = Column(Enum('calleridnum', 'pin', 'all',
                                       name='meetmefeatures_admin_identification',
                                       metadata=Base.metadata),
                                  nullable=False)
    admin_mode = Column(Enum('listen', 'talk', 'all',
                             name='meetmefeatures_mode',
                             metadata=Base.metadata),
                        nullable=False)
    admin_announceusercount = Column(Integer, nullable=False, server_default='0')
    admin_announcejoinleave = Column(Enum('no', 'yes', 'noreview',
                                          name='meetmefeatures_announcejoinleave',
                                          metadata=Base.metadata),
                                     nullable=False)
    admin_moderationmode = Column(Integer, nullable=False, server_default='0')
    admin_initiallymuted = Column(Integer, nullable=False, server_default='0')
    admin_musiconhold = Column(String(128))
    admin_poundexit = Column(Integer, nullable=False, server_default='0')
    admin_quiet = Column(Integer, nullable=False, server_default='0')
    admin_starmenu = Column(Integer, nullable=False, server_default='0')
    admin_closeconflastmarkedexit = Column(Integer, nullable=False, server_default='0')
    admin_enableexitcontext = Column(Integer, nullable=False, server_default='0')
    admin_exitcontext = Column(String(39))
    user_mode = Column(Enum('listen', 'talk', 'all',
                            name='meetmefeatures_mode',
                            metadata=Base.metadata),
                       nullable=False)
    user_announceusercount = Column(Integer, nullable=False, server_default='0')
    user_hiddencalls = Column(Integer, nullable=False, server_default='0')
    user_announcejoinleave = Column(Enum('no', 'yes', 'noreview',
                                         name='meetmefeatures_announcejoinleave',
                                         metadata=Base.metadata),
                                    nullable=False)
    user_initiallymuted = Column(Integer, nullable=False, server_default='0')
    user_musiconhold = Column(String(128))
    user_poundexit = Column(Integer, nullable=False, server_default='0')
    user_quiet = Column(Integer, nullable=False, server_default='0')
    user_starmenu = Column(Integer, nullable=False, server_default='0')
    user_enableexitcontext = Column(Integer, nullable=False, server_default='0')
    user_exitcontext = Column(String(39))
    talkeroptimization = Column(Integer, nullable=False, server_default='0')
    record = Column(Integer, nullable=False, server_default='0')
    talkerdetection = Column(Integer, nullable=False, server_default='0')
    noplaymsgfirstenter = Column(Integer, nullable=False, server_default='0')
    durationm = Column(Integer)
    closeconfdurationexceeded = Column(Integer, nullable=False, server_default='0')
    nbuserstartdeductduration = Column(Integer)
    timeannounceclose = Column(Integer)
    maxusers = Column(Integer, nullable=False, server_default='0')
    startdate = Column(Integer)
    emailfrom = Column(String(255))
    emailfromname = Column(String(255))
    emailsubject = Column(String(255))
    emailbody = Column(Text, nullable=False)
    preprocess_subroutine = Column(String(39))
    description = Column(Text, nullable=False)
    commented = Column(Integer, server_default='0')
