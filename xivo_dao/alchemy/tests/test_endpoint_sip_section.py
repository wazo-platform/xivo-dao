# -*- coding: utf-8 -*-
# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains_inanyorder,
    equal_to,
    has_properties,
    none,
    not_,
)
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

    def test_create_an_option(self):
        section = EndpointSIPSection(options=[])
        self.session.add(section)
        self.session.flush()

        section.options = [['type', 'aor']]
        self.session.flush()
        self.session.expire_all()
        assert_that(section.options, contains_inanyorder(['type', 'aor']))

    def test_update_an_option(self):
        section = EndpointSIPSection(options=[['type', 'aor'], ['old', 'value']])
        self.session.add(section)
        self.session.flush()

        section.options = [['type', 'aor'], ['new', 'value']]
        self.session.flush()
        self.session.expire_all()

        assert_that(section.options, contains_inanyorder(['type', 'aor'], ['new', 'value']))

    def test_delete_an_option(self):
        section = EndpointSIPSection(options=[['type', 'aor'], ['delete', 'value']])
        self.session.add(section)
        self.session.flush()

        section.options = [['type', 'aor']]
        self.session.flush()
        self.session.expire_all()

        assert_that(section.options, contains_inanyorder(['type', 'aor']))

    def test_update_and_create_options(self):
        section = EndpointSIPSection(options=[['update', 'old']])
        self.session.add(section)
        self.session.flush()

        section.options = [['create', 'value'], ['update', 'new']]
        self.session.flush()
        self.session.expire_all()

        assert_that(section.options, contains_inanyorder(['create', 'value'], ['update', 'new']))

    def test_update_and_delete_options(self):
        section = EndpointSIPSection(options=[['update', 'old'], ['delete', 'value']])
        self.session.add(section)
        self.session.flush()

        section.options = [['update', 'new']]
        self.session.flush()
        self.session.expire_all()

        assert_that(section.options, contains_inanyorder(['update', 'new']))

    def test_update_an_option_do_not_reuse_or_orphan_option(self):
        section = EndpointSIPSection(options=[['old', 'value']])
        self.session.add(section)
        self.session.flush()
        old_uuid = section._options[0].uuid

        section.options = [['new', 'value']]
        self.session.flush()
        self.session.expire_all()
        new_uuid = section._options[0].uuid

        assert_that(new_uuid, not_(equal_to(old_uuid)))
        options = self.session.query(EndpointSIPSectionOption).all()
        assert_that(options, contains_inanyorder(has_properties(uuid=new_uuid)))
