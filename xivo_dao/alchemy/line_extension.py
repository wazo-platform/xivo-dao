# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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

from sqlalchemy.types import Integer, Boolean
from sqlalchemy.schema import (Column,
                               ForeignKey,
                               PrimaryKeyConstraint)
from sqlalchemy.orm import relationship
from xivo_dao.helpers.db_manager import Base


class LineExtension(Base):

    __tablename__ = 'line_extension'
    __table_args__ = (
        PrimaryKeyConstraint('line_id', 'extension_id'),
    )

    line_id = Column(Integer, ForeignKey('linefeatures.id'), nullable=False)
    extension_id = Column(Integer, ForeignKey('extensions.id'), nullable=False)
    main_extension = Column(Boolean, nullable=False)

    linefeatures = relationship("LineFeatures")
    extensions = relationship("Extension")

    main_extension_rel = relationship("Extension",
                                      primaryjoin="""and_(LineExtension.extension_id == Extension.id,
                                      LineExtension.main_extension == True)"""
                                      )
