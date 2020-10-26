# -*- coding: utf-8 -*-
# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    none,
)
from xivo_dao.tests.test_dao import DAOTestCase

from ..user_external_app import UserExternalApp


class TestConfiguration(DAOTestCase):
    def test_json_null(self):
        user = self.add_user()
        user_external_app = self.add_user_external_app(
            user_uuid=user.uuid,
            configuration=None,
        )

        self.session.expire_all()

        assert_that(user_external_app.configuration, none())


class TestTenant(DAOTestCase):
    def test_delete_on_cascade(self):
        user = self.add_user()
        self.add_user_external_app(user_uuid=user.uuid)

        self.session.delete(user)
        self.session.flush()

        result = self.session.query(UserExternalApp).first()
        assert_that(result, none())
