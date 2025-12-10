# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.orm import joinedload

from xivo_dao.alchemy.contextmember import ContextMember
from xivo_dao.alchemy.queuefeatures import QueueFeatures as Queue
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.helpers import errors
from xivo_dao.helpers.db_manager import Session
from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.resources.utils.search import CriteriaBuilderMixin


class QueuePersistor(CriteriaBuilderMixin, BasePersistor):
    _search_table = Queue

    def __init__(self, session, queue_search, tenant_uuids=None):
        self.session = session
        self.search_system = queue_search
        self.tenant_uuids = tenant_uuids

    def _find_query(self, criteria):
        query = self._joinedload_query()
        query = self.build_criteria(query, criteria)
        if self.tenant_uuids is not None:
            query = query.filter(Queue.tenant_uuid.in_(self.tenant_uuids))
        return query

    def get_by(self, criteria):
        model = self.find_by(criteria)
        if not model:
            raise errors.not_found('Queue', **criteria)
        return model

    def _search_query(self):
        return self._joinedload_query()

    def _joinedload_query(self):
        return (
            self.session.query(Queue)
            .options(joinedload(Queue._queue))
            .options(joinedload(Queue.extensions))
            .options(joinedload(Queue.caller_id))
            .options(joinedload(Queue.queue_dialactions))
            .options(joinedload(Queue.schedule_paths).joinedload(SchedulePath.schedule))
        )

    def delete(self, queue):
        self._delete_associations(queue)
        self.session.delete(queue)
        self.session.flush()

    def _delete_associations(self, queue):
        (
            self.session.query(ContextMember)
            .filter(ContextMember.type == 'queue')
            .filter(ContextMember.typeval == str(queue.id))
            .delete()
        )

        for extension in queue.extensions:
            extension.type = 'user'
            extension.typeval = '0'

    def associate_schedule(self, queue, schedule):
        queue.schedules = [schedule]
        self.session.flush()

    def dissociate_schedule(self, queue, schedule):
        queue.schedules = []
        self.session.flush()

    def associate_member_user(self, queue, member):
        if member not in queue.user_queue_members:
            with Session.no_autoflush:
                self._fill_user_queue_member_default_values(member)
                queue.user_queue_members.append(member)
                member.fix()
        self.session.flush()

    def _fill_user_queue_member_default_values(self, member):
        member.category = 'queue'
        member.usertype = 'user'

    def dissociate_member_user(self, queue, member):
        try:
            queue.user_queue_members.remove(member)
            self.session.flush()
        except ValueError:
            pass

    def associate_member_agent(self, queue, member):
        if member not in queue.agent_queue_members:
            with Session.no_autoflush:
                self._fill_agent_queue_member_default_values(member)
                queue.agent_queue_members.append(member)
                member.fix()
        self.session.flush()

    def _fill_agent_queue_member_default_values(self, member):
        member.category = 'queue'
        member.usertype = 'agent'

    def dissociate_member_agent(self, queue, member):
        try:
            queue.agent_queue_members.remove(member)
            self.session.flush()
        except ValueError:
            pass
