# Copyright 2020-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains,
    contains_inanyorder,
    empty,
    equal_to,
    has_properties,
    none,
)
from xivo_dao.tests.test_dao import DAOTestCase

from ..endpoint_sip import EndpointSIP, EndpointSIPTemplate
from ..endpoint_sip_section import EndpointSIPSection
from ..endpoint_sip_options_view import EndpointSIPOptionsView


class TestEndpointSIP(DAOTestCase):
    def test_create_with_all_relations(self):
        transport = self.add_transport()
        template_1 = self.add_endpoint_sip(template=True)
        template_2 = self.add_endpoint_sip(template=True)

        endpoint = EndpointSIP(
            label='general_config',
            name='general_config',
            aor_section_options=[['type', 'aor']],
            auth_section_options=[['type', 'auth']],
            endpoint_section_options=[['type', 'endpoint']],
            registration_section_options=[['type', 'registration']],
            registration_outbound_auth_section_options=[['type', 'auth']],
            identify_section_options=[['type', 'identify']],
            outbound_auth_section_options=[['type', 'auth']],
            transport=transport,
            templates=[template_1, template_2],
            tenant_uuid=self.default_tenant.uuid,
            template=True,
        )
        self.session.add(endpoint)
        self.session.flush()
        self.session.expunge_all()

        row = self.session.query(EndpointSIP).filter_by(uuid=endpoint.uuid).first()
        assert_that(row, has_properties(
            label='general_config',
            name='general_config',
            aor_section_options=[['type', 'aor']],
            auth_section_options=[['type', 'auth']],
            endpoint_section_options=[['type', 'endpoint']],
            registration_section_options=[['type', 'registration']],
            registration_outbound_auth_section_options=[['type', 'auth']],
            identify_section_options=[['type', 'identify']],
            outbound_auth_section_options=[['type', 'auth']],
            template=True,
            transport=has_properties(uuid=transport.uuid),
            templates=contains(
                has_properties(uuid=template_1.uuid),
                has_properties(uuid=template_2.uuid),
            ),
        ))

    def test_create_concrete_endpoint(self):
        transport = self.add_transport()
        template = self.add_endpoint_sip(
            label="my tenant's global config",
            template=True,
            transport_uuid=transport.uuid,
        )

        endpoint = EndpointSIP(
            label='my-line',
            name='general_config',
            templates=[template],
            auth_section_options=[
                ['username', 'random-username'],
                ['password', 'random-password'],
            ],
            tenant_uuid=self.default_tenant.uuid,
        )
        self.session.add(endpoint)
        self.session.flush()

        row = self.session.query(EndpointSIP).filter_by(uuid=endpoint.uuid).first()
        assert_that(row, has_properties(
            label='my-line',
            name='general_config',
            aor_section_options=[],
            auth_section_options=[
                ['username', 'random-username'],
                ['password', 'random-password'],
            ],
            endpoint_section_options=[],
            registration_section_options=[],
            identify_section_options=[],
            outbound_auth_section_options=[],
            template=False,
            transport_uuid=None,
            templates=contains(
                has_properties(uuid=template.uuid),
            )
        ))

    def test_username(self):
        endpoint = self.add_endpoint_sip(
            auth_section_options=[['username', 'my-username']],
        )
        assert_that(endpoint.username, equal_to('my-username'))

        endpoint = self.add_endpoint_sip()
        assert_that(endpoint.username, none())

    def test_username_expression(self):
        self.add_endpoint_sip(auth_section_options=[['username', 'my-username']])
        self.add_endpoint_sip()
        endpoint_3 = self.add_endpoint_sip(
            auth_section_options=[['username', 'other-username']],
        )

        result = (
            self.session.query(EndpointSIP.uuid)
            .filter(EndpointSIP.username == 'other-username')
            .scalar()
        )
        assert_that(result, equal_to(endpoint_3.uuid))

    def test_password(self):
        endpoint = self.add_endpoint_sip(
            auth_section_options=[['password', 'my-password']],
        )
        assert_that(endpoint.password, equal_to('my-password'))

        endpoint = self.add_endpoint_sip()
        assert_that(endpoint.password, none())

    def test_password_expression(self):
        self.add_endpoint_sip(auth_section_options=[['password', 'my-password']])
        self.add_endpoint_sip(auth_section_options=[['username', 'my-password']])
        endpoint_3 = self.add_endpoint_sip(
            auth_section_options=[['password', 'other-password']],
        )

        result = (
            self.session.query(EndpointSIP.uuid)
            .filter(EndpointSIP.password == 'other-password')
            .scalar()
        )
        assert_that(result, equal_to(endpoint_3.uuid))


