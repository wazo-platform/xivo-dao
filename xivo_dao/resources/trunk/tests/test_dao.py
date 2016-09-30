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

from __future__ import unicode_literals

from hamcrest import (assert_that,
                      contains,
                      contains_inanyorder,
                      equal_to,
                      empty,
                      has_items,
                      has_properties,
                      has_property,
                      is_not,
                      none,
                      not_)


from xivo_dao.alchemy.outcall import Outcall
from xivo_dao.alchemy.outcalltrunk import OutcallTrunk
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures as Trunk
from xivo_dao.alchemy.staticiax import StaticIAX
from xivo_dao.alchemy.staticsip import StaticSIP
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.alchemy.useriax import UserIAX
from xivo_dao.alchemy.usercustom import UserCustom
from xivo_dao.helpers.exception import NotFoundError, InputError
from xivo_dao.resources.trunk import dao as trunk_dao
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase


class TestFind(DAOTestCase):

    def test_find_no_trunk(self):
        result = trunk_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        trunk_row = self.add_trunk()

        trunk = trunk_dao.find(trunk_row.id)

        assert_that(trunk, equal_to(trunk_row))


class TestGet(DAOTestCase):

    def test_get_no_trunk(self):
        self.assertRaises(NotFoundError, trunk_dao.get, 42)

    def test_get(self):
        trunk_row = self.add_trunk()

        trunk = trunk_dao.get(trunk_row.id)

        assert_that(trunk, equal_to(trunk_row))

    def test_endpoint_sip_relationship(self):
        sip_row = self.add_usersip()
        trunk_row = self.add_trunk()
        trunk_row.associate_endpoint(sip_row)

        trunk = trunk_dao.get(trunk_row.id)
        assert_that(trunk, equal_to(trunk_row))
        assert_that(trunk.endpoint_sip, equal_to(sip_row))
        assert_that(trunk.endpoint_iax, none())
        assert_that(trunk.endpoint_custom, none())

    def test_endpoint_iax_relationship(self):
        iax_row = self.add_useriax()
        trunk_row = self.add_trunk()
        trunk_row.associate_endpoint(iax_row)

        trunk = trunk_dao.get(trunk_row.id)
        assert_that(trunk, equal_to(trunk_row))
        assert_that(trunk.endpoint_sip, none())
        assert_that(trunk.endpoint_iax, equal_to(iax_row))
        assert_that(trunk.endpoint_custom, none())

    def test_endpoint_custom_relationship(self):
        custom_row = self.add_usercustom()
        trunk_row = self.add_trunk()
        trunk_row.associate_endpoint(custom_row)

        trunk = trunk_dao.get(trunk_row.id)
        assert_that(trunk, equal_to(trunk_row))
        assert_that(trunk.endpoint_sip, none())
        assert_that(trunk.endpoint_iax, none())
        assert_that(trunk.endpoint_custom, equal_to(custom_row))


class TestFindBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, trunk_dao.find_by, invalid=42)

    def test_find_by_custom_column(self):
        trunk1 = self.add_trunk(endpoint_id=1)
        self.add_trunk(endpoint_id=2)

        trunk = trunk_dao.find_by(endpoint_id=1)

        assert_that(trunk, equal_to(trunk1))

    def test_find_by_context(self):
        trunk_row = self.add_trunk(context='MyCôntext')

        trunk = trunk_dao.find_by(context='MyCôntext')

        assert_that(trunk, equal_to(trunk_row))
        assert_that(trunk.context, equal_to('MyCôntext'))

    def test_given_trunk_does_not_exist_then_returns_null(self):
        trunk = trunk_dao.find_by(context='42')

        assert_that(trunk, none())


class TestGetBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, trunk_dao.get_by, invalid=42)

    def test_get_by_context(self):
        trunk_row = self.add_trunk(context='MyCôntext')

        trunk = trunk_dao.get_by(context='MyCôntext')

        assert_that(trunk, equal_to(trunk_row))
        assert_that(trunk.context, equal_to('MyCôntext'))

    def test_given_trunk_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, trunk_dao.get_by, context='42')


