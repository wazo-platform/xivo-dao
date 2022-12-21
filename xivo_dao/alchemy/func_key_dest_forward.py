# Copyright 2014-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

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

from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.helpers.db_manager import Base


class FuncKeyDestForward(Base):

    DESTINATION_TYPE_ID = 6

    __tablename__ = 'func_key_dest_forward'
    __table_args__ = (
        PrimaryKeyConstraint('func_key_id', 'destination_type_id', 'extension_id'),
        ForeignKeyConstraint(['func_key_id', 'destination_type_id'],
                             ['func_key.id', 'func_key.destination_type_id']),
        CheckConstraint('destination_type_id = {}'.format(DESTINATION_TYPE_ID)),
    )

    func_key_id = Column(Integer)
    destination_type_id = Column(Integer, server_default="{}".format(DESTINATION_TYPE_ID))
    extension_id = Column(Integer, ForeignKey('extensions.id'))
    number = Column(String(40))

    type = 'forward'

    func_key = relationship(FuncKey, cascade='all,delete-orphan', single_parent=True)

    extension = relationship(Extension)
    extension_typeval = association_proxy(
        'extension', 'typeval',
        # Only to keep value persistent in the instance
        creator=lambda _typeval: Extension(type='extenfeatures',
                                           typeval=_typeval)
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
        FORWARDS = {'fwdbusy': 'busy',
                    'fwdrna': 'noanswer',
                    'fwdunc': 'unconditional'}
        return FORWARDS.get(self.extension_typeval, self.extension_typeval)

    @forward.expression
    def forward(cls):
        return cls.extension_typeval  # only used to pass test

    @forward.setter
    def forward(self, value):
        TYPEVALS = {'busy': 'fwdbusy',
                    'noanswer': 'fwdrna',
                    'unconditional': 'fwdunc'}
        self.extension_typeval = TYPEVALS.get(value, value)
