# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (
    assert_that,
    contains,
    equal_to,
    none,
)

from xivo_dao.tests.test_dao import DAOTestCase

from ..asterisk_file_section import AsteriskFileSection
from ..asterisk_file_variable import AsteriskFileVariable


class TestVariables(DAOTestCase):

    def test_getter(self):
        file_ = self.add_asterisk_file()
        file_section = self.add_asterisk_file_section(asterisk_file_id=file_.id)
        file_variable1 = self.add_asterisk_file_variable(priority=2, asterisk_file_section_id=file_section.id)
        file_variable2 = self.add_asterisk_file_variable(priority=1, asterisk_file_section_id=file_section.id)
        file_variable3 = self.add_asterisk_file_variable(priority=None, asterisk_file_section_id=file_section.id)
        file_variable4 = self.add_asterisk_file_variable(priority=None, asterisk_file_section_id=file_section.id)

        result = self.session.query(AsteriskFileSection).filter_by(id=file_section.id).first()

        assert_that(result, equal_to(file_section))
        assert_that(result.variables, contains(
            file_variable2,
            file_variable1,
            file_variable3,
            file_variable4,
        ))

    def test_setter(self):
        file_ = self.add_asterisk_file()
        file_section = self.add_asterisk_file_section(asterisk_file_id=file_.id)

        file_section.variables.append(AsteriskFileVariable(key='allow'))

        result = self.session.query(AsteriskFileVariable).first()
        assert_that(result, equal_to(file_section.variables[0]))
        assert_that(result.priority, none())

    def test_deleter(self):
        file_ = self.add_asterisk_file()
        file_section = self.add_asterisk_file_section(asterisk_file_id=file_.id)
        self.add_asterisk_file_variable(asterisk_file_section_id=file_section.id)

        file_section.variables = []

        result = self.session.query(AsteriskFileVariable).first()
        assert_that(result, none())


class TestDelete(DAOTestCase):

    def test_variables_are_deleted(self):
        file_ = self.add_asterisk_file()
        file_section = self.add_asterisk_file_section(asterisk_file_id=file_.id)
        self.add_asterisk_file_variable(asterisk_file_section_id=file_section.id)

        self.session.delete(file_section)

        result = self.session.query(AsteriskFileVariable).first()
        assert_that(result, none())
