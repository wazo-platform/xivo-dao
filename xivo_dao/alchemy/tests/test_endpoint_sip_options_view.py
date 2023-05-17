# Copyright 2021-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    equal_to,
    has_entries,
)

from xivo_dao.tests.test_dao import DAOTestCase
from ..endpoint_sip_options_view import EndpointSIPOptionsView


class TestView(DAOTestCase):
    def test_refresh(self):
        sip = self.add_endpoint_sip()
        sip.endpoint_section_options = [('key', 'value')]

        assert_that(sip.get_option_value('key'), equal_to(None))

        self.session.flush()
        self.session.expire(sip)

        assert_that(sip.get_option_value('key'), equal_to('value'))

    def test_multiple_inheritance(self):
        template1 = self.add_endpoint_sip()
        template2 = self.add_endpoint_sip()
        template3 = self.add_endpoint_sip(templates=[template1])
        sip = self.add_endpoint_sip(templates=[template2, template3])

        template1.endpoint_section_options = [('templ1', 'first')]
        template2.endpoint_section_options = [('templ2', 'second')]
        template3.endpoint_section_options = [('templ3', 'third')]
        sip.endpoint_section_options = [('sip', 'fourth')]

        self.session.flush()

        assert_that(
            sip._options,
            has_entries(templ1='first', templ2='second', templ3='third', sip='fourth'),
        )

    def test_inheritance_priority(self):
        template = self.add_endpoint_sip()
        sip = self.add_endpoint_sip(templates=[template])

        template.endpoint_section_options = [('option', 'template')]
        sip.endpoint_section_options = [('option', 'sip')]

        self.session.flush()

        assert_that(sip.get_option_value('option'), equal_to('sip'))

    def test_view_query(self):
        template = self.add_endpoint_sip()
        sip = self.add_endpoint_sip(templates=[template])

        template.endpoint_section_options = [('second', 'value2')]
        sip.endpoint_section_options = [('first', 'value1')]

        self.session.flush()

        result = (
            self.session.query(EndpointSIPOptionsView).filter_by(root=sip.uuid).first()
        )
        assert_that(result.root, equal_to(sip.uuid))
        assert_that(result.options, has_entries(first='value1', second='value2'))

    def test_view_dont_update_on_get(self):
        sip = self.add_endpoint_sip(
            endpoint_section_options=[('test', 'old_value')]
        )

        assert_that(sip.get_option_value('test'), equal_to('old_value'))

        sip.endpoint_section_options = [('test', 'new_value')]

        # view should not be updated, because no flush occurred
        assert_that(sip.get_option_value('test'), equal_to('old_value'))

        self.session.add(sip)
        self.session.flush()
        self.session.expire(sip)

        # view is only updated when a EndpointSIPOption object is updated
        assert_that(sip.get_option_value('test'), equal_to('new_value'))
