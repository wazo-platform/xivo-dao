# Copyright 2017-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains,
    equal_to,
    has_entries,
    none,
)

from xivo_dao.tests.test_dao import DAOTestCase

from ..asterisk_file import AsteriskFile
from ..asterisk_file_section import AsteriskFileSection


class TestSectionsOrdered(DAOTestCase):

    def test_getter(self):
        file_ = self.add_asterisk_file()
        file_section1 = self.add_asterisk_file_section(priority=5, asterisk_file_id=file_.id)
        file_section2 = self.add_asterisk_file_section(priority=0, asterisk_file_id=file_.id)
        file_section3 = self.add_asterisk_file_section(priority=None, asterisk_file_id=file_.id)
        file_section4 = self.add_asterisk_file_section(priority=None, asterisk_file_id=file_.id)

        result = self.session.query(AsteriskFile).filter_by(id=file_.id).first()

        assert_that(result, equal_to(file_))
        assert_that(result.sections_ordered, contains(
            file_section2,
            file_section1,
            file_section3,
            file_section4
        ))


class TestSections(DAOTestCase):

    def test_getter(self):
        file_ = self.add_asterisk_file()
        file_section1 = self.add_asterisk_file_section(name='default', priority=5, asterisk_file_id=file_.id)
        file_section2 = self.add_asterisk_file_section(name='general', priority=0, asterisk_file_id=file_.id)
        file_section3 = self.add_asterisk_file_section(name='conf1', priority=None, asterisk_file_id=file_.id)
        file_section4 = self.add_asterisk_file_section(name='conf2', priority=None, asterisk_file_id=file_.id)

        result = self.session.query(AsteriskFile).filter_by(id=file_.id).first()

        assert_that(result, equal_to(file_))
        assert_that(result.sections, has_entries(
            default=file_section1,
            general=file_section2,
            conf1=file_section3,
            conf2=file_section4,
        ))

    def test_setter(self):
        file_ = self.add_asterisk_file()

        file_.sections['default'] = AsteriskFileSection(name='default')

        result = self.session.query(AsteriskFileSection).first()
        assert_that(result, equal_to(file_.sections['default']))

    def test_deleter(self):
        file_ = self.add_asterisk_file()
        self.add_asterisk_file_section(asterisk_file_id=file_.id)

        file_.sections = {}

        result = self.session.query(AsteriskFileSection).first()
        assert_that(result, none())


class TestDelete(DAOTestCase):

    def test_sections_are_deleted(self):
        file_ = self.add_asterisk_file()
        self.add_asterisk_file_section(asterisk_file_id=file_.id)

        self.session.delete(file_)

        result = self.session.query(AsteriskFileSection).first()
        assert_that(result, none())
