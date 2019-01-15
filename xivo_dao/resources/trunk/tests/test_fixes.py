# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

from hamcrest import assert_that, equal_to, none

from xivo_dao.alchemy.trunkfeatures import TrunkFeatures as Trunk
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.alchemy.useriax import UserIAX
from xivo_dao.alchemy.usercustom import UserCustom
from xivo_dao.resources.trunk.fixes import TrunkFixes
from xivo_dao.tests.test_dao import DAOTestCase


class TestTrunkFixes(DAOTestCase):

    def setUp(self):
        super(TestTrunkFixes, self).setUp()
        self.fixes = TrunkFixes(self.session)

    def test_given_trunk_has_sip_endpoint_then_category_and_context_updated(self):
        sip = self.add_usersip(context=None, category='user')
        trunk = self.add_trunk(protocol='sip', protocolid=sip.id, context='mycontext')

        self.fixes.fix(trunk.id)

        sip = self.session.query(UserSIP).first()
        assert_that(sip.category, equal_to('trunk'))
        assert_that(sip.context, equal_to('mycontext'))

    def test_given_trunk_has_iax_endpoint_then_category_and_context_updated(self):
        iax = self.add_useriax(context=None, category='user')
        trunk = self.add_trunk(protocol='iax', protocolid=iax.id, context='mycontext')

        self.fixes.fix(trunk.id)

        iax = self.session.query(UserIAX).first()
        assert_that(iax.category, equal_to('trunk'))
        assert_that(iax.context, equal_to('mycontext'))

    def test_given_trunk_has_custom_endpoint_then_category_and_context_updated(self):
        custom = self.add_usercustom(context=None, category='user')
        trunk = self.add_trunk(protocol='custom', protocolid=custom.id, context='mycontext')

        self.fixes.fix(trunk.id)

        custom = self.session.query(UserCustom).first()
        assert_that(custom.category, equal_to('trunk'))
        assert_that(custom.context, equal_to('mycontext'))

    def test_given_sip_protocol_is_no_longer_associated_then_protocol_removed(self):
        trunk = self.add_trunk(protocol='sip', protocolid=1234)

        self.fixes.fix(trunk.id)

        trunk = self.session.query(Trunk).first()
        assert_that(trunk.protocol, none())
        assert_that(trunk.protocolid, none())

    def test_given_iax_protocol_is_no_longer_associated_then_protocol_removed(self):
        trunk = self.add_trunk(protocol='iax', protocolid=1234)

        self.fixes.fix(trunk.id)

        trunk = self.session.query(Trunk).first()
        assert_that(trunk.protocol, none())
        assert_that(trunk.protocolid, none())

    def test_given_custom_protocol_is_no_longer_associated_then_protocol_removed(self):
        trunk = self.add_trunk(protocol='custom', protocolid=1234)

        self.fixes.fix(trunk.id)

        trunk = self.session.query(Trunk).first()
        assert_that(trunk.protocol, none())
        assert_that(trunk.protocolid, none())

    def test_given_other_protocol_is_no_longer_associated_then_protocol_removed(self):
        sccp = self.add_sccpline()
        trunk = self.add_trunk(protocol='sccp', protocolid=sccp.id)

        self.fixes.fix(trunk.id)

        trunk = self.session.query(Trunk).first()
        assert_that(trunk.protocol, none())
        assert_that(trunk.protocolid, none())
