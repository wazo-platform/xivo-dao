# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from hamcrest import (
    assert_that,
    contains,
    contains_inanyorder,
    empty,
    has_properties,
)

from xivo_dao.alchemy.staticvoicemail import StaticVoicemail
from xivo_dao.resources.voicemail_zonemessages import dao as voicemail_zonemessages_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestFindAll(DAOTestCase):

    def test_find_all_no_voicemail_zonemessages(self):
        result = voicemail_zonemessages_dao.find_all()

        assert_that(result, empty())

    def test_find_all(self):
        row1 = self.add_voicemail_zonemessages_settings(var_name='setting1',
                                                        var_val='value1')
        row2 = self.add_voicemail_zonemessages_settings(var_name='setting2',
                                                        var_val='value1')
        row3 = self.add_voicemail_zonemessages_settings(var_name='setting3',
                                                        var_val='value1')
        row4 = self.add_voicemail_zonemessages_settings(var_name='setting2',
                                                        var_val='value2')

        voicemail_zonemessages = voicemail_zonemessages_dao.find_all()

        assert_that(voicemail_zonemessages, contains_inanyorder(row3, row2, row1, row4))

    def test_find_all_do_not_find_voicemail_general(self):
        self.add_voicemail_general_settings(var_name='setting1',
                                            var_val='value1')
        row2 = self.add_voicemail_zonemessages_settings(var_name='setting2',
                                                        var_val='value2')

        voicemail_zonemessages = voicemail_zonemessages_dao.find_all()

        assert_that(voicemail_zonemessages, contains(row2))

    def test_find_all_do_not_find_var_val_none(self):
        self.add_voicemail_zonemessages_settings(var_name='setting1',
                                                 var_val=None)
        row2 = self.add_voicemail_zonemessages_settings(var_name='setting1',
                                                        var_val='value1')

        voicemail_zonemessages = voicemail_zonemessages_dao.find_all()

        assert_that(voicemail_zonemessages, contains(row2))


class TestEditAll(DAOTestCase):

    def test_edit_all(self):
        row1 = StaticVoicemail(var_name='setting1', var_val='value1')
        row2 = StaticVoicemail(var_name='setting2', var_val='value1')
        row3 = StaticVoicemail(var_name='setting3', var_val='value1')
        row4 = StaticVoicemail(var_name='setting2', var_val='value2')

        voicemail_zonemessages_dao.edit_all([row3, row4, row2, row1])

        voicemail_zonemessages = voicemail_zonemessages_dao.find_all()
        assert_that(voicemail_zonemessages, contains_inanyorder(row3, row4, row2, row1))

    def test_default_values(self):
        row = StaticVoicemail(var_name='setting', var_val='value')

        voicemail_zonemessages_dao.edit_all([row])

        voicemail_zonemessages = voicemail_zonemessages_dao.find_all()
        assert_that(voicemail_zonemessages, contains_inanyorder(
            has_properties(cat_metric=1,
                           filename='voicemail.conf',
                           category='zonemessages')
        ))
