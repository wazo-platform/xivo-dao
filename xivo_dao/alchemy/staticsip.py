# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

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
