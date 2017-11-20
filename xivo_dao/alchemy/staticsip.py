# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column, PrimaryKeyConstraint, Index
from sqlalchemy.types import Integer, String
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property

from xivo_dao.helpers.db_manager import Base


class StaticSIP(Base):

    __tablename__ = 'staticsip'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        Index('staticsip__idx__category', 'category')
    )

    id = Column(Integer, nullable=False)
    cat_metric = Column(Integer, nullable=False, server_default='0')
    var_metric = Column(Integer, nullable=False, server_default='0')
    commented = Column(Integer, nullable=False, server_default='0')
    filename = Column(String(128), nullable=False)
    category = Column(String(128), nullable=False)
    var_name = Column(String(128), nullable=False)
    var_val = Column(String(255))

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
