# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Index, PrimaryKeyConstraint
from sqlalchemy.types import Boolean, Integer

from xivo_dao.helpers.db_manager import Base


class LineExtension(Base):
    __tablename__ = 'line_extension'
    __table_args__ = (
        PrimaryKeyConstraint('line_id', 'extension_id'),
        Index('line_extension__idx__line_id', 'line_id'),
        Index('line_extension__idx__extension_id', 'extension_id'),
    )

    line_id = Column(
        Integer, ForeignKey('linefeatures.id', ondelete='CASCADE'), nullable=False
    )
    extension_id = Column(
        Integer, ForeignKey('extensions.id', ondelete='CASCADE'), nullable=False
    )
    main_extension = Column(Boolean, nullable=False)

    main_extension_rel = relationship(
        'Extension',
        primaryjoin="""and_(
            LineExtension.extension_id == Extension.id,
            LineExtension.main_extension == True
        )""",
        viewonly=True,
    )

    line = relationship('LineFeatures', back_populates='line_extensions')
    extension = relationship('Extension')