class TestAORSectionOptions(DAOTestCase):
    def test_delete_all(self):
        endpoint = self.add_endpoint_sip(aor_section_options=[['type', 'aor']])

        endpoint.aor_section_options = []
        self.session.flush()

        section = self.session.query(EndpointSIPSection).first()
        assert_that(section, none())

    def test_update(self):
        endpoint = self.add_endpoint_sip(aor_section_options=[['type', 'aor']])

        endpoint.aor_section_options = [['type', 'new']]
        self.session.flush()
        self.session.expire_all()

        assert_that(endpoint.aor_section_options, equal_to([['type', 'new']]))

    def test_create(self):
        endpoint = self.add_endpoint_sip()

        endpoint.aor_section_options = [['type', 'aor']]
        self.session.flush()
        self.session.expire_all()

        assert_that(endpoint.aor_section_options, equal_to([['type', 'aor']]))

    def test_get(self):
        endpoint = self.add_endpoint_sip(aor_section_options=[['type', 'aor']])
        assert_that(endpoint.aor_section_options, equal_to([['type', 'aor']]))

    def test_get_empty(self):
        endpoint = self.add_endpoint_sip(aor_section_options=None)
        assert_that(endpoint.aor_section_options, empty())


class TestTemplates(DAOTestCase):
    def test_order_by(self):
        sip = self.add_endpoint_sip()
        template_1 = self.add_endpoint_sip(template=True)
        template_2 = self.add_endpoint_sip(template=True)
        template_3 = self.add_endpoint_sip(template=True)

        sip.templates = [template_2, template_3, template_1]
        self.session.flush()

        self.session.expire_all()
        assert_that(sip.templates, contains(
            template_2,
            template_3,
            template_1,
        ))
        templates = self.session.query(EndpointSIPTemplate).all()
        assert_that(templates, contains_inanyorder(
            has_properties(parent_uuid=template_2.uuid, priority=0),
            has_properties(parent_uuid=template_3.uuid, priority=1),
            has_properties(parent_uuid=template_1.uuid, priority=2),
        ))

    def test_reorder_on_delete(self):
        template_1 = self.add_endpoint_sip(template=True)
        template_2 = self.add_endpoint_sip(template=True)
        template_3 = self.add_endpoint_sip(template=True)
        sip = self.add_endpoint_sip(templates=[template_1, template_2, template_3])

        sip.templates = [template_1, template_3]
        self.session.flush()

        self.session.expire_all()
        templates = self.session.query(EndpointSIPTemplate).all()
        assert_that(templates, contains_inanyorder(
            has_properties(parent_uuid=template_1.uuid, priority=0),
            has_properties(parent_uuid=template_3.uuid, priority=1),
        ))

    def test_delete(self):
        template = self.add_endpoint_sip(template=True)
        sip = self.add_endpoint_sip(templates=[template])

        sip.templates = []
        self.session.flush()

        self.session.expire_all()
        templates = self.session.query(EndpointSIPTemplate).all()
        assert_that(templates, empty())


class TestInheritedOptions(DAOTestCase):
    def test_inherited_aor_options(self):
        template_1 = self.add_endpoint_sip(
            template=True,
            aor_section_options=[['max_contacts', '1'], ['remove_existing', 'yes']],
        )
        template_2 = self.add_endpoint_sip(
            template=True,
            templates=[template_1],
            aor_section_options=[['max_contacts', '10'], ['remove_existing', 'no']],
        )

        sip = self.add_endpoint_sip(templates=[template_2])

        assert_that(
            sip.inherited_aor_section_options,
            contains(
                # template_1 options
                ['max_contacts', '1'],
                ['remove_existing', 'yes'],

                # template_2 options
                ['max_contacts', '10'],
                ['remove_existing', 'no'],
            )
        )

    def test_inherited_endpoint_options(self):
        template_1 = self.add_endpoint_sip(
            template=True,
            endpoint_section_options=[['webrtc', 'yes'], ['allow', '!all,ulaw']],
        )
        template_2 = self.add_endpoint_sip(
            template=True,
            templates=[template_1],
            endpoint_section_options=[['max_audio_streams', '25'], ['allow', '!all,alaw,g729']],
        )

        sip = self.add_endpoint_sip(templates=[template_2])

        assert_that(
            sip.inherited_endpoint_section_options,
            contains(
                # template_1 options
                ['webrtc', 'yes'],
                ['allow', '!all,ulaw'],

                # template_2 options
                ['max_audio_streams', '25'],
                ['allow', '!all,alaw,g729'],
            )
        )


