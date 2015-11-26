# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from sqlalchemy import and_

from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.alchemy.func_key_mapping import FuncKeyMapping
from xivo_dao.alchemy.func_key_dest_bsfilter import FuncKeyDestBSFilter
from xivo_dao.alchemy.func_key_dest_user import FuncKeyDestUser


class DestinationPersistor(object):

    def __init__(self, session):
        self.session = session

    def create_user_destination(self, user):
        func_key = FuncKey.new_for_user()
        destination = FuncKeyDestUser(func_key=func_key, userfeatures=user)
        self.session.add(func_key)
        self.session.add(destination)
        self.session.flush()

    def delete_user_destination(self, user):
        self.delete_user_func_key(user)
        self.delete_bsfilter_func_key(user)
        self.session.flush()

    def delete_user_func_key(self, user):
        destination = self.session.query(FuncKeyDestUser).filter_by(user_id=user.id).first()
        self.delete_mappings(destination)
        self.session.delete(destination)
        self.delete_func_key(destination.func_key_id)

    def delete_mappings(self, destination):
        (self.session.query(FuncKeyMapping)
         .filter_by(func_key_id=destination.func_key_id)
         .delete())

    def delete_func_key(self, func_key_id):
        (self.session
         .query(FuncKey)
         .filter(FuncKey.id == func_key_id)
         .delete())

    def delete_bsfilter_func_key(self, user):
        for destination in self.find_secretary_destinations(user):
            self.delete_mappings(destination)
            self.session.delete(destination)
            self.delete_func_key(destination.func_key_id)

    def find_secretary_destinations(self, user):
        return (self.session.query(FuncKeyDestBSFilter)
                .join(Callfiltermember,
                      and_(FuncKeyDestBSFilter.filtermember_id == Callfiltermember.id,
                           Callfiltermember.bstype == 'secretary',
                           Callfiltermember.typeval == str(user.id))))
