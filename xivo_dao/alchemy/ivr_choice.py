# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Index, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.helpers.db_manager import Base


class IVRChoice(Base):
    __tablename__ = 'ivr_choice'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        Index('ivr_choice__idx__ivr_id', 'ivr_id'),
    )

    id = Column(Integer)
    ivr_id = Column(Integer, ForeignKey('ivr.id', ondelete='CASCADE'), nullable=False)
    exten = Column(String(40), nullable=False)

    dialaction = relationship(
        Dialaction,
        primaryjoin="""and_(Dialaction.category == 'ivr_choice',
                            Dialaction.categoryval == cast(IVRChoice.id, String))""",
        foreign_keys='Dialaction.categoryval',
        cascade='all, delete-orphan',
        back_populates='ivr_choice',
        uselist=False,
        overlaps=(
            'callfilter_dialactions,'
            'dialaction,'
            'dialactions,'
            'group_dialactions,'
            'ivr_choice,'
            'queue_dialactions,'
            'switchboard_dialactions,'
            'user_dialactions,'
        ),
    )

    @property
    def destination(self):
        return self.dialaction

    @destination.setter
    def destination(self, destination):
        if not self.dialaction:
            destination.event = 'ivr_choice'
            destination.category = 'ivr_choice'
            self.dialaction = destination

        self.dialaction.action = destination.action
        self.dialaction.actionarg1 = destination.actionarg1
        self.dialaction.actionarg2 = destination.actionarg2
