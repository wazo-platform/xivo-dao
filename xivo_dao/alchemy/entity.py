# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import sql
from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.types import Integer, String, Text

from xivo_dao.helpers.db_manager import Base


class Entity(Base):

    __tablename__ = 'entity'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'),
    )

    id = Column(Integer)
    name = Column(String(64), nullable=False, server_default='')
    displayname = Column(String(128), nullable=False, server_default='')
    phonenumber = Column(String(40), nullable=False, server_default='')
    faxnumber = Column(String(40), nullable=False, server_default='')
    email = Column(String(255), nullable=False, server_default='')
    url = Column(String(255), nullable=False, server_default='')
    address1 = Column(String(30), nullable=False, server_default='')
    address2 = Column(String(30), nullable=False, server_default='')
    city = Column(String(128), nullable=False, server_default='')
    state = Column(String(128), nullable=False, server_default='')
    zipcode = Column(String(16), nullable=False, server_default='')
    country = Column(String(3), nullable=False, server_default='')
    disable = Column(Integer, nullable=False, server_default='0')
    dcreate = Column(Integer, nullable=False, server_default='0')
    description = Column(Text, nullable=False)

    @classmethod
    def query_default_id(cls):
        return sql.select([cls.id]).limit(1)

    @classmethod
    def query_default_name(cls):
        return sql.select([cls.name]).limit(1)

    @hybrid_property
    def display_name(self):
        if self.displayname == '':
            return None
        return self.displayname

    @display_name.expression
    def display_name(cls):
        return func.nullif(cls.displayname, '')

    @display_name.setter
    def display_name(self, value):
        if value is None:
            self.displayname = ''
        else:
            self.displayname = value
