# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

from hamcrest import (
    assert_that,
    contains,
    equal_to,
    has_items,
    has_properties,
    none,
    not_,
)

from xivo_dao.alchemy.asterisk_file import AsteriskFile
from xivo_dao.alchemy.asterisk_file_variable import AsteriskFileVariable
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as asterisk_file_dao


class TestFindBy(DAOTestCase):

    def test_find_by_no_asterisk_file(self):
        result = asterisk_file_dao.find_by()

        assert_that(result, none())

    def test_find_by(self):
        asterisk_file = self.add_asterisk_file(name='confbridge.conf')

        result = asterisk_file_dao.find_by(name='confbridge.conf')

        assert_that(result, equal_to(asterisk_file))


class TestEdit(DAOTestCase):

    def test_edit(self):
        row = self.add_asterisk_file(name='confbridge.conf')
        row.name = 'confbridge2.conf'

        asterisk_file_dao.edit(row)

        result = self.session.query(AsteriskFile).first()
        assert_that(result, equal_to(row))
        assert_that(result, has_properties(name='confbridge2.conf'))


class TestEditSectionVariables(DAOTestCase):

    def test_edit(self):
        file_ = self.add_asterisk_file()
        section = self.add_asterisk_file_section(asterisk_file_id=file_.id)
        old_variable = self.add_asterisk_file_variable(asterisk_file_section_id=section.id)
        variable = AsteriskFileVariable(key='key', value='value', asterisk_file_section_id=section.id)

        asterisk_file_dao.edit_section_variables(section, [variable])

        results = self.session.query(AsteriskFileVariable).all()
        assert_that(results, contains(variable))
        assert_that(results, not_(has_items(old_variable)))
