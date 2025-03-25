# Copyright 2020-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    contains_exactly,
    contains_inanyorder,
    empty,
    equal_to,
    has_entries,
    has_key,
    has_properties,
    none,
)
from xivo_dao.tests.test_dao import DAOTestCase

from ..endpoint_sip import EndpointSIP, EndpointSIPTemplate
from ..endpoint_sip_section import EndpointSIPSection


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
        assert_that(
            row,
            has_properties(
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
                templates=contains_exactly(
                    has_properties(uuid=template_1.uuid),
                    has_properties(uuid=template_2.uuid),
                ),
            ),
        )

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
        assert_that(
            row,
            has_properties(
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
                templates=contains_exactly(
                    has_properties(uuid=template.uuid),
                ),
            ),
        )

    def test_username(self):
        endpoint = self.add_endpoint_sip(
            auth_section_options=[['username', 'my-username']],
        )
        assert_that(endpoint.username, equal_to('my-username'))

        endpoint = self.add_endpoint_sip()
        assert_that(endpoint.username, none())

    def test_password(self):
        endpoint = self.add_endpoint_sip(
            auth_section_options=[['password', 'my-password']],
        )
        assert_that(endpoint.password, equal_to('my-password'))

        endpoint = self.add_endpoint_sip()
        assert_that(endpoint.password, none())


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
        assert_that(
            sip.templates,
            contains_exactly(
                template_2,
                template_3,
                template_1,
            ),
        )
        templates = self.session.query(EndpointSIPTemplate).all()
        assert_that(
            templates,
            contains_inanyorder(
                has_properties(parent_uuid=template_2.uuid, priority=0),
                has_properties(parent_uuid=template_3.uuid, priority=1),
                has_properties(parent_uuid=template_1.uuid, priority=2),
            ),
        )

    def test_reorder_on_delete(self):
        template_1 = self.add_endpoint_sip(template=True)
        template_2 = self.add_endpoint_sip(template=True)
        template_3 = self.add_endpoint_sip(template=True)
        sip = self.add_endpoint_sip(templates=[template_1, template_2, template_3])

        sip.templates = [template_1, template_3]
        self.session.flush()

        self.session.expire_all()
        templates = self.session.query(EndpointSIPTemplate).all()
        assert_that(
            templates,
            contains_inanyorder(
                has_properties(parent_uuid=template_1.uuid, priority=0),
                has_properties(parent_uuid=template_3.uuid, priority=1),
            ),
        )

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
            contains_exactly(
                # template_1 options
                ['max_contacts', '1'],
                ['remove_existing', 'yes'],
                # template_2 options
                ['max_contacts', '10'],
                ['remove_existing', 'no'],
            ),
        )

    def test_inherited_endpoint_options(self):
        template_1 = self.add_endpoint_sip(
            template=True,
            endpoint_section_options=[['webrtc', 'yes'], ['allow', '!all,ulaw']],
        )
        template_2 = self.add_endpoint_sip(
            template=True,
            templates=[template_1],
            endpoint_section_options=[
                ['max_audio_streams', '25'],
                ['allow', '!all,alaw,g729'],
            ],
        )

        sip = self.add_endpoint_sip(templates=[template_2])

        assert_that(
            sip.inherited_endpoint_section_options,
            contains_exactly(
                # template_1 options
                ['webrtc', 'yes'],
                ['allow', '!all,ulaw'],
                # template_2 options
                ['max_audio_streams', '25'],
                ['allow', '!all,alaw,g729'],
            ),
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
            templates=[template_2], aor_section_options=[['contact', 'sip:foo@bar']]
        )

        assert_that(
            sip.combined_aor_section_options,
            contains_exactly(
                # template_1 options
                ['max_contacts', '1'],
                ['remove_existing', 'yes'],
                # template_2 options
                ['max_contacts', '10'],
                ['remove_existing', 'no'],
                # endpoint options
                ['contact', 'sip:foo@bar'],
            ),
        )

    def test_combined_endpoint_options(self):
        template_1 = self.add_endpoint_sip(
            template=True,
            endpoint_section_options=[['webrtc', 'yes'], ['allow', '!all,ulaw']],
        )
        template_2 = self.add_endpoint_sip(
            template=True,
            templates=[template_1],
            endpoint_section_options=[
                ['max_audio_streams', '25'],
                ['allow', '!all,alaw,g729'],
            ],
        )

        sip = self.add_endpoint_sip(
            templates=[template_2],
            endpoint_section_options=[['allow', '!all,opus']],
        )

        assert_that(
            sip.combined_endpoint_section_options,
            contains_exactly(
                # template_1 options
                ['webrtc', 'yes'],
                ['allow', '!all,ulaw'],
                # template_2 options
                ['max_audio_streams', '25'],
                ['allow', '!all,alaw,g729'],
                # endpoint options
                ['allow', '!all,opus'],
            ),
        )


