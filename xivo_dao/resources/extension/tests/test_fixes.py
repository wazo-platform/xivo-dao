# -*- coding: utf-8 -*-
# Copyright 2015-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, equal_to

from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.alchemy.extension import Extension
from xivo_dao.tests.test_dao import DAOTestCase

from xivo_dao.resources.extension.fixes import ExtensionFixes


class TestExtensionFixes(DAOTestCase):

    def setUp(self):
        super(TestExtensionFixes, self).setUp()
        self.fixes = ExtensionFixes(self.session)

    def test_given_extension_associated_to_nothing_then_fixes_pass(self):
        extension = self.add_extension(exten="1000", context="default")
        self.fixes.fix(extension.id)

    def test_given_extension_associated_to_line_then_number_and_context_updated(self):
        line = self.add_line(context="mycontext", number="2000")
        extension = self.add_extension(exten="1000", context="default")
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

        self.fixes.fix(extension.id)

        line = self.session.query(Line).first()
        assert_that(line.number, equal_to('1000'))
        assert_that(line.context, equal_to('default'))

    def test_given_user_has_extension_then_destination_updated(self):
        extension = self.add_extension()
        line = self.add_line()
        user = self.add_user()
        self.add_user_line(user_id=user.id, line_id=line.id)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

        self.fixes.fix(extension.id)

        extension = self.session.query(Extension).first()
        assert_that(extension.type, equal_to('user'))
        assert_that(extension.typeval, equal_to(str(user.id)))

    def test_given_line_has_multiple_users_then_main_extension_updated(self):
        extension = self.add_extension()
        line = self.add_line()
        main_user = self.add_user()
        other_user = self.add_user()
        self.add_line_extension(line_id=line.id, extension_id=extension.id)
        self.add_user_line(user_id=main_user.id, line_id=line.id,
                           main_user=True, main_line=True)
        self.add_user_line(user_id=other_user.id, line_id=line.id,
                           main_user=False, main_line=True)

        self.fixes.fix(extension.id)

        extension = self.session.query(Extension).first()
        assert_that(extension.type, equal_to('user'))
        assert_that(extension.typeval, equal_to(str(main_user.id)))

    def test_given_user_has_multiple_lines_then_all_extensions_updated(self):
        extension1 = self.add_extension(exten='1800')
        extension2 = self.add_extension(exten='1801')
        line1 = self.add_line()
        line2 = self.add_line()
        user = self.add_user()
        self.add_user_line(user_id=user.id, line_id=line1.id,
                           main_user=True, main_line=True)
        self.add_user_line(user_id=user.id, line_id=line2.id,
                           main_user=True, main_line=False)
        self.add_line_extension(line_id=line1.id, extension_id=extension1.id,
                                main_extension=True)
        self.add_line_extension(line_id=line2.id, extension_id=extension2.id,
                                main_extension=True)

        self.fixes.fix(extension1.id)
        self.fixes.fix(extension2.id)

        extension = self.session.query(Extension).filter(Extension.exten == extension1.exten).first()
        assert_that(extension.type, equal_to('user'))
        assert_that(extension.typeval, equal_to(str(user.id)))

        extension = self.session.query(Extension).filter(Extension.exten == extension2.exten).first()
        assert_that(extension.type, equal_to('user'))
        assert_that(extension.typeval, equal_to(str(user.id)))

    def test_given_extension_is_not_associated_to_user_then_destination_reset(self):
        extension = self.add_extension(exten="1000", context="default",
                                       type="user", typeval="1234")

        self.fixes.fix(extension.id)

        extension = self.session.query(Extension).first()
        assert_that(extension.type, equal_to('user'))
        assert_that(extension.typeval, equal_to('0'))

    def test_given_extension_destination_is_other_than_user_or_incall_then_destination_is_unchanged(self):
        extension = self.add_extension(exten="1000", context="default",
                                       type="queue", typeval="1234")

        self.fixes.fix(extension.id)

        extension = self.session.query(Extension).first()
        assert_that(extension.type, equal_to('queue'))
        assert_that(extension.typeval, equal_to('1234'))
