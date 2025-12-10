# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.orm import joinedload

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.groupfeatures import GroupFeatures as Group
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.helpers import errors
from xivo_dao.helpers.db_manager import Session
from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.resources.utils.search import CriteriaBuilderMixin


class GroupPersistor(CriteriaBuilderMixin, BasePersistor):
    _search_table = Group

    def __init__(self, session, group_search, tenant_uuids=None):
        self.session = session
        self.search_system = group_search
        self.tenant_uuids = tenant_uuids

    def _find_query(self, criteria):
        query = self._search_query()
        query = self.build_criteria(query, criteria)
        if self.tenant_uuids is not None:
            query = query.filter(Group.tenant_uuid.in_(self.tenant_uuids))
        return query

    def get_by(self, criteria):
        model = self.find_by(criteria)
        if not model:
            raise errors.not_found('Group', **criteria)
        return model

    def _search_query(self):
        return (
            self.session.query(Group)
            .options(joinedload(Group.caller_id))
            .options(joinedload(Group.extensions))
            .options(joinedload(Group.incall_dialactions).joinedload(Dialaction.incall))
            .options(joinedload(Group.group_dialactions))
            .options(joinedload(Group.user_queue_members).joinedload(QueueMember.user))
            .options(joinedload(Group._queue))
            .options(joinedload(Group.schedule_paths).joinedload(SchedulePath.schedule))
            .options(
                joinedload(Group.rightcall_members).joinedload(
                    RightCallMember.rightcall
                )
            )
        )

    def delete(self, group):
        self._delete_associations(group)
        self.session.delete(group)
        self.session.flush()

    def _delete_associations(self, group):
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
            self.session.expire(group, ['rightcall_members'])

    def dissociate_call_permission(self, group, call_permission):
        if call_permission in group.call_permissions:
            group.call_permissions.remove(call_permission)
            self.session.flush()
            self.session.expire(group, ['rightcall_members'])
