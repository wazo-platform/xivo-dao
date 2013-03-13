# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>


import re
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.alchemy.ctipresences import CtiPresences
from xivo_dao.alchemy.ctistatus import CtiStatus


@daosession
def get_config(session):
    res = {}
    ctipresences = session.query(CtiPresences).all()
    for ctipresence in ctipresences:
        res[ctipresence.name] = {}
        status = get_status_with_presence_id(ctipresence.id)
        _build_status_for_presence(status, res[ctipresence.name])
    return res


@daosession
def get_status_with_presence_id(session, presence_id):
    return session.query(CtiStatus).filter(CtiStatus.presence_id == presence_id).all()


def _build_status_for_presence(status, res):
    status_dict = _build_status_dict(status)

    for statut in status:
        ref = res[statut.name] = {}
        ref['longname'] = statut.display_name
        ref['color'] = statut.color
        status_list = statut.access_status.split(',')
        allowed = _build_status_allowed_for_status(status_list, status_dict)
        if allowed:
            ref['allowed'] = allowed
        actions_list = statut.actions.split(',')
        actions = _build_actions_for_status(actions_list)
        if actions:
            ref['actions'] = _build_actions_for_status(actions_list)


def _build_status_dict(status):
    status_dict = {}
    for statut in status:
        status_dict[int(statut.id)] = statut.name
    return status_dict


def _build_status_allowed_for_status(status_list, status_dict):
    allowed = []
    for statut_id in status_list:
        if statut_id:
            allowed.append(status_dict[int(statut_id)])
    return allowed


def _build_actions_for_status(actions_list):
    action_pattern = r'(.*)\((.*)\)'
    actions = {}
    for action in actions_list:
        m = re.match(action_pattern, action)
        if m:
            actions[m.group(1)] = m.group(2)
    return actions
