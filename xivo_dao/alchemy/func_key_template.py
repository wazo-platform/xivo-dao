# Copyright 2014-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column
from sqlalchemy.sql.schema import ForeignKey, Index
from sqlalchemy.types import Boolean, Integer, String

from xivo_dao.helpers import errors
from xivo_dao.helpers.db_manager import Base


class FuncKeyTemplate(Base):
    __tablename__ = 'func_key_template'
    __table_args__ = (Index('func_key_template__idx__tenant_uuid', 'tenant_uuid'),)

    id = Column(Integer, primary_key=True)
    tenant_uuid = Column(
        String(36),
        ForeignKey('tenant.uuid', ondelete='CASCADE'),
        nullable=False,
    )
    name = Column(String(128))
    private = Column(Boolean, nullable=False, server_default='False')

    def __init__(self, **kwargs):
        # keys should probably be retrieved by relationship
        # but that implies to convert FuncKeyMapping.destination as relationship
        self.keys = kwargs.pop('keys', {})
        super().__init__(**kwargs)

    def get(self, position):
        if position not in self.keys:
            raise errors.not_found('FuncKey', template_id=self.id, position=position)
        return self.keys[position]

    def merge(self, other):
        keys = dict(self.keys)
        keys.update(other.keys)
        merged_template = FuncKeyTemplate(name=self.name)
        merged_template.keys = keys
        return merged_template
