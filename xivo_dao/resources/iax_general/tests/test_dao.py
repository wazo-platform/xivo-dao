# Copyright 2017-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from hamcrest import assert_that, empty, equal_to

from xivo_dao.alchemy.staticiax import StaticIAX
from xivo_dao.resources.iax_general import dao as iax_general_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestFindAll(DAOTestCase):
    def test_find_all_no_iax_general(self):
        result = iax_general_dao.find_all()

        assert_that(result, empty())

    def test_find_all(self):
        row1 = self.add_iax_general_settings(
            var_metric=3, var_name='setting1', var_val='value1'
        )
        row2 = self.add_iax_general_settings(
            var_metric=2, var_name='setting2', var_val='value1'
        )
        row3 = self.add_iax_general_settings(
            var_metric=1, var_name='setting3', var_val='value1'
        )
        row4 = self.add_iax_general_settings(
            var_metric=4, var_name='setting2', var_val='value2'
        )

        iax_general = iax_general_dao.find_all()

        assert_that(iax_general, equal_to([row3, row2, row1, row4]))

    def test_find_all_do_not_find_register(self):
        self.add_iax_general_settings(
            var_metric=1, var_name='register', var_val='value1'
        )
        row2 = self.add_iax_general_settings(
            var_metric=2, var_name='setting1', var_val='value1'
        )

        iax_general = iax_general_dao.find_all()

        assert_that(iax_general, equal_to([row2]))

    def test_find_all_do_not_find_var_val_none(self):
        self.add_iax_general_settings(var_metric=1, var_name='setting1', var_val=None)
        row2 = self.add_iax_general_settings(
            var_metric=2, var_name='setting1', var_val='value1'
        )

        iax_general = iax_general_dao.find_all()

        assert_that(iax_general, equal_to([row2]))


class TestEditAll(DAOTestCase):
    def test_edit_all(self):
        row1 = StaticIAX(var_name='setting1', var_val='value1')
        row2 = StaticIAX(var_name='setting2', var_val='value1')
        row3 = StaticIAX(var_name='setting3', var_val='value1')
        row4 = StaticIAX(var_name='setting2', var_val='value2')

        iax_general_dao.edit_all([row3, row4, row2, row1])

        iax_general = iax_general_dao.find_all()
        assert_that(iax_general, equal_to([row3, row4, row2, row1]))

    def test_edit_all_do_not_delete_register(self):
        row1 = self.add_iax_general_settings(
            var_metric=1, var_name='register', var_val='value1'
        )

        row2 = StaticIAX(var_name='nat', var_val='value1')

        iax_general_dao.edit_all([row2])

        assert_that(
            self.session.query(StaticIAX)
            .filter(StaticIAX.var_name == 'register')
            .first(),
            equal_to(row1),
        )

    def test_delete_old_entries(self):
        self.add_iax_general_settings()
        self.add_iax_general_settings()
        row = StaticIAX(var_name='nat', var_val='value1')

        iax_general_dao.edit_all([row])

        iax_general = iax_general_dao.find_all()
        assert_that(iax_general, equal_to([row]))


class TestTable(DAOTestCase):
    def test_values_from_renamed_column(self):
        row1 = StaticIAX(var_name='setting1', var_val='value1', metric=None)
        row2 = StaticIAX(var_name='setting2', var_val='value1', metric=0)
        row3 = StaticIAX(var_name='setting3', var_val='value1', metric=1)

        assert_that(row1.var_metric, equal_to(0))
        assert_that(row2.var_metric, equal_to(1))
        assert_that(row3.var_metric, equal_to(2))
