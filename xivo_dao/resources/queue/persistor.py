# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.orm import joinedload
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.queuefeatures import QueueFeatures as Queue

from xivo_dao.helpers import errors
from xivo_dao.helpers.db_manager import Session
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class QueuePersistor(CriteriaBuilderMixin):

    _search_table = Queue

    def __init__(self, session, queue_search):
        self.session = session
        self.queue_search = queue_search

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self._joinedload_query()
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        queue = self.find_by(criteria)
        if not queue:
            raise errors.not_found('Queue', **criteria)
        return queue

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        rows, total = self.queue_search.search_from_query(self._joinedload_query(), parameters)
        return SearchResult(total, rows)

    def _joinedload_query(self):
        return (
            self.session.query(Queue)
            .options(joinedload('_queue'))
            .options(joinedload('extensions'))
            .options(joinedload('caller_id'))
            .options(joinedload('queue_dialactions'))
            .options(joinedload('schedule_paths')
                     .joinedload('schedule'))
        )

    def create(self, queue):
        self.session.add(queue)
        self.session.flush()
        return queue

    def edit(self, queue):
        self.session.add(queue)
        self.session.flush()

    def delete(self, queue):
        self._delete_associations(queue)
        self.session.delete(queue)
        self.session.flush()

    def _delete_associations(self, queue):
        (self.session.query(Dialaction)
         .filter(Dialaction.action == 'queue')
         .filter(Dialaction.actionarg1 == str(queue.id))
         .update({'linked': 0}))

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
