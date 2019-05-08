# -*- coding: utf-8 -*-
# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column, UniqueConstraint, ForeignKey
from sqlalchemy.sql import func, case
from sqlalchemy.types import Integer, String, Text

from xivo_dao.helpers.db_manager import Base


class QueueSkillRule(Base):

    __tablename__ = 'queueskillrule'

    id = Column(Integer, primary_key=True)
    tenant_uuid = Column(String(36), ForeignKey('tenant.uuid', ondelete='CASCADE'), nullable=False)
    name = Column(String(64), unique=True, nullable=False)
    rule = Column(Text)

    @hybrid_property
    def rules(self):
        if not self.rule:
            return []
        return self.rule.split(';')

    @rules.expression
    def rules(cls):
        return case([(cls.rule == None, [])], else_=func.string_to_array(cls.rule, ';'))

    @rules.setter
    def rules(self, value):
        self.rule = ';'.join(value) if value else None
