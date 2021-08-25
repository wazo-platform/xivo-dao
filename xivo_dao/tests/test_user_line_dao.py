# -*- coding: utf-8 -*-
# Copyright 2013-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao import user_line_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestUserLineDAO(DAOTestCase):

    def test_get_line_identity_with_no_line(self):
        self.assertRaises(LookupError, user_line_dao.get_line_identity_by_user_id, 1234)

    def test_get_line_identity(self):
        sip1 = self.add_endpoint_sip()
        sip2 = self.add_endpoint_sip()
        sip3 = self.add_endpoint_sip()
        self.add_user_line_with_exten(exten='445', endpoint_sip_uuid=sip1.uuid)
        self.add_user_line_with_exten(exten='221', endpoint_sip_uuid=sip2.uuid)
        user_line = self.add_user_line_with_exten(name_line='a1b2c3', endpoint_sip_uuid=sip3.uuid)

        result = user_line_dao.get_line_identity_by_user_id(user_line.user.id)

        self.assertEqual(result, 'pjsip/a1b2c3')
