# Copyright 2014-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column, UniqueConstraint, CheckConstraint
from sqlalchemy.sql import cast, not_
from sqlalchemy.types import Integer, String, Boolean

from xivo_dao.helpers.db_manager import Base


class AccessFeatures(Base):
    __tablename__ = 'accessfeatures'
    __table_args__ = (
        CheckConstraint('feature=\'phonebook\''),
        UniqueConstraint('host', 'feature'),
    )

    id = Column(Integer, primary_key=True)
    host = Column(String(255), nullable=False, server_default='')
    commented = Column(Integer, nullable=False, server_default='0')
    feature = Column(String(64), nullable=False, server_default='phonebook')

    @hybrid_property
    def enabled(self):
        return self.commented == 0

    @enabled.expression
    def enabled(cls):
        return not_(cast(cls.commented, Boolean))

    @enabled.setter
    def enabled(self, value):
        self.commented = int(value is False)
