# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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

import abc

from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.alchemy.func_key_dest_bsfilter import FuncKeyDestBSFilter
from xivo_dao.alchemy.func_key_dest_user import FuncKeyDestUser
from xivo_dao.helpers import errors
from xivo_dao.resources.func_key.model import UserFuncKey, BSFilterFuncKey


class FuncKeyManager(object):

    def __init__(self, repositories):
        self.repositories = repositories

    def for_func_key(self, func_key):
        repository = self.repositories.get(func_key.__class__)
        if not repository:
            raise errors.not_found("func key destination type '{}'".format(func_key.__class__))
        return repository


class FuncKeyRepository(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def type_id(self):
        return

    @abc.abstractproperty
    def destination_type_id(self):
        return

    @abc.abstractmethod
    def create(self, session, func_key):
        return

    @abc.abstractmethod
    def delete(self, session, func_key):
        return

    def insert_func_key(self, session):
        row = FuncKey(type_id=self.type_id,
                      destination_type_id=self.destination_type_id)
        session.add(row)
        session.flush()
        return row

    def delete_func_key(self, session, func_key_id):
        (session
         .query(FuncKey)
         .filter(FuncKey.id == func_key_id)
         .delete())


class UserFuncKeyRespository(FuncKeyRepository):

    type_id = 1
    destination_type_id = 1

    def create(self, session, func_key):
        func_key_row = self.insert_func_key(session)
        user_destination_row = FuncKeyDestUser(func_key_id=func_key_row.id,
                                               user_id=func_key.user_id)
        session.add(user_destination_row)
        session.flush()

        return UserFuncKey(id=func_key_row.id, user_id=func_key.user_id)

    def delete(self, session, func_key):
        (session
         .query(FuncKeyDestUser)
         .filter(FuncKeyDestUser.func_key_id == func_key.id)
         .delete())

        self.delete_func_key(session, func_key.id)


class BSFilterFuncKeyRespository(FuncKeyRepository):

    type_id = 1
    destination_type_id = 12

    def create(self, session, func_key):
        func_key_row = self.insert_func_key(session)
        member_row = self._find_member_row(session, func_key)

        destination_row = FuncKeyDestBSFilter(func_key_id=func_key_row.id,
                                              filtermember_id=member_row.id)
        session.add(destination_row)
        session.flush()

        return BSFilterFuncKey(id=func_key_row.id,
                               filter_id=func_key.filter_id,
                               secretary_id=func_key.secretary_id)

    def _find_member_row(self, session, func_key):
        row = (session.query(Callfiltermember.id)
               .filter(Callfiltermember.callfilterid == func_key.filter_id)
               .filter(Callfiltermember.bstype == 'secretary')
               .filter(Callfiltermember.typeval == str(func_key.secretary_id))
               .first())

        return row

    def delete(self, session, func_key):
        member_row = self._find_member_row(session, func_key)

        (session
         .query(FuncKeyDestBSFilter)
         .filter(FuncKeyDestBSFilter.filtermember_id == member_row.id)
         .delete())

        self.delete_func_key(session, func_key.id)


func_key_manager = FuncKeyManager({UserFuncKey: UserFuncKeyRespository(),
                                   BSFilterFuncKey: BSFilterFuncKeyRespository()})
