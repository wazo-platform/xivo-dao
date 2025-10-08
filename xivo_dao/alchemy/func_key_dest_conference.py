# Copyright 2014-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.orm import relationship
from sqlalchemy.schema import CheckConstraint, Column, ForeignKey, ForeignKeyConstraint
from sqlalchemy.types import Integer

from xivo_dao.alchemy.conference import Conference
from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.helpers.db_manager import Base


class FuncKeyDestConference(Base):
    DESTINATION_TYPE_ID = 4

    __tablename__ = 'func_key_dest_conference'
    __table_args__ = (
        ForeignKeyConstraint(
            ('func_key_id', 'destination_type_id'),
            ('func_key.id', 'func_key.destination_type_id'),
        ),
        CheckConstraint(f'destination_type_id = {DESTINATION_TYPE_ID}'),
    )

    func_key_id = Column(Integer, primary_key=True)
    destination_type_id = Column(
        Integer, primary_key=True, server_default=f"{DESTINATION_TYPE_ID}"
    )
    conference_id = Column(
        Integer, ForeignKey('conference.id', ondelete='CASCADE'), primary_key=True
    )

    type = 'conference'

    func_key = relationship(FuncKey, cascade='all,delete-orphan', single_parent=True)
    conference = relationship(Conference, viewonly=True)

    def to_tuple(self):
        return (('conference_id', self.conference_id),)
