# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.groupfeatures import GroupFeatures as Group
from xivo_dao.alchemy.rightcallmember import RightCallMember

from xivo_dao.helpers import errors
from xivo_dao.helpers.db_manager import Session
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class GroupPersistor(CriteriaBuilderMixin):

    _search_table = Group

    def __init__(self, session, group_search):
        self.session = session
        self.group_search = group_search

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(Group)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        group = self.find_by(criteria)
        if not group:
            raise errors.not_found('Group', **criteria)
        return group

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        rows, total = self.group_search.search(self.session, parameters)
        return SearchResult(total, rows)

    def create(self, group):
        self.session.add(group)
        self.session.flush()
        return group

    def edit(self, group):
        self.session.add(group)
        self.session.flush()

    def delete(self, group):
        self._delete_associations(group)
        self.session.delete(group)
        self.session.flush()

    def _delete_associations(self, group):
        (self.session.query(RightCallMember)
         .filter(RightCallMember.type == 'group')
         .filter(RightCallMember.typeval == str(group.id))
         .delete())

        (self.session.query(Dialaction)
         .filter(Dialaction.action == 'group')
         .filter(Dialaction.actionarg1 == str(group.id))
         .update({'linked': 0}))

        for extension in group.extensions:
            extension.type = 'user'
            extension.typeval = '0'

    def associate_all_member_users(self, group, members):
        with Session.no_autoflush:
            group.users_member = members
            for member in group.group_members:
                member.fix()
        self.session.flush()

    def associate_all_member_extensions(self, group, members):
        group.extensions_member = members
        self.session.flush()

    def associate_call_permission(self, group, call_permission):
        group.call_permissions.append(call_permission)
        self.session.flush()

    def dissociate_call_permission(self, group, call_permission):
        if call_permission in group.call_permissions:
            group.call_permissions.remove(call_permission)
            self.session.flush()
