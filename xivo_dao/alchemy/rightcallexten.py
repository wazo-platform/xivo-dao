# Copyright 2014-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column, ForeignKey, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class RightCallExten(Base):
    __tablename__ = 'rightcallexten'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('rightcallid', 'exten'),
    )

    id = Column(Integer, nullable=False)
    rightcallid = Column(
        Integer,
        ForeignKey('rightcall.id', ondelete='CASCADE'),
        nullable=False,
        server_default='0',
    )
    exten = Column(String(40), nullable=False, server_default='')
