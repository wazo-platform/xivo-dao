# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.orm import joinedload
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.groupfeatures import GroupFeatures as Group

from xivo_dao.helpers import errors
from xivo_dao.helpers.db_manager import Session
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class GroupPersistor(CriteriaBuilderMixin):

    _search_table = Group

    def __init__(self, session, group_search, tenant_uuids=None):
        self.session = session
        self.group_search = group_search
        self.tenant_uuids = tenant_uuids

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self._joinedload_query()
        query = self.build_criteria(query, criteria)
        if self.tenant_uuids is not None:
            query = query.filter(Group.tenant_uuid.in_(self.tenant_uuids))
        return query

    def get_by(self, criteria):
        group = self.find_by(criteria)
        if not group:
            raise errors.not_found('Group', **criteria)
        return group

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        query = self._joinedload_query()
        if self.tenant_uuids is not None:
            query = query.filter(Group.tenant_uuid.in_(self.tenant_uuids))

        rows, total = self.group_search.search_from_query(query, parameters)
        return SearchResult(total, rows)

    def _joinedload_query(self):
        return (self.session.query(Group)
                .options(joinedload('caller_id'))
                .options(joinedload('extensions'))
                .options(joinedload('incall_dialactions')
                         .joinedload('incall'))
                .options(joinedload('group_dialactions'))
                .options(joinedload('user_queue_members')
                         .joinedload('user'))
                .options(joinedload('queue'))
                .options(joinedload('schedule_paths')
                         .joinedload('schedule'))
                .options(joinedload('rightcall_members')
                         .joinedload('rightcall')))

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
        (self.session.query(Dialaction)
         .filter(Dialaction.action == 'group')
         .filter(Dialaction.actionarg1 == str(group.id))
         .update({'linked': 0}))

        for extension in group.extensions:
            extension.type = 'user'
            extension.typeval = '0'

    def associate_all_member_users(self, group, members):
        with Session.no_autoflush:
            group.user_queue_members = []
            for member in members:
                self._fill_user_queue_member_default_values(member)
                group.user_queue_members.append(member)
                member.fix()
        self.session.flush()

    def _fill_user_queue_member_default_values(self, member):
        member.category = 'group'
        member.usertype = 'user'

    def associate_all_member_extensions(self, group, members):
        with Session.no_autoflush:
            group.extension_queue_members = []
            for member in members:
                self._fill_extension_queue_member_default_values(member)
                group.extension_queue_members.append(member)
                member.fix()
        self.session.flush()

    def _fill_extension_queue_member_default_values(self, member):
        member.category = 'group'
        member.usertype = 'user'
        member.userid = 0

    def associate_call_permission(self, group, call_permission):
        if call_permission not in group.call_permissions:
            group.call_permissions.append(call_permission)
            self.session.flush()

    def dissociate_call_permission(self, group, call_permission):
        if call_permission in group.call_permissions:
            group.call_permissions.remove(call_permission)
            self.session.flush()
