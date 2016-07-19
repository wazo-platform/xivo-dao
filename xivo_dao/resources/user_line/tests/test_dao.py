# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
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

from hamcrest import assert_that, equal_to, has_property, instance_of, all_of, none, has_items, contains_inanyorder, contains, is_not, has_length

from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.resources.user_line import dao as user_line_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestUserLineFindMainByUserId(DAOTestCase):

    def test_given_user_is_not_main_then_returns_null(self):
        user = self.add_user()
        line = self.add_line()
        self.add_user_line(user_id=user.id, line_id=line.id, main_user=False, main_line=True)

        result = user_line_dao.find_main_by_user_id(user.id)
        assert_that(result, none())

    def test_given_line_is_not_main_then_returns_null(self):
        user = self.add_user()
        line = self.add_line()
        self.add_user_line(user_id=user.id, line_id=line.id, main_user=True, main_line=False)

        result = user_line_dao.find_main_by_user_id(user.id)
        assert_that(result, none())

    def test_given_user_and_line_are_main_then_returns_user_line(self):
        user = self.add_user()
        line = self.add_line()
        self.add_user_line(user_id=user.id, line_id=line.id, main_user=True, main_line=True)

        result = user_line_dao.find_main_by_user_id(user.id)

        assert_that(result.user_id, equal_to(user.id))
        assert_that(result.line_id, equal_to(line.id))

    def test_given_multiple_users_associated_then_returns_main_user(self):
        main_user = self.add_user()
        other_user = self.add_user()
        line = self.add_line()
        self.add_user_line(user_id=main_user.id, line_id=line.id,
                           main_user=True, main_line=True)
        self.add_user_line(user_id=other_user.id, line_id=line.id,
                           main_user=False, main_line=True)

        result = user_line_dao.find_main_by_user_id(main_user.id)

        assert_that(result.user_id, equal_to(main_user.id))
        assert_that(result.line_id, equal_to(line.id))


class TestUserLineFindAllByUserId(DAOTestCase):

    def test_find_all_by_user_id_no_user_line(self):
        expected_result = []
        result = user_line_dao.find_all_by_user_id(1)

        assert_that(result, equal_to(expected_result))

    def test_find_all_by_user_id(self):
        user_line = self.add_user_line_without_exten()

        result = user_line_dao.find_all_by_user_id(user_line.user_id)

        assert_that(result, has_items(
            all_of(
                has_property('user_id', user_line.user_id),
                has_property('line_id', user_line.line_id))
        ))

    def test_find_all_by_user_id_two_users(self):
        user = self.add_user()
        line1 = self.add_line()
        line2 = self.add_line()
        self.add_user_line(user_id=user.id,
                           line_id=line1.id,
                           main_user=True,
                           main_line=True)
        self.add_user_line(user_id=user.id,
                           line_id=line2.id,
                           main_user=True,
                           main_line=False)

        result = user_line_dao.find_all_by_user_id(user.id)

        assert_that(result, has_items(
            all_of(
                has_property('user_id', user.id),
                has_property('line_id', line2.id)),
            all_of(
                has_property('user_id', user.id),
                has_property('line_id', line1.id))
        ))


class TestUserLineFindMainUserLine(DAOTestCase):

    def test_find_main_user_line_no_user(self):
        line_id = 33

        result = user_line_dao.find_main_user_line(line_id)

        assert_that(result, equal_to(None))

    def test_find_main_user_line_no_line(self):
        self.add_user()
        line_id = 2

        result = user_line_dao.find_main_user_line(line_id)

        assert_that(result, equal_to(None))

    def test_find_main_user_line_one_user(self):
        user_line = self.add_user_line_without_exten()

        result = user_line_dao.find_main_user_line(user_line.line_id)

        assert_that(result.user_id, equal_to(user_line.user_id))

    def test_find_main_user_line_one_line_no_user(self):
        user_line = self.add_user_line_without_user()

        result = user_line_dao.find_main_user_line(user_line.line_id)

        assert_that(result, none())

    def test_find_main_user_line(self):
        user1 = self.add_user()
        user2 = self.add_user()
        line = self.add_line()
        main_user_line = self.add_user_line(user_id=user1.id,
                                            line_id=line.id,
                                            main_user=True,
                                            main_line=True)
        self.add_user_line(user_id=user2.id,
                           line_id=line.id,
                           main_user=False,
                           main_line=True)

        result = user_line_dao.find_main_user_line(line.id)

        assert_that(result, instance_of(UserLine))
        assert_that(result,
                    has_property('user_id', main_user_line.user_id),
                    has_property('line_id', main_user_line.line_id)
                    )


