# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    none,
    not_none,
)

from xivo_dao.tests.test_dao import DAOTestCase

from ..func_key_mapping import FuncKeyMapping


class TestDelete(DAOTestCase):

    def test_func_key_mapping_deleted(self):
        func_key_destination = self.add_func_key_destination_type()
        func_key_type = self.add_func_key_type()
        func_key = self.add_func_key(type_id=func_key_type.id, destination_type_id=func_key_destination.id)

        template = self.add_func_key_template()
        self.add_func_key_mapping(
            func_key_id=func_key.id,
            template_id=template.id,
            destination_type_id=func_key_destination.id,
        )

        row = self.session.query(FuncKeyMapping).first()
        assert_that(row, not_none())

        self.session.delete(func_key)
        self.session.flush()

        row = self.session.query(FuncKeyMapping).first()
        assert_that(row, none())
