# Copyright 2024-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, none, not_none

from xivo_dao.resources.func_key.tests.test_helpers import FuncKeyHelper
from xivo_dao.tests.test_dao import DAOTestCase

from ..func_key_dest_agent import FuncKey


class TestDelete(DAOTestCase, FuncKeyHelper):
    def setUp(self):
        super().setUp()
        self.setup_funckeys()

    def test_func_key_deleted(self):
        parking_lot = self.add_parking_lot()
        func_key_dest_parking = self.add_parking_destination(
            parking_lot_id=parking_lot.id,
        )

        row = self.session.query(FuncKey).first()
        assert_that(row, not_none())

        self.session.delete(func_key_dest_parking)
        self.session.flush()

        row = self.session.query(FuncKey).first()
        assert_that(row, none())
