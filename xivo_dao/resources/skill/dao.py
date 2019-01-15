# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession

from .persistor import SkillPersistor
from .search import skill_search


@daosession
def search(session, **parameters):
    return SkillPersistor(session, skill_search).search(parameters)


@daosession
def get(session, skill_id):
    return SkillPersistor(session, skill_search).get_by({'id': skill_id})


@daosession
def get_by(session, **criteria):
    return SkillPersistor(session, skill_search).get_by(criteria)


@daosession
def find(session, skill_id):
    return SkillPersistor(session, skill_search).find_by({'id': skill_id})


@daosession
def find_by(session, **criteria):
    return SkillPersistor(session, skill_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return SkillPersistor(session, skill_search).find_all_by(criteria)


@daosession
def create(session, skill):
    return SkillPersistor(session, skill_search).create(skill)


@daosession
def edit(session, skill):
    SkillPersistor(session, skill_search).edit(skill)


@daosession
def delete(session, skill):
    SkillPersistor(session, skill_search).delete(skill)
