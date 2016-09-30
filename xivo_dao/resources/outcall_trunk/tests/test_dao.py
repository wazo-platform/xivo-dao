# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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

from hamcrest import (assert_that,
                      empty,
                      equal_to,
                      has_properties,
                      none,
                      has_items,
                      contains)

from xivo_dao.alchemy.outcalltrunk import OutcallTrunk
from xivo_dao.helpers.exception import NotFoundError, InputError
from xivo_dao.resources.outcall_trunk import dao as outcall_trunk_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestFindAllBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, outcall_trunk_dao.find_by, invalid=42)

    def test_find_all_by_when_no_outcall_trunk(self):
        result = outcall_trunk_dao.find_all_by()

        assert_that(result, empty())

    def test_find_all_by(self):
        outcall_trunk = self.add_outcall_trunk()

        result = outcall_trunk_dao.find_all_by(outcall_id=outcall_trunk.outcall_id)
        assert_that(result, contains(outcall_trunk))

        result = outcall_trunk_dao.find_all_by(trunk_id=outcall_trunk.trunk_id)
        assert_that(result, contains(outcall_trunk))

        result = outcall_trunk_dao.find_all_by(outcall_id=outcall_trunk.outcall_id,
                                               trunk_id=outcall_trunk.trunk_id)
        assert_that(result, contains(outcall_trunk))

    def test_find_all_by_outcall_id_two_outcall_trunks_order_by_priority(self):
        outcall = self.add_outcall()
        trunk1 = self.add_trunk()
        trunk2 = self.add_trunk()
        self.add_outcall_trunk(outcall_id=outcall.id,
                               trunk_id=trunk2.id,
                               priority=1)
        self.add_outcall_trunk(outcall_id=outcall.id,
                               trunk_id=trunk1.id,
                               priority=0)

        result = outcall_trunk_dao.find_all_by(outcall_id=outcall.id)

        assert_that(result, contains(
            has_properties({'outcall_id': outcall.id,
                            'trunk_id': trunk1.id}),
            has_properties({'outcall_id': outcall.id,
                            'trunk_id': trunk2.id}),
        ))

    def test_find_all_by_trunk_id_two_outcall_trunks(self):
        trunk = self.add_trunk()
        outcall1 = self.add_outcall()
        outcall2 = self.add_outcall()
        self.add_outcall_trunk(outcall_id=outcall1.id,
                               trunk_id=trunk.id)
        self.add_outcall_trunk(outcall_id=outcall2.id,
                               trunk_id=trunk.id)

        result = outcall_trunk_dao.find_all_by(trunk_id=trunk.id)

        assert_that(result, has_items(
            has_properties({'outcall_id': outcall1.id,
                            'trunk_id': trunk.id}),
            has_properties({'outcall_id': outcall2.id,
                            'trunk_id': trunk.id}),
        ))

    def test_find_all_by_outcall_id_trunk_id_two_outcall_trunks(self):
        trunk = self.add_trunk()
        outcall1 = self.add_outcall()
        outcall2 = self.add_outcall()
        self.add_outcall_trunk(outcall_id=outcall1.id,
                               trunk_id=trunk.id)
        self.add_outcall_trunk(outcall_id=outcall2.id,
                               trunk_id=trunk.id)

        result = outcall_trunk_dao.find_all_by(trunk_id=trunk.id,
                                               outcall_id=outcall1.id)

        assert_that(result, has_items(
            has_properties({'outcall_id': outcall1.id,
                            'trunk_id': trunk.id}),
        ))

    def test_find_all_by_when_endpoint_associated_to_trunk(self):
        trunk = self.add_trunk()
        outcall = self.add_outcall()
        sip = self.add_usersip()
        self.add_outcall_trunk(outcall_id=outcall.id,
                               trunk_id=trunk.id)
        trunk.associate_endpoint(sip)

        result = outcall_trunk_dao.find_all_by(trunk_id=trunk.id)

        assert_that(result, contains(
            has_properties({'outcall_id': outcall.id,
                            'trunk_id': trunk.id}),
        ))


class TestFindBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, outcall_trunk_dao.find_by, invalid=42)

    def test_find_by_when_no_outcall_trunk(self):
        result = outcall_trunk_dao.find_by()

        assert_that(result, equal_to(None))

    def test_find_by(self):
        outcall_trunk = self.add_outcall_trunk()

        result = outcall_trunk_dao.find_by(outcall_id=outcall_trunk.outcall_id)
        assert_that(result, equal_to(outcall_trunk))

        result = outcall_trunk_dao.find_by(trunk_id=outcall_trunk.trunk_id)
        assert_that(result, equal_to(outcall_trunk))

        result = outcall_trunk_dao.find_by(outcall_id=outcall_trunk.outcall_id,
                                           trunk_id=outcall_trunk.trunk_id)
        assert_that(result, equal_to(outcall_trunk))


class TestGetBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, outcall_trunk_dao.get_by, invalid=42)

    def test_given_outcall_trunk_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, outcall_trunk_dao.get_by, outcall_id=1)

    def test_get_by_outcall_id(self):
        outcall_trunk = self.add_outcall_trunk()

        result = outcall_trunk_dao.get_by(outcall_id=outcall_trunk.outcall_id)
        assert_that(result, equal_to(outcall_trunk))


class TestAssociateAllTrunks(DAOTestCase):

    def test_associate_trunks_with_outcall(self):
        outcall = self.add_outcall()
        trunk1 = self.add_trunk()
        trunk2 = self.add_trunk()
        trunk3 = self.add_trunk()

        trunks = [trunk3, trunk1, trunk2]
        result = outcall_trunk_dao.associate_all_trunks(outcall, trunks)

        assert_that(result, contains(has_properties({'outcall_id': outcall.id,
                                                     'trunk_id': trunk3.id}),
                                     has_properties({'outcall_id': outcall.id,
                                                     'trunk_id': trunk1.id}),
                                     has_properties({'outcall_id': outcall.id,
                                                     'trunk_id': trunk2.id})))


class TestDissociateAllByOutcall(DAOTestCase):

    def test_dissociate_all_by_outcall(self):
        outcall = self.add_outcall()
        trunk1 = self.add_trunk()
        trunk2 = self.add_trunk()
        trunk3 = self.add_trunk()
        trunks = [trunk1, trunk2, trunk3]
        outcall_trunk_dao.associate_all_trunks(outcall, trunks)

        outcall_trunk_dao.dissociate_all_by_outcall(outcall)

        result = (self.session.query(OutcallTrunk)
                  .filter(OutcallTrunk.outcall_id == outcall.id)
                  .first())

        assert_that(result, none())
