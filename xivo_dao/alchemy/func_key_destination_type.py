# Copyright 2014-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import sql
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class FuncKeyDestinationType(Base):
    __tablename__ = 'func_key_destination_type'

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)

    @classmethod
    def query_id(cls, name):
        return sql.select(cls.id).where(cls.name == name)
