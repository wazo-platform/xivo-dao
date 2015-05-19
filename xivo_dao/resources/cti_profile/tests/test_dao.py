# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from hamcrest import assert_that, equal_to, has_length

from xivo_dao.alchemy.cti_profile import CtiProfile as CtiProfileSchema
from xivo_dao.resources.cti_profile import dao
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.tests.test_dao import DAOTestCase


class TestCtiProfile(DAOTestCase):

    def test_find_all(self):
        profile_row1 = CtiProfileSchema(id=1, name='Profil 01')
        profile_row2 = CtiProfileSchema(id=2, name='Profil 02')
        self.add_me(profile_row1)
        self.add_me(profile_row2)

        result = dao.find_all()

        assert_that(result, has_length(2))
        assert_that(result[0].id, equal_to(1))
        assert_that(result[0].name, equal_to('Profil 01'))
        assert_that(result[1].id, equal_to(2))
        assert_that(result[1].name, equal_to('Profil 02'))

    def test_get(self):
        profile_row = CtiProfileSchema(id=1, name='Profil 01')
        self.add_me(profile_row)

        result = dao.get(1)

        assert_that(result.id, equal_to(1))
        assert_that(result.name, equal_to('Profil 01'))

    def test_get_unknown_user(self):
        self.assertRaises(NotFoundError, dao.get, 1)

    def test_get_id_by_name(self):
        profile_row1 = CtiProfileSchema(id=1, name='Profil 01')
        profile_row2 = CtiProfileSchema(id=2, name='Profil 02')
        self.add_me(profile_row1)
        self.add_me(profile_row2)

        result = dao.get_id_by_name('Profil 02')

        assert_that(result, equal_to(2))

    def test_get_id_by_name_not_found(self):
        self.assertRaises(NotFoundError, dao.get_id_by_name, 'Profil 01')
