# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.queueskill import QueueSkill
from xivo_dao.alchemy.queueskillcat import QueueSkillCat

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class SkillPersistor(CriteriaBuilderMixin):

    _search_table = QueueSkill

    def __init__(self, session, skill_search):
        self.session = session
        self.skill_search = skill_search

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(QueueSkill)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        skill = self.find_by(criteria)
        if not skill:
            raise errors.not_found('Skill', **criteria)
        return skill

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        rows, total = self.skill_search.search(self.session, parameters)
        return SearchResult(total, rows)

    def create(self, skill):
        self._set_or_create_category(skill)
        self.session.add(skill)
        self.session.flush()
        return skill

    def edit(self, skill):
        self._set_or_create_category(skill)
        self.session.add(skill)
        self.session.flush()

    def _set_or_create_category(self, skill):
        if not hasattr(skill, '_category'):
            return

        if skill._category is None:
            self.queue_skill_cat = None
            return

        category = self.session.query(QueueSkillCat).filter_by(name=skill._category).first()
        if not category:
            category = QueueSkillCat(name=skill._category)
        skill.queue_skill_cat = category

    def delete(self, skill):
        self.session.delete(skill)
        self.session.flush()
