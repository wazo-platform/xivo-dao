# Copyright 2014-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import (
    CheckConstraint,
    Column,
    ForeignKey,
    ForeignKeyConstraint,
    PrimaryKeyConstraint,
)
from sqlalchemy.types import Integer, String

from xivo_dao.alchemy.feature_extension import FeatureExtension
from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.helpers.db_manager import Base


class FuncKeyDestForward(Base):
    DESTINATION_TYPE_ID = 6

    __tablename__ = 'func_key_dest_forward'
    __table_args__ = (
        PrimaryKeyConstraint(
            'func_key_id', 'destination_type_id', 'feature_extension_uuid'
        ),
        ForeignKeyConstraint(
            ('func_key_id', 'destination_type_id'),
            ('func_key.id', 'func_key.destination_type_id'),
        ),
        CheckConstraint(f'destination_type_id = {DESTINATION_TYPE_ID}'),
    )

    func_key_id = Column(Integer)
    destination_type_id = Column(Integer, server_default=f"{DESTINATION_TYPE_ID}")
    feature_extension_uuid = Column(
        UUID(as_uuid=True), ForeignKey('feature_extension.uuid'), nullable=False
    )
    number = Column(String(40))

    type = 'forward'

    func_key = relationship(FuncKey, cascade='all,delete-orphan', single_parent=True)

    feature_extension = relationship(FeatureExtension, viewonly=True)
    feature_extension_feature = association_proxy(
        'feature_extension',
        'feature',
        # Only to keep value persistent in the instance
        creator=lambda _feature: FeatureExtension(feature=_feature),
    )

    def to_tuple(self):
        return (
            ('exten', self.exten),
            ('forward', self.forward),
        )

    @hybrid_property
    def exten(self):
        return self.number

    @exten.setter
    def exten(self, value):
        self.number = value

    @hybrid_property
    def forward(self):
        FORWARDS = {'fwdbusy': 'busy', 'fwdrna': 'noanswer', 'fwdunc': 'unconditional'}
        return FORWARDS.get(
            self.feature_extension_feature, self.feature_extension_feature
        )

    @forward.expression
    def forward(cls):
        return cls.feature_extension_feature  # only used to pass test

    @forward.setter
    def forward(self, value):
        TYPEVALS = {'busy': 'fwdbusy', 'noanswer': 'fwdrna', 'unconditional': 'fwdunc'}
        self.feature_extension_feature = TYPEVALS.get(value, value)
