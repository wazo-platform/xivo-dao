# -*- coding: utf-8 -*-
# Copyright 2013-2016 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import assert_that, equal_to, has_length

from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.resources.cti_profile import dao
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.tests.test_dao import DAOTestCase


class TestCtiProfile(DAOTestCase):

    def test_find_all(self):
        profile_row1 = CtiProfile(id=1, name='Profil 01')
        profile_row2 = CtiProfile(id=2, name='Profil 02')
        self.add_me(profile_row1)
        self.add_me(profile_row2)

        result = dao.find_all()

        assert_that(result, has_length(2))
        assert_that(result[0].id, equal_to(1))
        assert_that(result[0].name, equal_to('Profil 01'))
        assert_that(result[1].id, equal_to(2))
        assert_that(result[1].name, equal_to('Profil 02'))

    def test_get(self):
        profile_row = CtiProfile(id=1, name='Profil 01')
        self.add_me(profile_row)

        result = dao.get(1)

        assert_that(result.id, equal_to(1))
        assert_that(result.name, equal_to('Profil 01'))

    def test_get_unknown_user(self):
        self.assertRaises(NotFoundError, dao.get, 1)

    def test_get_id_by_name(self):
        profile_row1 = CtiProfile(id=1, name='Profil 01')
        profile_row2 = CtiProfile(id=2, name='Profil 02')
        self.add_me(profile_row1)
        self.add_me(profile_row2)

        result = dao.get_id_by_name('Profil 02')

        assert_that(result, equal_to(2))

    def test_get_id_by_name_not_found(self):
        self.assertRaises(NotFoundError, dao.get_id_by_name, 'Profil 01')
