# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import (
    Column,
    CheckConstraint,
    ForeignKey,
)
from sqlalchemy.types import String

from xivo_dao.helpers.db_manager import Base


class ApplicationDestNode(Base):

    __tablename__ = 'application_dest_node'

    application_uuid = Column(
        String(36),
        ForeignKey('application.uuid', ondelete='CASCADE'),
        primary_key=True,
    )
    type_ = Column(
        'type',
        String(32),
        CheckConstraint("type in ('holding', 'mixing')"),
        nullable=False,
    )
    music_on_hold = Column(String(128))