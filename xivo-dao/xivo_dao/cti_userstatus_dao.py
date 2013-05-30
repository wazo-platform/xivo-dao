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

_ACTION_REGEX = re.compile(r'(.*?)\((.*?)\)')


@daosession
def get_config(session):
    res = {}
    ctipresences = session.query(CtiPresences).all()
    for ctipresence in ctipresences:
        statuses = get_statuses_with_presence_id(ctipresence.id)
        res[ctipresence.name] = _build_status_for_presence(statuses)
    return res


@daosession
def get_statuses_with_presence_id(session, presence_id):
    return session.query(CtiStatus).filter(CtiStatus.presence_id == presence_id).all()


def _build_status_for_presence(statuses):
    res = {}
    status_dict = _build_status_dict(statuses)

    for status in statuses:
        ref = res[status.name] = {}
        ref['longname'] = status.display_name
        ref['color'] = status.color

        status_list = status.access_status.split(',')
        allowed = _build_status_allowed_for_status(status_list, status_dict)
        if allowed:
            ref['allowed'] = allowed

        actions_list = status.actions.split(',')
        actions = _build_actions(actions_list)
        if actions:
            ref['actions'] = actions
    return res


def _build_status_dict(statuses):
    return dict((int(status.id), status.name) for status in statuses)


def _build_status_allowed_for_status(status_list, status_dict):
    allowed = []
    for status_id in status_list:
        if status_id:
            status_id = int(status_id)
            if status_id in status_dict:
                allowed.append(status_dict[status_id])
    return allowed


def _build_actions(actions_list):
    actions = {}
    for action in actions_list:
        m = _ACTION_REGEX.match(action)
        if m:
            actions[m.group(1)] = m.group(2)
    return actions
