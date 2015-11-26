# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint, \
    PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from xivo_dao.helpers.db_manager import Base


class UserLine(Base):

    __tablename__ = 'user_line'
    __table_args__ = (
        PrimaryKeyConstraint('id', 'line_id'),
        UniqueConstraint('user_id', 'line_id'),
    )

    id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('userfeatures.id'))
    line_id = Column(Integer, ForeignKey('linefeatures.id'), nullable=False)
    extension_id = Column(Integer, ForeignKey('extensions.id'))
    main_user = Column(Boolean, nullable=False)
    main_line = Column(Boolean, nullable=False)

    linefeatures = relationship("LineFeatures")
    userfeatures = relationship("UserFeatures")
    extensions = relationship("Extension")

    main_user_rel = relationship("UserFeatures",
                                 primaryjoin="""and_(UserLine.user_id == UserFeatures.id,
                                 UserLine.main_user == True)"""
                                 )

    main_extension_rel = relationship("Extension",
                                      primaryjoin="""and_(UserLine.extension_id == Extension.id,
                                      UserLine.main_user == True,
                                      UserLine.main_line == True)"""
                                      )

    main_line_rel = relationship("LineFeatures",
                                 primaryjoin="""and_(UserLine.line_id == LineFeatures.id,
                                 UserLine.main_user == True,
                                 UserLine.main_line == True)"""
                                 )
