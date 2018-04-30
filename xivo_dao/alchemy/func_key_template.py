# -*- coding: utf-8 -*-
# Copyright 2014-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, Boolean, String

from xivo_dao.helpers import errors
from xivo_dao.helpers.db_manager import Base


class FuncKeyTemplate(Base):

    __tablename__ = 'func_key_template'

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=True)
    private = Column(Boolean, nullable=False, server_default='False')

    def __init__(self, **kwargs):
        self.keys = kwargs.pop('keys', {})  # TODO populate this property with relationship
        super(FuncKeyTemplate, self).__init__(**kwargs)

    def get(self, position):
        if position not in self.keys:
            raise errors.not_found('FuncKey', template_id=self.id, position=position)
        return self.keys[position]

    def merge(self, other):
        keys = dict(self.keys)
        other_keys = other.keys
        keys.update(other_keys)
        # TODO Check if we can improve logic to merge/return unified template
        unified_template = FuncKeyTemplate(name=self.name)
        unified_template.keys = keys
        return unified_template
