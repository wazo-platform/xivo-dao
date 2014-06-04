# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, PrimaryKeyConstraint, ForeignKeyConstraint, ForeignKey
from sqlalchemy.types import Integer

from xivo_dao.helpers.db_manager import Base


class UserContact(Base):

    __tablename__ = 'user_contact'
    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'phonebook_id'),
        ForeignKeyConstraint(('phonebook_id',),
                             ('phonebook.id',),
                             name='fk_phonebook_id',
                             ondelete='CASCADE'),
        ForeignKeyConstraint(('user_id',),
                             ('userfeatures.id',),
                             name='fk_user_id',
                             ondelete='CASCADE'),
    )

    user_id = Column(Integer, ForeignKey('userfeatures.id'))
    phonebook_id = Column(Integer, ForeignKey('phonebook.id'))

    phonebook = relationship('Phonebook', foreign_keys=phonebook_id)
    user = relationship('UserFeatures', foreign_keys=user_id)
