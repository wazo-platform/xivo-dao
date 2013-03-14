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


from xivo_dao.helpers.db_manager import daosession
from xivo_dao.alchemy.ctisheetactions import CtiSheetActions
from xivo_dao.alchemy.ctisheetevents import CtiSheetEvents
import json


@daosession
def get_config(session):
    res = {}
    res['events'] = _build_sheetevents()
    res.update(_build_sheetactions())
    return res


@daosession
def _build_sheetevents(session):
    events = {}
    ctisheetevents = session.query(CtiSheetEvents).first()
    if ctisheetevents:
        for field_name, ctisheetevent in ctisheetevents.todict().iteritems():
            if field_name == 'id' or not ctisheetevent:
                continue
            tmp = events[field_name] = {}
            tmp["display"] = ctisheetevent
            tmp["option"] = ctisheetevent
            tmp["condition"] = ctisheetevent
    return events


@daosession
def _build_sheetactions(session):
    res = {
        'options': {},
        'displays': {},
        'conditions': {}
    }
    ctisheactions = session.query(CtiSheetActions).all()
    for ctisheaction in ctisheactions:
        name = ctisheaction.name
        res['options'][name] = {}
        res['options'][name]['focus'] = 'yes' if ctisheaction.focus else 'no'
        res['options'][name]['zip'] = 1

        res['displays'][name] = {}
        res['displays'][name]['systray_info'] = json.loads(ctisheaction.systray_info)
        res['displays'][name]['sheet_info'] = json.loads(ctisheaction.sheet_info)
        res['displays'][name]['action_info'] = json.loads(ctisheaction.action_info)
        res['displays'][name]['sheet_qtui'] = {}
        qtui = 'null'
        sheet_info = json.loads(ctisheaction.sheet_info)
        if sheet_info:
            for sheet_info_value in sheet_info.itervalues():
                siv = tuple(sheet_info_value)
                if siv[1] == 'form':
                    qtui = siv[3]

        res['displays'][name]['sheet_qtui'][qtui] = ctisheaction.sheet_qtui

        res['conditions'][name] = {}
        res['conditions'][name]['whom'] = ctisheaction.whom
    return res