class TestFindAllBy(DAOTestCase):

    def test_find_all_by_no_trunk(self):
        result = trunk_dao.find_all_by(context='toto')

        assert_that(result, contains())

    def test_find_all_by_native_column(self):
        trunk1 = self.add_trunk(context='MyCôntext')
        trunk2 = self.add_trunk(context='MyCôntext')

        trunks = trunk_dao.find_all_by(context='MyCôntext')

        assert_that(trunks, has_items(has_property('id', trunk1.id),
                                      has_property('id', trunk2.id)))


class TestSearch(DAOTestCase):

    def assert_search_returns_result(self, search_result, **parameters):
        result = trunk_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_given_no_trunk_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_trunk_then_returns_one_result(self):
        trunk = self.add_trunk()
        expected = SearchResult(1, [trunk])

        self.assert_search_returns_result(expected)


class TestSearchGivenMultipleTrunks(TestSearch):

    def setUp(self):
        super(TestSearch, self).setUp()
        self.trunk1 = self.add_trunk(context='Ashton', description='resto')
        self.trunk2 = self.add_trunk(context='Beaugarton', description='bar')
        self.trunk3 = self.add_trunk(context='Casa', description='resto')
        self.trunk4 = self.add_trunk(context='Dunkin', description='resto')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.trunk2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.trunk1])
        self.assert_search_returns_result(expected_resto, search='ton', description='resto')

        expected_bar = SearchResult(1, [self.trunk2])
        self.assert_search_returns_result(expected_bar, search='ton', description='bar')

        expected_all_resto = SearchResult(3, [self.trunk1, self.trunk3, self.trunk4])
        self.assert_search_returns_result(expected_all_resto, description='resto', order='context')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4,
                                [self.trunk1,
                                 self.trunk2,
                                 self.trunk3,
                                 self.trunk4])

        self.assert_search_returns_result(expected, order='context')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(4, [self.trunk4,
                                    self.trunk3,
                                    self.trunk2,
                                    self.trunk1])

        self.assert_search_returns_result(expected, order='context', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.trunk1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_skipping_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.trunk2, self.trunk3, self.trunk4])

        self.assert_search_returns_result(expected, skip=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.trunk2])

        self.assert_search_returns_result(expected,
                                          search='a',
                                          order='context',
                                          direction='desc',
                                          skip=1,
                                          limit=1)


class TestCreate(DAOTestCase):

    def test_create_minimal_fields(self):
        trunk = Trunk()
        created_trunk = trunk_dao.create(trunk)

        row = self.session.query(Trunk).first()

        assert_that(created_trunk, equal_to(row))
        assert_that(created_trunk, has_properties(id=is_not(none()),
                                                  context=none(),
                                                  protocol=none(),
                                                  protocolid=none(),
                                                  registerid=0,
                                                  registercommented=0,
                                                  description=none()))

    def test_create_with_all_fields(self):
        trunk = Trunk(context='default',
                      protocol='sip',
                      protocolid=1,
                      registerid=1,
                      registercommented=1,
                      description='description')

        created_trunk = trunk_dao.create(trunk)

        row = self.session.query(Trunk).first()

        assert_that(created_trunk, equal_to(row))
        assert_that(created_trunk, has_properties(id=is_not(none()),
                                                  context='default',
                                                  protocol='sip',
                                                  protocolid=1,
                                                  registerid=1,
                                                  registercommented=1,
                                                  description='description'))


class TestEdit(DAOTestCase):

    def test_edit_all_fields(self):
        sip = self.add_usersip()
        trunk = trunk_dao.create(Trunk(context='default',
                                       registerid=1,
                                       registercommented=1,
                                       description='description'))
        trunk.associate_endpoint(sip)

        trunk = trunk_dao.get(trunk.id)
        trunk.context = 'other_default'
        trunk.registerid = 0
        trunk.registercommented = 0
        trunk.description = 'other description'

        custom = self.add_usercustom()
        trunk.associate_endpoint(custom)

        trunk_dao.edit(trunk)

        row = self.session.query(Trunk).first()

        assert_that(trunk, equal_to(row))
        assert_that(row, has_properties(context='other_default',
                                        protocol='custom',
                                        protocolid=custom.id,
                                        registerid=0,
                                        registercommented=0,
                                        description='other description'))

    def test_edit_set_fields_to_null(self):
        trunk = trunk_dao.create(Trunk(context='default',
                                       protocol='sip',
                                       protocolid=1,
                                       registerid=1,
                                       registercommented=1,
                                       description='description'))
        trunk = trunk_dao.get(trunk.id)
        trunk.context = None
        trunk.description = None

        trunk_dao.edit(trunk)

        row = self.session.query(Trunk).first()

        assert_that(trunk, equal_to(row))
        assert_that(row, has_properties(context=none(),
                                        description=none()))


