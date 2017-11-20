# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy import ForeignKey
from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class CtiDirectoryFields(Base):

    __tablename__ = 'ctidirectoryfields'
    __table_args__ = (
        PrimaryKeyConstraint('dir_id', 'fieldname'),
    )

    dir_id = Column(Integer,
                    ForeignKey('ctidirectories.id', ondelete='CASCADE'),
                    autoincrement=False)
    fieldname = Column(String(255), autoincrement=False)
    value = Column(String(255))