class TestAssociateUserLine(DAOTestCase):

    def test_associate_user_with_line(self):
        user = self.add_user()
        line = self.add_line()

        result = user_line_dao.associate(user, line)

        assert_that(result.user_id, equal_to(user.id))
        assert_that(result.line_id, equal_to(line.id))
        assert_that(result.extension_id, none())
        assert_that(result.main_user, equal_to(True))
        assert_that(result.main_line, equal_to(True))

    def test_associate_main_user_with_line(self):
        main_user = self.add_user()
        line = self.add_line()

        result = user_line_dao.associate(main_user, line)

        assert_that(result.user_id, equal_to(main_user.id))
        assert_that(result.line_id, equal_to(line.id))
        assert_that(result.extension_id, none())
        assert_that(result.main_user, equal_to(True))
        assert_that(result.main_line, equal_to(True))

    def test_associate_secondary_user_with_line(self):
        main_user = self.add_user()
        secondary_user = self.add_user()
        line = self.add_line()

        self.add_user_line(user_id=main_user.id,
                           line_id=line.id,
                           extension_id=None,
                           main_user=True,
                           main_line=True)

        user_line_dao.associate(secondary_user, line)

        result = (self.session.query(UserLine)
                  .filter(UserLine.line_id == line.id)
                  .all())

        assert_that(result, contains_inanyorder(
            all_of(has_property('user_id', main_user.id),
                   has_property('line_id', line.id),
                   has_property('extension_id', None),
                   has_property('main_user', True),
                   has_property('main_line', True)),
            all_of(has_property('user_id', secondary_user.id),
                   has_property('line_id', line.id),
                   has_property('extension_id', None),
                   has_property('main_user', False),
                   has_property('main_line', True))))

    def test_associate_main_user_with_line_and_extension(self):
        user = self.add_user()
        line = self.add_line()
        extension = self.add_extension()
        self.add_user_line(line_id=line.id, extension_id=extension.id)

        result = user_line_dao.associate(user, line)

        assert_that(result, all_of(
            has_property('user_id', user.id),
            has_property('line_id', line.id),
            has_property('extension_id', extension.id),
            has_property('main_user', True),
            has_property('main_line', True)))

    def test_associate_secondary_user_with_line_and_extension(self):
        main_user = self.add_user()
        secondary_user = self.add_user()
        line = self.add_line()
        extension = self.add_extension()

        main_user_line_row = self.add_user_line(user_id=main_user.id,
                                                line_id=line.id,
                                                extension_id=extension.id,
                                                main_user=True,
                                                main_line=True)

        user_line_dao.associate(secondary_user, line)

        main_row = (self.session.query(UserLine)
                    .filter(UserLine.id == main_user_line_row.id)
                    .first())

        secondary_row = (self.session.query(UserLine)
                         .filter(UserLine.line_id == line.id)
                         .filter(UserLine.user_id == secondary_user.id)
                         .first())

        assert_that(main_row, all_of(
            has_property('user_id', main_user.id),
            has_property('line_id', line.id),
            has_property('extension_id', extension.id),
            has_property('main_user', True),
            has_property('main_line', True)))

        assert_that(secondary_row, all_of(
            has_property('user_id', secondary_user.id),
            has_property('line_id', line.id),
            has_property('extension_id', extension.id),
            has_property('main_user', False),
            has_property('main_line', True)))


