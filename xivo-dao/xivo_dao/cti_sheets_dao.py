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
    res['events'] = _build_sheetevents(session)
    res.update(_build_sheetactions(session))
    return res


def _build_sheetevents(session):
    events = {}
    ctisheetevents = session.query(CtiSheetEvents).first()
    if ctisheetevents:
        for event_name in ['incomingdid', 'hangup', 'dial', 'link', 'unlink']:
            model_name = getattr(ctisheetevents, event_name)
            if not model_name:
                continue
            events[event_name] = [{
                'display': model_name,
                'option': model_name,
                'condition': model_name
            }]
    return events


def _build_sheetactions(session):
    res = {
        'options': {},
        'displays': {},
        'conditions': {}
    }
    ctisheactions = session.query(CtiSheetActions).all()
    for ctisheaction in ctisheactions:
        try:
            systray_info = json.loads(ctisheaction.systray_info)
            sheet_info = json.loads(ctisheaction.sheet_info)
            action_info = json.loads(ctisheaction.action_info)
        except ValueError:
            continue
        name = ctisheaction.name
        focus = 'yes' if ctisheaction.focus else 'no'
        sheet_qtui = {'null': ctisheaction.sheet_qtui}

        res['options'][name] = {
            'focus': focus,
            'zip': 1,
        }
        res['displays'][name] = {
            'systray_info': systray_info,
            'sheet_info': sheet_info,
            'action_info': action_info,
            'sheet_qtui': sheet_qtui,
        }
        res['conditions'][name] = {
            'whom': ctisheaction.whom,
        }
    return res
