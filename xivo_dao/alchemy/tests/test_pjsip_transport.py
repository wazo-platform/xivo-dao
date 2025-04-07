# Copyright 2020-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains_exactly,
    contains_inanyorder,
    equal_to,
    has_properties,
)
from sqlalchemy import func

from xivo_dao.tests.test_dao import DAOTestCase

from ..pjsip_transport import PJSIPTransport
from ..pjsip_transport_option import PJSIPTransportOption


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
        assert_that(
            row,
            has_properties(
                name='my-transport',
                options=contains_inanyorder(
                    contains_exactly('local_net', network),
                    contains_exactly('external_media_address', public_ip),
                    contains_exactly('external_signaling_address', public_ip),
                ),
            ),
        )

    def test_adding_options(self):
        local_net = '192.168.0.0/32'
        public_ip = '10.37.0.42'

        original_options = [
            ['local_net', local_net],
            ['external_media_address', public_ip],
            ['external_signaling_address', public_ip],
        ]

        transport = self.add_transport(options=original_options)

        new_options = list(original_options) + [
            ['local_net', '10.37.1.16/24'],
            ['tos', 'ef'],
        ]

        transport.options = new_options

        row = self.session.query(PJSIPTransport).filter_by(uuid=transport.uuid).first()
        assert_that(row, has_properties(options=contains_inanyorder(*new_options)))

    def test_removing_and_adding_options(self):
        local_net = '192.168.0.0/32'
        public_ip = '10.37.0.42'

        original_options = [
            ['local_net', local_net],
            ['external_media_address', public_ip],
            ['external_signaling_address', public_ip],
        ]

        transport = self.add_transport(options=original_options)

        new_options = list(original_options[:-1]) + [
            ['tos', 'ef'],
        ]

        transport.options = new_options

        row = self.session.query(PJSIPTransport).filter_by(uuid=transport.uuid).first()
        assert_that(row, has_properties(options=contains_inanyorder(*new_options)))

    def test_option_removal(self):
        options = [
            ['local_net', '192.168.0.0/32'],
            ['external_media_address', '10.37.0.42'],
            ['external_signaling_address', '10.37.0.42'],
        ]

        transport = self.add_transport(options=options)

        self.session.delete(transport)

        remaining_options = self.session.query(
            func.count(PJSIPTransportOption.id)
        ).scalar()

        assert_that(remaining_options, equal_to(0))
