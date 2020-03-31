# -*- coding: utf-8 -*-
# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_properties, contains, contains_inanyorder
from xivo_dao.tests.test_dao import DAOTestCase
from ..pjsip_transport import PJSIPTransport


class TestPJSIPTransport(DAOTestCase):

    def test_creation(self):
        public_ip = '10.37.0.42'
        network = '192.168.0.0/32'

        transport = PJSIPTransport(
            name='my-transport',
            options=[
                ['local_net', network],
                ['external_media_address', public_ip],
                ['external_signaling_address', public_ip],
            ],
        )
        self.add_me(transport)

        row = self.session.query(PJSIPTransport).filter_by(uuid=transport.uuid).first()
        assert_that(row, has_properties(
            name='my-transport',
            options=contains_inanyorder(
                contains('local_net', network),
                contains('external_media_address', public_ip),
                contains('external_signaling_address', public_ip),
            )
        ))
