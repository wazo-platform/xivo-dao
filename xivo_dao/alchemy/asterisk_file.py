# Copyright 2017-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class AsteriskFile(Base):

    __tablename__ = 'asterisk_file'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)

    sections_ordered = relationship('AsteriskFileSection',
                                    order_by='AsteriskFileSection.priority',
                                    viewonly=True)

    sections = relationship('AsteriskFileSection',
                            collection_class=attribute_mapped_collection('name'),
                            cascade='all, delete-orphan',
                            passive_deletes=True)