class TestOptionValue(DAOTestCase):
    def setUp(self):
        super().setUp()
        self.sip = self.add_endpoint_sip()
        self.sip.endpoint_section_options = [('test', 'value')]

    def test_get_value(self):
        endpoint = self.sip.all_options['endpoint']
        assert_that(endpoint['test'], equal_to('value'))

    def test_get_value_invalid_option(self):
        endpoint = self.sip.all_options['endpoint']
        assert_that(endpoint.get('invalid'), equal_to(None))

    def test_get_value_no_option_values(self):
        sip = self.add_endpoint_sip()
        assert_that(sip.all_options.get('endpoint'), equal_to(None))


class TestCallerId(DAOTestCase):
    def test_get_callerid_nearest_value(self):
        template1 = self.add_endpoint_sip(caller_id='template1')
        template2 = self.add_endpoint_sip(caller_id='template2')
        sip = self.add_endpoint_sip(templates=[template1, template2], caller_id='sip')

        print(sip.all_options)
        assert_that(
            sip.all_options['endpoint']['callerid'],
            equal_to('sip'),
        )

    def test_get_callerid_inherited(self):
        template1 = self.add_endpoint_sip(caller_id='template1')
        template2 = self.add_endpoint_sip(caller_id='template2')
        sip = self.add_endpoint_sip(templates=[template1, template2])

        assert_that(
            sip.all_options['endpoint']['callerid'],
            equal_to('template1'),
        )

    def test_get_callerid_inherited_depth_first(self):
        template0 = self.add_endpoint_sip(caller_id='template0')
        template1 = self.add_endpoint_sip(templates=[template0])
        template2 = self.add_endpoint_sip(caller_id='template2')
        sip = self.add_endpoint_sip(templates=[template1, template2])

        assert_that(
            sip.all_options['endpoint']['callerid'],
            equal_to('template0'),
        )

    def test_callerid_inheritance(self):
        template1 = self.add_endpoint_sip(caller_id='template1')
        sip = self.add_endpoint_sip(templates=[template1])

        assert_that(
            sip.all_options['endpoint']['callerid'],
            equal_to('template1'),
        )
        assert_that(
            template1.all_options['endpoint']['callerid'],
            equal_to('template1'),
        )


