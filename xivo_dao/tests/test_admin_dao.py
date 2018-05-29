# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import assert_that, calling, equal_to, raises

from xivo_dao import admin_dao
from xivo_dao.helpers import exception
from xivo_dao.tests.test_dao import DAOTestCase, DEFAULT_TENANT


class TestAdminUserDAO(DAOTestCase):

    def test_given_right_credentials_when_check_username_password_then_return_true(self):
        self.add_admin(login='foo', passwd='bar')

        valid = admin_dao.check_username_password('foo', 'bar')

        assert_that(valid, equal_to(True))

    def test_given_invalid_account_when_check_username_password_then_return_false(self):
        self.add_admin(login='foo', passwd='bar', valid=0)

        valid = admin_dao.check_username_password('foo', 'bar')

        assert_that(valid, equal_to(False))

    def test_given_invalid_login_when_check_username_password_then_return_false(self):
        self.add_admin(login='foo', passwd='bar')

        valid = admin_dao.check_username_password('alice', 'bar')

        assert_that(valid, equal_to(False))

    def test_given_invalid_password_when_check_username_password_then_return_false(self):
        self.add_admin(login='foo', passwd='bar')

        valid = admin_dao.check_username_password('foo', 'superdupersecret')

        assert_that(valid, equal_to(False))

    def test_get_admin_uuid(self):
        admin = self.add_admin(login='foo', passwd='bar')

        result = admin_dao.get_admin_uuid('foo')

        assert_that(result, equal_to(admin.uuid))

    def test_that_get_admin_uuid_raises_if_not_found(self):
        assert_that(
            calling(admin_dao.get_admin_uuid).with_args('foo'),
            raises(exception.NotFoundError))

    def test_get_admin_entity(self):
        tenant = self.add_tenant()
        entity = self.add_entity(name='test', tenant_uuid=tenant.uuid)
        self.add_admin(login='foo', passwd='bar', entity_id=entity.id)

        name, tenant_uuid = admin_dao.get_admin_entity('foo')

        assert_that(name, equal_to('test'))
        assert_that(tenant_uuid, equal_to(tenant.uuid))

    def test_get_admin_entity_no_entify(self):
        self.add_admin(login='alice', passwd='foobar')

        name, tenant_uuid = admin_dao.get_admin_entity('alice')

        assert_that(name, equal_to(None))
        assert_that(tenant_uuid, equal_to(None))
