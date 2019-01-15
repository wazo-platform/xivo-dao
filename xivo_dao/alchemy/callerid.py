# -*- coding: utf-8 -*-
# Copyright (C) 2014 Avencall
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String, Enum

from xivo_dao.helpers.db_manager import Base


class Callerid(Base):

    __tablename__ = 'callerid'
    __table_args__ = (
        PrimaryKeyConstraint('type', 'typeval'),
    )

    mode = Column(Enum('prepend', 'overwrite', 'append',
                       name='callerid_mode',
                       metadata=Base.metadata))
    callerdisplay = Column(String(80), nullable=False, server_default='')
    type = Column(Enum('callfilter', 'incall', 'group', 'queue',
                       name='callerid_type',
                       metadata=Base.metadata))
    typeval = Column(Integer, nullable=False, autoincrement=False)

    @hybrid_property
    def name(self):
        if self.callerdisplay == '':
            return None
        return self.callerdisplay

    @name.setter
    def name(self, value):
        if value is None:
            self.callerdisplay = ''
        else:
            self.callerdisplay = value
