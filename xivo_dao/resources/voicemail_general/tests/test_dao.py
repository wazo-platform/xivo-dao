# Copyright 2017-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from hamcrest import (
    assert_that,
    contains_exactly,
    contains_inanyorder,
    empty,
    equal_to,
)

from xivo_dao.alchemy.staticvoicemail import StaticVoicemail
from xivo_dao.tests.test_dao import DAOTestCase
from .. import dao as voicemail_general_dao


class TestFindAll(DAOTestCase):

    def test_find_all_no_voicemail_general(self):
        result = voicemail_general_dao.find_all()

        assert_that(result, empty())

    def test_find_all(self):
        row1 = self.add_voicemail_general_settings(var_metric=3)
        row2 = self.add_voicemail_general_settings(var_metric=2)
        row3 = self.add_voicemail_general_settings(var_metric=1)
        row4 = self.add_voicemail_general_settings(var_metric=4)

        voicemail_general = voicemail_general_dao.find_all()

        assert_that(voicemail_general, contains_exactly(row3, row2, row1, row4))

    def test_find_all_do_not_find_register(self):
        self.add_voicemail_general_settings(category='zonemessages')
        row2 = self.add_voicemail_general_settings()

        voicemail_general = voicemail_general_dao.find_all()

        assert_that(voicemail_general, contains_exactly(row2))

    def test_find_all_do_not_find_var_val_none(self):
        self.add_voicemail_general_settings(var_metric=1,
                                            var_name='setting1',
                                            var_val=None)
        row2 = self.add_voicemail_general_settings(var_metric=2,
                                                   var_name='setting1',
                                                   var_val='value1')

        voicemail_general = voicemail_general_dao.find_all()

        assert_that(voicemail_general, contains_exactly(row2))


class TestEditAll(DAOTestCase):

    def test_edit_all(self):
        row1 = StaticVoicemail(var_name='setting1', var_val='value1')
        row2 = StaticVoicemail(var_name='setting2', var_val='value1')
        row3 = StaticVoicemail(var_name='setting3', var_val='value1')
        row4 = StaticVoicemail(var_name='setting2', var_val='value2')

        voicemail_general_dao.edit_all([row1, row2, row3, row4])

        voicemail_general = voicemail_general_dao.find_all()
        assert_that(voicemail_general, contains_inanyorder(row1, row2, row3, row4))

    def test_edit_all_do_not_delete_register(self):
        row1 = self.add_voicemail_general_settings(category='zonemessages')
        row2 = StaticVoicemail(var_name='nat', var_val='value1')

        voicemail_general_dao.edit_all([row2])

        assert_that(self.session.query(StaticVoicemail)
                    .filter(StaticVoicemail.category == 'zonemessages')
                    .first(), equal_to(row1))

    def test_delete_old_entries(self):
        self.add_voicemail_general_settings()
        self.add_voicemail_general_settings()
        row = StaticVoicemail(var_name='nat', var_val='value1')

        voicemail_general_dao.edit_all([row])

        voicemail_general = voicemail_general_dao.find_all()
        assert_that(voicemail_general, contains_exactly(row))