class TestDissociateUserLine(DAOTestCase):

    def test_dissociate_user_line_with_queue_member(self):
        user_line = self.add_user_line_with_queue_member()

        user_line_dao.dissociate(user_line.user, user_line.line)

        result = (self.session.query(QueueMember)
                  .filter(QueueMember.usertype == 'user')
                  .filter(QueueMember.userid == user_line.user_id)
                  .first())

        assert_that(result, none())

    def test_dissociate_main_user_line_without_exten(self):
        user_line = self.add_user_line_without_exten()

        user_line_dao.dissociate(user_line.user, user_line.line)

        result = (self.session.query(UserLine)
                  .filter(UserLine.id == user_line.id)
                  .first())

        assert_that(result, none())

    def test_dissociate_main_user_line_with_exten(self):
        user_line = self.add_user_line_with_exten()

        user_line_dao.dissociate(user_line.user, user_line.line)

        result = (self.session.query(UserLine)
                  .filter(UserLine.id == user_line.id)
                  .first())

        assert_that(result.user_id, none())

    def test_dissociate_secondary_user_line(self):
        main_user_line = self.add_user_line_with_exten()
        secondary_user_line = self.prepare_secondary_user_line(main_user_line)

        user_line_dao.dissociate(secondary_user_line.userfeatures, secondary_user_line.linefeatures)

        self.assert_user_line_associated(main_user_line)
        self.assert_user_line_deleted(secondary_user_line)

    def prepare_secondary_user_line(self, main_user_line):
        user_row = self.add_user()
        return self.add_user_line(user_id=user_row.id,
                                  line_id=main_user_line.line_id,
                                  extension_id=main_user_line.extension_id,
                                  main_user=False,
                                  main_line=True)

    def test_dissociate_user_secondary_line(self):
        user_main_line = self.add_user_line_with_exten()
        user_secondary_line = self.prepare_user_secondary_line(user_main_line)

        user_line_dao.dissociate(user_secondary_line.userfeatures, user_secondary_line.linefeatures)

        self.assert_user_line_associated(user_main_line, main_line=True)
        self.assert_user_line_deleted(user_secondary_line)

    def test_dissociate_user_main_line_when_has_secondary_line(self):
        user_main_line = self.add_user_line_with_exten()
        user_secondary_line = self.prepare_user_secondary_line(user_main_line)

        user_line_dao.dissociate(user_main_line.userfeatures, user_main_line.linefeatures)

        self.assert_user_line_associated(user_secondary_line, main_line=True)
        self.assert_user_line_deleted(user_main_line)

    def prepare_user_secondary_line(self, user_main_line):
        line = self.add_line()
        return self.add_user_line(user_id=user_main_line.user_id,
                                  line_id=line.id,
                                  extension_id=user_main_line.extension_id,
                                  main_user=True,
                                  main_line=False)

    def assert_user_line_associated(self, user_line, main_line=True):
        row = (self.session.query(UserLine)
               .filter(UserLine.user_id == user_line.user_id)
               .filter(UserLine.line_id == user_line.line_id)
               .filter(UserLine.main_line == main_line)
               .first())

        assert_that(row, is_not(none()))

    def assert_user_line_deleted(self, user_line):
        if user_line.user_id is not None:
            row = (self.session.query(UserLine)
                   .filter(UserLine.user_id == user_line.user_id)
                   .filter(UserLine.line_id == user_line.line_id)
                   .first())

            assert_that(row, none())


class TestUserLineFindAllByLineId(DAOTestCase):

    def test_find_all_by_line_id_no_user_line(self):
        result = user_line_dao.find_all_by_line_id(1)

        assert_that(result, has_length(0))

    def test_find_all_by_line_id_one_user_line_with_exten(self):
        user_line = self.add_user_line_with_exten()

        result = user_line_dao.find_all_by_line_id(user_line.line_id)

        assert_that(result, contains(user_line))

    def test_find_all_by_line_id_one_user_line_without_exten(self):
        user_line = self.add_user_line_without_exten()

        result = user_line_dao.find_all_by_line_id(user_line.line_id)

        assert_that(result, contains(user_line))

    def test_find_all_by_line_id_two_user_lines(self):
        user_line_1 = self.add_user_line_with_exten()
        user_row = self.add_user()
        user_line_2 = self.add_user_line(user_id=user_row.id,
                                         line_id=user_line_1.line_id,
                                         main_user=False,
                                         main_line=True)

        result = user_line_dao.find_all_by_line_id(user_line_1.line_id)

        assert_that(result, contains_inanyorder(user_line_1, user_line_2))

    def test_find_all_by_line_id_with_line_no_user(self):
        user_line_row = self.add_user_line_without_user()

        result = user_line_dao.find_all_by_line_id(user_line_row.line_id)

        assert_that(result, contains())
