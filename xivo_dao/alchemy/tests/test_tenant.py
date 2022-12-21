# Copyright 2020-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_properties

from xivo_dao.tests.test_dao import DAOTestCase

from ..tenant import Tenant


class TestTenantSIPTemplates(DAOTestCase):
    def test_sip_template_properties(self):
        tenant = self.add_tenant()

        global_template = self.add_endpoint_sip(
            label='global', template=True, tenant_uuid=tenant.uuid,
        )
        webrtc_template = self.add_endpoint_sip(
            label='webrtc', template=True, tenant_uuid=tenant.uuid,
        )
        reg_template = self.add_endpoint_sip(
            label='reg trunk', template=True, tenant_uuid=tenant.uuid,
        )
        tenant.sip_templates_generated = True
        tenant.global_sip_template_uuid = global_template.uuid
        tenant.webrtc_sip_template_uuid = webrtc_template.uuid
        tenant.registration_trunk_sip_template_uuid = reg_template.uuid

        self.session.flush()
        self.session.expunge_all()

        row = self.session.query(Tenant).filter_by(uuid=tenant.uuid).first()
        assert_that(
            row,
            has_properties(
                global_sip_template=has_properties(uuid=global_template.uuid),
                webrtc_sip_template=has_properties(uuid=webrtc_template.uuid),
                registration_trunk_sip_template=has_properties(uuid=reg_template.uuid),
            )
        )
