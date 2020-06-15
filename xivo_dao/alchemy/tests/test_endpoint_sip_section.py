# -*- coding: utf-8 -*-
# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, none
from sqlalchemy.inspection import inspect

from xivo_dao.tests.test_dao import DAOTestCase

from ..endpoint_sip_section import EndpointSIPSection
from ..endpoint_sip_section_option import EndpointSIPSectionOption


class TestOptions(DAOTestCase):
    def test_ondelete_cascade_when_options_are_not_in_session(self):
        section = EndpointSIPSection(options=[['type', 'aor']])
        self.session.add(section)
        self.session.flush()
        self.session.expire_all()

        self.session.delete(section)
        self.session.flush()

        assert_that(inspect(section).deleted)
        option = self.session.query(EndpointSIPSectionOption).first()
        assert_that(option, none())
