# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
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

from __future__ import unicode_literals

from xivo_dao import cti_sheets_dao
from xivo_dao.alchemy.ctisheetactions import CtiSheetActions
from xivo_dao.alchemy.ctisheetevents import CtiSheetEvents
from xivo_dao.tests.test_dao import DAOTestCase


class TestCtiSheetsDAO(DAOTestCase):

    def test_get_config(self):
        expected_result = {
            'conditions': {
                'XiVO': {'whom': 'dest'},
            },
            'displays': {
                'XiVO': {
                    'action_info': {},
                    'sheet_info': {
                        '10': ['Nom',
                               'title',
                               '',
                               '{xivo-calleridname}',
                               0],
                        '20': ['Num\xe9ro',
                               'text',
                               '',
                               '{xivo-calleridnum}',
                               0],
                        '30': ['Origine',
                               'text',
                               '',
                               '{xivo-origin}',
                               0]
                    },
                    'sheet_qtui': 'file:///tmp/test.ui',
                    'systray_info': {
                        '10': ['Nom',
                               'title',
                               '',
                               '{xivo-calledidname}'],
                        '20': ['Num\xe9ro',
                               'body',
                               '',
                               '{xivo-calleridnum}'],
                        '30': ['Origine',
                               'body',
                               '',
                               '{xivo-origin}']
                    }
                }
            },
            'events': {
                'dial': [{
                    'condition': 'XiVO',
                    'display': 'XiVO',
                    'option': 'XiVO'
                }],
                'link': [{
                    'condition': 'XiVO',
                    'display': 'XiVO',
                    'option': 'XiVO'
                }]
            },
            'options': {
                'XiVO': {
                    'focus': 'no',
                    'zip': 1
                }
            }
        }

        self._add_ctisheetevents()
        self._add_ctisheetactions()
        self._add_bad_ctisheetactions()

        result = cti_sheets_dao.get_config()

        self.assertEqual(expected_result, result)

    def test_no_qtui(self):
        self._add_ctisheetevents()
        self._add_ctisheetactions(qt_ui='')

        result = cti_sheets_dao.get_config()

        self.assertTrue('sheet_qtui' not in result['displays']['XiVO'],
                        'sheet_qtui is in the displays')

    def _add_ctisheetevents(self):
        cti_sheetevent = CtiSheetEvents()
        cti_sheetevent.incomingdid = ''
        cti_sheetevent.hangup = ''
        cti_sheetevent.dial = 'XiVO'
        cti_sheetevent.link = 'XiVO'
        cti_sheetevent.unlink = ''

        self.add_me(cti_sheetevent)
        return cti_sheetevent.id

    def _add_ctisheetactions(self, qt_ui='file:///tmp/test.ui'):
        cti_sheetaction = CtiSheetActions()
        cti_sheetaction.name = 'XiVO'
        cti_sheetaction.description = 'Modèle de fiche de base.'
        cti_sheetaction.whom = 'dest'
        cti_sheetaction.sheet_info = '{"10": [ "Nom","title","","{xivo-calleridname}",0 ],"20": [ "Numéro","text","","{xivo-calleridnum}",0 ],"30": [ "Origine","text","","{xivo-origin}",0 ]}'
        cti_sheetaction.systray_info = '{"10": [ "Nom","title","","{xivo-calledidname}" ],"20": [ "Numéro","body","","{xivo-calleridnum}" ],"30": [ "Origine","body","","{xivo-origin}" ]}'
        cti_sheetaction.sheet_qtui = qt_ui
        cti_sheetaction.action_info = '{}'
        cti_sheetaction.focus = 0
        cti_sheetaction.deletable = 1
        cti_sheetaction.disable = 1

        self.add_me(cti_sheetaction)
        return cti_sheetaction.id

    def _add_bad_ctisheetactions(self):
        cti_sheetaction = CtiSheetActions()
        cti_sheetaction.name = 'bad'
        cti_sheetaction.description = ''
        cti_sheetaction.whom = 'dest'
        cti_sheetaction.sheet_info = '{"bad}'
        cti_sheetaction.systray_info = '{"bad}'
        cti_sheetaction.sheet_qtui = ''
        cti_sheetaction.action_info = '{"bad}'
        cti_sheetaction.focus = 0
        cti_sheetaction.deletable = 1
        cti_sheetaction.disable = 1

        self.add_me(cti_sheetaction)
        return cti_sheetaction.id