class TestDelete(DAOTestCase):

    def test_delete(self):
        trunk = trunk_dao.create(Trunk())

        trunk_dao.delete(trunk)

        row = self.session.query(Trunk).first()
        assert_that(row, none())

    def test_given_trunk_has_sip_endpoint_when_deleting_then_sip_endpoint_deleted(self):
        sip = self.add_usersip()
        trunk = self.add_trunk()
        trunk.associate_endpoint(sip)

        trunk_dao.delete(trunk)

        deleted_sip = self.session.query(UserSIP).first()
        assert_that(deleted_sip, none())

    def test_given_trunk_has_iax_endpoint_when_deleting_then_iax_endpoint_deleted(self):
        iax = self.add_useriax()
        trunk = self.add_trunk()
        trunk.associate_endpoint(iax)

        trunk_dao.delete(trunk)

        deleted_sccp = self.session.query(UserIAX).first()
        assert_that(deleted_sccp, none())

    def test_given_trunk_has_custom_endpoint_when_deleting_then_custom_endpoint_deleted(self):
        custom = self.add_usercustom()
        trunk = self.add_trunk()
        trunk.associate_endpoint(custom)

        trunk_dao.delete(trunk)

        deleted_custom = self.session.query(UserCustom).first()
        assert_that(deleted_custom, none())

    def test_given_trunk_has_sip_register_when_deleting_then_sip_register_deleted(self):
        sip = self.add_usersip()
        register = self.add_sip_general_settings(var_name='register')
        trunk = self.add_trunk(registerid=register.id)
        trunk.associate_endpoint(sip)

        trunk_dao.delete(trunk)

        deleted_register = self.session.query(StaticSIP).filter(StaticSIP.id == trunk.registerid).first()
        assert_that(deleted_register, none())

    def test_given_trunk_has_iax_register_when_deleting_then_iax_register_deleted(self):
        iax = self.add_useriax()
        register = self.add_iax_general_settings(var_name='register')
        trunk = self.add_trunk(registerid=register.id)
        trunk.associate_endpoint(iax)

        trunk_dao.delete(trunk)

        deleted_register = self.session.query(StaticIAX).filter(StaticIAX.id == trunk.registerid).first()
        assert_that(deleted_register, none())


class TestRelations(DAOTestCase):

    def test_outcalls_create(self):
        outcall = Outcall(name='test', context='to-extern')
        trunk_row = self.add_trunk()
        trunk_row.outcalls = [outcall]
        trunk = trunk_dao.get(trunk_row.id)

        assert_that(trunk, equal_to(trunk_row))
        assert_that(trunk.outcalls, contains_inanyorder(outcall))

    def test_outcalls_association(self):
        outcall1_row = self.add_outcall()
        outcall2_row = self.add_outcall()
        outcall3_row = self.add_outcall()
        trunk_row = self.add_trunk()

        trunk_row.outcalls = [outcall1_row, outcall2_row, outcall3_row]
        trunk = trunk_dao.get(trunk_row.id)

        assert_that(trunk, equal_to(trunk_row))
        assert_that(trunk.outcalls, contains_inanyorder(outcall1_row, outcall2_row, outcall3_row))

    def test_outcalls_dissociation(self):
        outcall1_row = self.add_outcall()
        outcall2_row = self.add_outcall()
        outcall3_row = self.add_outcall()
        trunk_row = self.add_trunk()

        trunk_row.outcalls = [outcall1_row, outcall2_row, outcall3_row]
        trunk = trunk_dao.get(trunk_row.id)

        assert_that(trunk, equal_to(trunk_row))
        assert_that(trunk.outcalls, not_(empty()))

        trunk_row.outcalls = []
        trunk = trunk_dao.get(trunk_row.id)

        assert_that(trunk, equal_to(trunk_row))
        assert_that(trunk.outcalls, empty())

        row = self.session.query(Outcall).first()
        assert_that(row, not_(none()))

        row = self.session.query(OutcallTrunk).first()
        assert_that(row, none())
