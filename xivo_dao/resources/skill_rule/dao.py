# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession

from .persistor import SkillRulePersistor
from .search import skill_rule_search


@daosession
def search(session, tenant_uuids=None, **parameters):
    return SkillRulePersistor(session, skill_rule_search, tenant_uuids).search(parameters)


@daosession
def get(session, skill_rule_id, tenant_uuids=None):
    return SkillRulePersistor(session, skill_rule_search, tenant_uuids).get_by({'id': skill_rule_id})


@daosession
def get_by(session, tenant_uuids=None, **criteria):
    return SkillRulePersistor(session, skill_rule_search, tenant_uuids).get_by(criteria)


@daosession
def find(session, skill_rule_id, tenant_uuids=None):
    return SkillRulePersistor(session, skill_rule_search, tenant_uuids).find_by({'id': skill_rule_id})


@daosession
def find_by(session, tenant_uuids=None, **criteria):
    return SkillRulePersistor(session, skill_rule_search, tenant_uuids).find_by(criteria)


@daosession
def find_all_by(session, tenant_uuids=None, **criteria):
    return SkillRulePersistor(session, skill_rule_search, tenant_uuids).find_all_by(criteria)


@daosession
def create(session, skill_rule):
    return SkillRulePersistor(session, skill_rule_search).create(skill_rule)


@daosession
def edit(session, skill_rule):
    SkillRulePersistor(session, skill_rule_search).edit(skill_rule)


@daosession
def delete(session, skill_rule):
    SkillRulePersistor(session, skill_rule_search).delete(skill_rule)
