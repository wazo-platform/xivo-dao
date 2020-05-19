# -*- coding: utf-8 -*-
# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao import user_line_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestUserLineDAO(DAOTestCase):

    def test_get_line_identity_with_no_line(self):
        self.assertRaises(LookupError, user_line_dao.get_line_identity_by_user_id, 1234)

    def test_get_line_identity(self):
        sip1 = self.add_usersip()
        sip2 = self.add_usersip()
        sip3 = self.add_usersip()
        self.add_user_line_with_exten(exten='445', endpoint_sip_id=sip1.id)
        self.add_user_line_with_exten(exten='221', endpoint_sip_id=sip2.id)
        user_line = self.add_user_line_with_exten(name_line='a1b2c3', endpoint_sip_id=sip3.id)

        result = user_line_dao.get_line_identity_by_user_id(user_line.user.id)

        self.assertEqual(result, 'sip/a1b2c3')
