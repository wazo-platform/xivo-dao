# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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


from hamcrest import assert_that, equal_to
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.data_handler.entity import dao


class TestDefaultEntityName(DAOTestCase):
    def test_given_entity_then_return_entity_name(self):
        entity_name = 'entity'
        self.add_entity(name=entity_name)

        result = dao.default_entity_name()

        assert_that(result, equal_to(entity_name))


class TestDefaultEntityID(DAOTestCase):
    def test_given_entity_then_return_entity_id(self):
        entity = self.add_entity()

        result = dao.default_entity_id()

        assert_that(result, equal_to(entity.id))
