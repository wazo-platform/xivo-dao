# -*- coding: utf-8 -*-
# Copyright (C) 2014-2016 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, PrimaryKeyConstraint, Index
from sqlalchemy.types import Integer

from xivo_dao.helpers.db_manager import Base


class OutcallTrunk(Base):

    __tablename__ = 'outcalltrunk'
    __table_args__ = (
        PrimaryKeyConstraint('outcallid', 'trunkfeaturesid'),
        Index('outcalltrunk__idx__priority', 'priority'),
    )

    outcallid = Column(Integer, ForeignKey('outcall.id'), nullable=False)
    trunkfeaturesid = Column(Integer, ForeignKey('trunkfeatures.id'), nullable=False)
    priority = Column(Integer, nullable=False, server_default='0')

    trunk = relationship('TrunkFeatures',
                         back_populates='outcall_trunks')

    outcall = relationship('Outcall',
                           back_populates='outcall_trunks')

    @hybrid_property
    def outcall_id(self):
        return self.outcallid

    @outcall_id.setter
    def outcall_id(self, value):
        self.outcallid = value

    @hybrid_property
    def trunk_id(self):
        return self.trunkfeaturesid

    @trunk_id.setter
    def trunk_id(self, value):
        self.trunkfeaturesid = value
