# Copyright 2017-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column, ForeignKey, Index
from sqlalchemy.types import Integer, String, Text

from xivo_dao.helpers.db_manager import Base


class AsteriskFileVariable(Base):

    __tablename__ = 'asterisk_file_variable'
    __table_args__ = (
        Index('asterisk_file_variable__idx__asterisk_file_section_id', 'asterisk_file_section_id'),
    )

    id = Column(Integer, primary_key=True)
    key = Column(String(255), nullable=False)
    value = Column(Text)
    priority = Column(Integer)
    asterisk_file_section_id = Column(Integer,
                                      ForeignKey('asterisk_file_section.id', ondelete='CASCADE'),
                                      nullable=False)
