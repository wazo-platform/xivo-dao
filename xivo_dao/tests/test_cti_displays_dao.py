# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, equal_to
from xivo_dao import cti_displays_dao
from xivo_dao.alchemy.cti_contexts import CtiContexts
from xivo_dao.alchemy.cti_displays import CtiDisplays
from xivo_dao.tests.test_dao import DAOTestCase


class TestCTIDisplaysDAO(DAOTestCase):

    def setUp(self):
        super(TestCTIDisplaysDAO, self).setUp()
        display_configs = [
            ('switchboard', '{ "10": [ "", "status", "", ""],"20": [ "Name", "name", "", "{db-firstname} {db-lastname}"],"30": [ "Number", "number_office", "", "{db-phone}"]}'),
            ('Display', '{ "10": [ "Firstname", "", "", "{db-firstname}"],"20": [ "Lastname", "", "", "{db-lastname}"],"30": [ "Number", "", "", "{db-number}"] }'),
        ]
        for config in display_configs:
            display = CtiDisplays(
                name=config[0],
                data=config[1],
            )
            self.add_me(display)

    def test_get_config(self):
        result = cti_displays_dao.get_config()

        expected = {'switchboard': {'10': ['', 'status', '', ''],
                                    '20': ['Name', 'name', '', '{db-firstname} {db-lastname}'],
                                    '30': ['Number', 'number_office', '', '{db-phone}']},
                    'Display': {'10': ['Firstname', '', '', '{db-firstname}'],
                                '20': ['Lastname', '', '', '{db-lastname}'],
                                '30': ['Number', '', '', '{db-number}']}}

        assert_that(result, equal_to(expected))

    def test_get_profile_configuration(self):
        self.add_directory(name='xivodir', dirtype='xivo')
        self.add_directory(name='garbage', dirtype='phonebook')
        self.add_directory(name='csvws', dirtype='csv')
        profile_configs = [
            ('__switchboard_directory', 'xivodir,garbage', 'switchboard'),
            ('default', 'ldapone,csvws', 'Display'),
        ]
        for config in profile_configs:
            cti_config = CtiContexts(
                name=config[0],
                directories=config[1],
                display=config[2],
            )
            self.add_me(cti_config)

        result = cti_displays_dao.get_profile_configuration()

        expected = {'__switchboard_directory': {'display': 'switchboard',
                                                'sources': ['xivodir', 'garbage'],
                                                'types': ['xivo', 'phonebook']},
                    'default': {'display': 'Display',
                                'sources': ['ldapone', 'csvws'],
                                'types': ['ldap', 'csv']}}

        assert_that(result, equal_to(expected))

    def test_get_profile_association_invalid_display(self):
        self.add_directory(name='xivodir', dirtype='xivo')
        self.add_directory(name='garbage', dirtype='phonebook')
        profile_configs = [
            ('__switchboard_directory', 'xivodir,garbage', 'switchboard'),
            ('default', 'ldapone,csvws', 'NOT'),
        ]
        for config in profile_configs:
            cti_config = CtiContexts(
                name=config[0],
                directories=config[1],
                display=config[2],
            )
            self.add_me(cti_config)

        result = cti_displays_dao.get_profile_configuration()

        expected = {'__switchboard_directory': {'display': 'switchboard',
                                                'sources': ['xivodir', 'garbage'],
                                                'types': ['xivo', 'phonebook']}}

        assert_that(result, equal_to(expected))

    def test_get_profile_association_no_selection(self):
        profile_configs = [
            ('__switchboard_directory', '', 'switchboard'),
            ('default', 'ldapone,csvws', 'NOT'),
        ]
        for config in profile_configs:
            cti_config = CtiContexts(
                name=config[0],
                directories=config[1],
                display=config[2],
            )
            self.add_me(cti_config)

        result = cti_displays_dao.get_profile_configuration()

        expected = {'__switchboard_directory': {'display': 'switchboard',
                                                'sources': [],
                                                'types': []}}

        assert_that(result, equal_to(expected))
