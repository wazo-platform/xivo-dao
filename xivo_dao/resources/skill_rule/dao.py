# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_manager import daosession

from .persistor import SkillRulePersistor
from .search import skill_rule_search


@daosession
def search(session, **parameters):
    return SkillRulePersistor(session, skill_rule_search).search(parameters)


@daosession
def get(session, skill_rule_id):
    return SkillRulePersistor(session, skill_rule_search).get_by({'id': skill_rule_id})


@daosession
def get_by(session, **criteria):
    return SkillRulePersistor(session, skill_rule_search).get_by(criteria)


@daosession
def find(session, skill_rule_id):
    return SkillRulePersistor(session, skill_rule_search).find_by({'id': skill_rule_id})


@daosession
def find_by(session, **criteria):
    return SkillRulePersistor(session, skill_rule_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return SkillRulePersistor(session, skill_rule_search).find_all_by(criteria)


@daosession
def create(session, skill_rule):
    return SkillRulePersistor(session, skill_rule_search).create(skill_rule)


@daosession
def edit(session, skill_rule):
    SkillRulePersistor(session, skill_rule_search).edit(skill_rule)


@daosession
def delete(session, skill_rule):
    SkillRulePersistor(session, skill_rule_search).delete(skill_rule)
