# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.alchemy.rightcallmember import RightCallMember as UserCallPermission
from xivo_dao.resources.utils.search import CriteriaBuilderMixin


class Persistor(CriteriaBuilderMixin):

    _search_table = UserCallPermission

    def __init__(self, session):
        self.session = session

    def find_by(self, **criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(UserCallPermission).filter(UserCallPermission.type == 'user')
        return self.build_criteria(query, criteria)

    def get_by(self, **criteria):
        user_call_permission = self.find_by(**criteria)
        if not user_call_permission:
            raise errors.not_found('UserCallPermission', **criteria)
        return user_call_permission

    def find_all_by(self, **criteria):
        query = self._find_query(criteria)
        return query.all()

    def associate_user_call_permission(self, user, call_permission):
        user_call_permission = self.find_by(user_id=user.id, call_permission_id=call_permission.id)
        if not user_call_permission:
            user_call_permission = UserCallPermission(user_id=user.id, call_permission_id=call_permission.id)
            self.session.add(user_call_permission)
            self.session.flush()
        return user_call_permission

    def dissociate_user_call_permission(self, user, call_permission):
        user_call_permission = self.find_by(user_id=user.id, call_permission_id=call_permission.id)
        if user_call_permission:
            self.session.delete(user_call_permission)
            self.session.flush()
        return user_call_permission

    def dissociate_all_call_permissions_by_user(self, user):
        user_call_permissions = self.find_all_by(user_id=user.id)
        for user_call_permission in user_call_permissions:
            self.session.delete(user_call_permission)
        self.session.flush()
        return user_call_permissions
