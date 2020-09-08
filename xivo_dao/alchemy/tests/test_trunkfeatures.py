# -*- coding: utf-8 -*-
# Copyright 2018-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    calling,
    raises,
)
from sqlalchemy.exc import IntegrityError

from xivo_dao.tests.test_dao import DAOTestCase


class TestConstraint(DAOTestCase):

    def test_many_endpoints(self):
        sip = self.add_endpoint_sip()
        iax = self.add_useriax()
        assert_that(calling(self.add_trunk).with_args(
            endpoint_sip_uuid=sip.uuid, endpoint_iax_id=iax.id,
        ), raises(IntegrityError))

    def test_register_iax_endpoint_sip_raise_integrity(self):
        sip = self.add_endpoint_sip()
        register_iax = self.add_register_iax()
        assert_that(calling(self.add_trunk).with_args(
            endpoint_sip_uuid=sip.uuid, register_iax_id=register_iax.id,
        ), raises(IntegrityError))

    def test_register_iax_endpoint_custom_raise_integrity(self):
        custom = self.add_usercustom()
        register_iax = self.add_register_iax()
        assert_that(calling(self.add_trunk).with_args(
            endpoint_custom_id=custom.id, register_iax_id=register_iax.id,
        ), raises(IntegrityError))