class TestAllOptions(DAOTestCase):
    def test_all_options(self):
        aor_values = [
            ('aor-1', 'aor-value-1'),
        ]
        auth_values = [
            ('auth-1', 'auth-value-1'),
            ('auth-2', 'auth-value-2'),
            ('auth-3', 'auth-value-3'),
        ]
        endpoint_values = [
            ('first', '1st'),
            ('second', '2nd'),
            ('third', '3rd'),
        ]
        sip = self.add_endpoint_sip()
        sip.endpoint_section_options = endpoint_values
        sip.auth_section_options = auth_values
        sip.aor_section_options = aor_values

        assert_that(
            sip.all_options,
            has_entries(
                aor=has_entries(
                    {
                        'aor-1': 'aor-value-1',
                    }
                ),
                auth=has_entries(
                    {
                        'auth-1': 'auth-value-1',
                        'auth-2': 'auth-value-2',
                        'auth-3': 'auth-value-3',
                    }
                ),
                endpoint=has_entries(
                    first='1st',
                    second='2nd',
                    third='3rd',
                ),
            ),
        )

    def test_inheritance(self):
        template1 = self.add_endpoint_sip()
        template1.endpoint_section_options = [('key1', 'template-value')]

        sip = self.add_endpoint_sip(templates=[template1])
        sip.endpoint_section_options = [
            ('key1', 'endpoint-value'),
            ('key2', 'other-value'),
        ]

        assert_that(
            sip.all_options['endpoint'],
            has_entries(
                key1='endpoint-value',
                key2='other-value',
            ),
        )

    def test_inheritance_depth_first(self):
        grandparent = self.add_endpoint_sip()
        parent1 = self.add_endpoint_sip(templates=[grandparent])
        parent2 = self.add_endpoint_sip()

        grandparent.endpoint_section_options = [('template', 'grandparent')]
        parent1.endpoint_section_options = [('template', 'parent 1')]
        parent2.endpoint_section_options = [
            ('template', 'parent 2'),
            ('other', 'value'),
        ]

        sip = self.add_endpoint_sip(templates=[parent1, parent2])
        assert_that(sip.all_options['endpoint']['template'], 'parent 1')

        parent1.endpoint_section_options = []
        sip = self.add_endpoint_sip(templates=[parent1, parent2])
        assert_that(sip.all_options['endpoint']['template'], 'grandparent')

        assert_that(sip.all_options['endpoint']['other'], 'value')

    def test_inheritance_from_many(self):
        base = self.add_endpoint_sip()
        base.endpoint_section_options = [('foo', 'bar')]
        base.auth_section_options = [('username', 'heros')]

        templates = [base]
        for identifier in ('A', 'B', 'C', 'D', 'E'):
            endpoint = self.add_endpoint_sip(templates=[templates[-1]])
            endpoint.endpoint_section_options = [(f'template{identifier}', True)]
            templates.append(endpoint)

        sip = self.add_endpoint_sip(templates=[templates[-1]])

        print(sip.all_options)
        assert_that(
            sip.all_options,
            has_entries(
                endpoint=all_of(
                    has_entries(foo='bar'),
                    has_key('templateA'),
                    has_key('templateB'),
                    has_key('templateC'),
                    has_key('templateD'),
                    has_key('templateE'),
                ),
            ),
        ),

    def test_sql_expression(self):
        sip_1 = self.add_endpoint_sip(label='1')
        sip_1.endpoint_section_options = [('key_1', 'value_1'), ('key_2', 'value_2')]
        sip_1.auth_section_options = [('foo', 'bar')]
        sip_1.outbound_auth_section_options = [('key_1', 'value_4')]

        sip_2 = self.add_endpoint_sip(label='2')
        sip_2.aor_section_options = [('fooz', 'baz')]
        sip_2.auth_section_options = []

        sip_3 = self.add_endpoint_sip(label='3')
        sip_3.registration_section_options = [('registration_1', 'test')]
        sip_3.endpoint_section_options = [('key_1', 'some-other-value')]

        scenarios = (
            (EndpointSIP.all_options['auth'].has_key('foo'), (sip_1,)),
            (EndpointSIP.all_options['aor'].has_key('fooz'), (sip_2,)),
            (EndpointSIP.all_options['auth'].op('->>')('foo') == 'bar', (sip_1,)),
            (EndpointSIP.all_options.op('#>>')('{aor,fooz}') == 'baz', (sip_2,)),
            (EndpointSIP.all_options.op('#>>')('{aor,fooz}') == 'invalid', None),
            (
                EndpointSIP.all_options.op('#>>')('{endpoint,key_1}') == 'value_1',
                (sip_1,),
            ),
            (EndpointSIP.all_options['endpoint'].has_key('key_1'), (sip_1, sip_3)),
        )

        for scenario_id, (filters, expected) in enumerate(scenarios, 1):
            result = self.session.query(EndpointSIP).filter(filters).all()
            matcher = contains_inanyorder(*expected) if expected else empty()

            assert_that(result, matcher, f"Scenario #{scenario_id} failed")
