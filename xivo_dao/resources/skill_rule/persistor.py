# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.queueskillrule import QueueSkillRule

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class SkillRulePersistor(CriteriaBuilderMixin):

    _search_table = QueueSkillRule

    def __init__(self, session, skill_rule_search):
        self.session = session
        self.skill_rule_search = skill_rule_search

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(QueueSkillRule)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        skill_rule = self.find_by(criteria)
        if not skill_rule:
            raise errors.not_found('SkillRule', **criteria)
        return skill_rule

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        rows, total = self.skill_rule_search.search(self.session, parameters)
        return SearchResult(total, rows)

    def create(self, skill_rule):
        self.session.add(skill_rule)
        self.session.flush()
        return skill_rule

    def edit(self, skill_rule):
        self.session.add(skill_rule)
        self.session.flush()

    def delete(self, skill_rule):
        self.session.delete(skill_rule)
        self.session.flush()
