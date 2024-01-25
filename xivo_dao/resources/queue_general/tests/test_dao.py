# Copyright 2018-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from hamcrest import (
    assert_that,
    contains_exactly,
    contains_inanyorder,
    empty,
)

from xivo_dao.alchemy.staticqueue import StaticQueue
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as queue_general_dao


class TestFindAll(DAOTestCase):
    def test_find_all_no_queue_general(self):
        result = queue_general_dao.find_all()

        assert_that(result, empty())

    def test_find_all(self):
        row1 = self.add_queue_general_settings(var_metric=3)
        row2 = self.add_queue_general_settings(var_metric=2)
        row3 = self.add_queue_general_settings(var_metric=1)
        row4 = self.add_queue_general_settings(var_metric=4)

        queue_general = queue_general_dao.find_all()

        assert_that(queue_general, contains_exactly(row3, row2, row1, row4))

    def test_find_all_do_not_find_var_val_none(self):
        self.add_queue_general_settings(
            var_metric=1, var_name='monitor-type', var_val=None
        )
        row2 = self.add_queue_general_settings(
            var_metric=2, var_name='setting1', var_val='value1'
        )

        queue_general = queue_general_dao.find_all()

        assert_that(queue_general, contains_exactly(row2))


class TestEditAll(DAOTestCase):
    def test_edit_all(self):
        row1 = StaticQueue(var_name='setting1', var_val='value1')
        row2 = StaticQueue(var_name='setting2', var_val='value1')
        row3 = StaticQueue(var_name='setting3', var_val='value1')
        row4 = StaticQueue(var_name='setting2', var_val='value2')

        queue_general_dao.edit_all([row1, row2, row3, row4])

        self.session.expire_all()
        queue_general = queue_general_dao.find_all()
        assert_that(queue_general, contains_inanyorder(row1, row2, row3, row4))

    def test_delete_old_entries(self):
        self.add_queue_general_settings()
        self.add_queue_general_settings()
        row = StaticQueue(var_name='nat', var_val='value1')

        queue_general_dao.edit_all([row])

        self.session.expire_all()
        queue_general = queue_general_dao.find_all()
        assert_that(queue_general, contains_exactly(row))