class TestCombinedOptions(DAOTestCase):
    def test_combined_aor_options(self):
        template_1 = self.add_endpoint_sip(
            template=True,
            aor_section_options=[['max_contacts', '1'], ['remove_existing', 'yes']],
        )
        template_2 = self.add_endpoint_sip(
            template=True,
            templates=[template_1],
            aor_section_options=[['max_contacts', '10'], ['remove_existing', 'no']],
        )

        sip = self.add_endpoint_sip(
            templates=[template_2],
            aor_section_options=[['contact', 'sip:foo@bar']]
        )

        assert_that(
            sip.combined_aor_section_options,
            contains(
                # template_1 options
                ['max_contacts', '1'],
                ['remove_existing', 'yes'],

                # template_2 options
                ['max_contacts', '10'],
                ['remove_existing', 'no'],

                # endpoint options
                ['contact', 'sip:foo@bar'],
            )
        )

    def test_combined_endpoint_options(self):
        template_1 = self.add_endpoint_sip(
            template=True,
            endpoint_section_options=[['webrtc', 'yes'], ['allow', '!all,ulaw']],
        )
        template_2 = self.add_endpoint_sip(
            template=True,
            templates=[template_1],
            endpoint_section_options=[['max_audio_streams', '25'], ['allow', '!all,alaw,g729']],
        )

        sip = self.add_endpoint_sip(
            templates=[template_2],
            endpoint_section_options=[['allow', '!all,opus']],
        )

        assert_that(
            sip.combined_endpoint_section_options,
            contains(
                # template_1 options
                ['webrtc', 'yes'],
                ['allow', '!all,ulaw'],

                # template_2 options
                ['max_audio_streams', '25'],
                ['allow', '!all,alaw,g729'],

                # endpoint options
                ['allow', '!all,opus'],
            )
        )


class TestOptionValue(DAOTestCase):
    def setUp(self):
        super().setUp()
        self.sip = self.add_endpoint_sip()
        self.sip.endpoint_section_options = [('test', 'value')]
        EndpointSIPOptionsView.refresh()

    def test_get_value(self):
        assert_that(
            self.sip.get_option_value('test'),
            equal_to('value')
        )

    def test_get_value_invalid_option(self):
        assert_that(
            self.sip.get_option_value('invalid'),
            equal_to(None)
        )

    def test_get_value_no_option_values(self):
        sip = self.add_endpoint_sip()
        EndpointSIPOptionsView.refresh()

        assert_that(
            sip.get_option_value('somevalue'),
            equal_to(None)
        )


class TestCallerId(DAOTestCase):
    def test_get_callerid_nearest_value(self):
        template1 = self.add_endpoint_sip(caller_id='template1')
        template2 = self.add_endpoint_sip(caller_id='template2')
        sip = self.add_endpoint_sip(
            templates=[template1, template2], caller_id='template3'
        )
        EndpointSIPOptionsView.refresh()

        result = sip.get_option_value('callerid')
        assert_that(result, equal_to('template3'))

    def test_get_callerid_inherited(self):
        template1 = self.add_endpoint_sip(caller_id='template1')
        template2 = self.add_endpoint_sip(caller_id='template2')
        sip = self.add_endpoint_sip(templates=[template1, template2])
        EndpointSIPOptionsView.refresh()

        result = sip.get_option_value('callerid')
        assert_that(result, equal_to('template1'))

    def test_get_callerid_inherited_depth_first(self):
        template0 = self.add_endpoint_sip(caller_id='template0')
        template1 = self.add_endpoint_sip(templates=[template0])
        template2 = self.add_endpoint_sip(caller_id='template2')
        sip = self.add_endpoint_sip(templates=[template1, template2])
        EndpointSIPOptionsView.refresh()

        result = sip.get_option_value('callerid')
        assert_that(result, equal_to('template0'))

    def test_callerid_inheritance(self):
        template1 = self.add_endpoint_sip(caller_id='template1')
        sip = self.add_endpoint_sip(templates=[template1])
        EndpointSIPOptionsView.refresh()

        assert_that(
            sip.get_option_value('callerid'),
            equal_to('template1')
        )
        assert_that(
            template1.get_option_value('callerid'),
            equal_to('template1')
        )
