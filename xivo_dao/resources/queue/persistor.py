# -*- coding: UTF-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.orm import joinedload
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.queuefeatures import QueueFeatures as Queue

from xivo_dao.helpers import errors
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
