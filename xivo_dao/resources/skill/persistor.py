# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.queueskill import QueueSkill
from xivo_dao.alchemy.queueskillcat import QueueSkillCat

from xivo_dao.helpers import errors
from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.resources.utils.search import CriteriaBuilderMixin


class SkillPersistor(CriteriaBuilderMixin, BasePersistor):

    _search_table = QueueSkill

    def __init__(self, session, skill_search, tenant_uuids=None):
        self.session = session
        self.search_system = skill_search
        self.tenant_uuids = tenant_uuids

    def _find_query(self, criteria):
        query = self.session.query(QueueSkill)
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        model = self.find_by(criteria)
        if not model:
            raise errors.not_found('Skill', **criteria)
        return model

    def _search_query(self):
        return self.session.query(self.search_system.config.table)

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
