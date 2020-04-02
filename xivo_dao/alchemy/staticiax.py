# -*- coding: utf-8 -*-
# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, PrimaryKeyConstraint, Index
from sqlalchemy.sql import func, cast, not_
from sqlalchemy.types import Boolean, Integer, String

from xivo_dao.helpers.db_manager import Base


class StaticIAX(Base):

    __tablename__ = 'staticiax'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        Index('staticiax__idx__category', 'category')
    )

    id = Column(Integer, nullable=False)
    cat_metric = Column(Integer, nullable=False, server_default='0')
    var_metric = Column(Integer, nullable=False, server_default='0')
    commented = Column(Integer, nullable=False, server_default='0')
    filename = Column(String(128), nullable=False)
    category = Column(String(128), nullable=False)
    var_name = Column(String(128), nullable=False)
    var_val = Column(String(255))

    trunk = relationship('TrunkFeatures',
                         primaryjoin="""and_(
                                       TrunkFeatures.protocol == 'iax',
                                       TrunkFeatures.registerid == StaticIAX.id
                         )""",
                         foreign_keys='TrunkFeatures.registerid',
                         viewonly=True,
                         uselist=False)

    @hybrid_property
    def metric(self):
        if self.var_metric == 0:
            return None
        return self.var_metric + 1

    @metric.expression
    def metric(cls):
        return func.nullif(cls.var_metric, 0)

    @metric.setter
    def metric(self, value):
        if value is None:
            self.var_metric = 0
        else:
            self.var_metric = value + 1

    @hybrid_property
    def enabled(self):
        if self.commented is None:
            return None
        return self.commented == 0

    @enabled.expression
    def enabled(cls):
        return not_(cast(cls.commented, Boolean))

    @enabled.setter
    def enabled(self, value):
        self.commented = int(value is False)
