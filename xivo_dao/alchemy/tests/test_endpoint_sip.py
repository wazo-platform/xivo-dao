# Copyright 2020-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains_exactly,
    contains_inanyorder,
    empty,
    equal_to,
    has_properties,
    none,
)
from xivo_dao.tests.test_dao import DAOTestCase

from sqlalchemy.sql import select

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


class TestCallerId(DAOTestCase):
    def sql_caller_id(self, sip):
        selectable = select([EndpointSIP.caller_id]).where(EndpointSIP.uuid == sip.uuid)
        return self.session.execute(selectable).scalar()

    def test_get_callerid_nearest_value(self):
        template1 = self.add_endpoint_sip(caller_id='template1')
        template2 = self.add_endpoint_sip(caller_id='template2')
        sip = self.add_endpoint_sip(templates=[template1, template2], caller_id='sip')

        assert_that(sip.caller_id, equal_to('sip'))
        assert_that(self.sql_caller_id(sip), equal_to('sip'))

    def test_get_callerid_inherited(self):
        template1 = self.add_endpoint_sip(caller_id='template1')
        template2 = self.add_endpoint_sip(caller_id='template2')
        sip = self.add_endpoint_sip(templates=[template1, template2])

        assert_that(sip.caller_id, equal_to('template1'))
        assert_that(self.sql_caller_id(sip), equal_to('template1'))

    def test_get_callerid_inherited_depth_first(self):
        template0 = self.add_endpoint_sip(caller_id='template0')
        template1 = self.add_endpoint_sip(templates=[template0])
        template2 = self.add_endpoint_sip(caller_id='template2')
        sip = self.add_endpoint_sip(templates=[template1, template2])

        assert_that(sip.caller_id, equal_to('template0'))
        assert_that(self.sql_caller_id(sip), equal_to('template0'))

    def test_callerid_inheritance(self):
        template1 = self.add_endpoint_sip(caller_id='template1')
        sip = self.add_endpoint_sip(templates=[template1])

        assert_that(sip.caller_id, equal_to('template1'))
        assert_that(self.sql_caller_id(sip), equal_to('template1'))
        assert_that(template1.caller_id, equal_to('template1'))
        assert_that(self.sql_caller_id(template1), equal_to('template1'))


class TestOptions(DAOTestCase):
    def test_get_options(self):
        sip = self.add_endpoint_sip()
        sip.endpoint_section_options = [('endpoint-1', 'value-1')]
        sip.auth_section_options = [('auth-2', 'value-2')]
        sip.aor_section_options = [('aor-3', 'value-3')]

        assert_that(sip._options_dfs('endpoint-1'), equal_to('value-1'))
        assert_that(sip._options_dfs('auth-2'), equal_to('value-2'))
        assert_that(sip._options_dfs('aor-3'), equal_to('value-3'))

    def test_inheritance(self):
        template1 = self.add_endpoint_sip()
        template1.endpoint_section_options = [
            ('key1', 'template-value-1'),
            ('key2', 'template-value-2'),
        ]

        sip = self.add_endpoint_sip(templates=[template1])
        sip.endpoint_section_options = [
            ('key1', 'endpoint-value-1'),
        ]

        assert_that(sip._options_dfs('key1'), equal_to('endpoint-value-1'))
        assert_that(sip._options_dfs('key2'), equal_to('template-value-2'))

    def test_inheritance_sql(self):
        Query = self.session.query

        template1 = self.add_endpoint_sip()
        template1.endpoint_section_options = [('callerid', 'template1')]

        template2 = self.add_endpoint_sip()
        template2.endpoint_section_options = [('callerid', 'template2')]

        template3 = self.add_endpoint_sip(templates=[template1])

        template4 = self.add_endpoint_sip()
        template4.endpoint_section_options = [('callerid', 'template4')]

        sip1 = self.add_endpoint_sip(templates=[template3, template4, template2])
        sip2 = self.add_endpoint_sip(templates=[template4, template3])

        query = Query(EndpointSIP).filter(
            EndpointSIP._options_dfs_sql('callerid', 'endpoint') == 'template1'
        )
        assert_that(query.all(), contains_inanyorder(template1, template3, sip1))

        query = Query(EndpointSIP).filter(
            EndpointSIP._options_dfs_sql('callerid', 'endpoint') == 'template4'
        )
        assert_that(query.all(), contains_inanyorder(template4, sip2))

    def test_inheritance_depth_first(self):
        def endpoint_option(uuid, option):
            selectable = select([EndpointSIP._options_dfs_sql(option)]).where(
                EndpointSIP.uuid == uuid
            )
            return self.session.execute(selectable).scalar()

        grandparent = self.add_endpoint_sip()
        parent1 = self.add_endpoint_sip(templates=[grandparent])
        parent2 = self.add_endpoint_sip()

        grandparent.endpoint_section_options = [('template', 'grandparent')]
        parent2.endpoint_section_options = [
            ('template', 'parent 2'),
            ('other', 'value'),
        ]

        sip1 = self.add_endpoint_sip(templates=[parent1, parent2])
        assert_that(
            sip1._options_dfs('template', 'endpoint'),
            equal_to('grandparent'),
        )
        assert_that(
            endpoint_option(sip1.uuid, 'template'),
            equal_to('grandparent'),
        )

        sip2 = self.add_endpoint_sip(templates=[parent2, parent1])
        assert_that(
            sip2._options_dfs('template', 'endpoint'),
            equal_to('parent 2'),
        )
        assert_that(
            sip2._options_dfs('other', 'endpoint'),
            equal_to('value'),
        )
        assert_that(
            endpoint_option(sip2.uuid, 'template'),
            equal_to('parent 2'),
        )

    def test_inheritance_from_many(self):
        base = self.add_endpoint_sip()
        base.endpoint_section_options = [('foo', 'bar')]
        base.auth_section_options = [('username', 'Bart')]

        templates = [base]
        for identifier in ('A', 'B', 'C', 'D', 'E'):
            endpoint = self.add_endpoint_sip(templates=[templates[-1]])
            endpoint.endpoint_section_options = [(f'template{identifier}', True)]
            templates.append(endpoint)

        sip = self.add_endpoint_sip(templates=[templates[-1]])

        assert_that(sip._options_dfs('foo', 'endpoint'), equal_to('bar'))
        assert_that(sip._options_dfs('username', 'auth'), equal_to('Bart'))
        assert_that(sip._options_dfs('templateA', 'endpoint'), equal_to(True))
        assert_that(sip._options_dfs('templateB', 'endpoint'), equal_to(True))
        assert_that(sip._options_dfs('templateC', 'endpoint'), equal_to(True))
        assert_that(sip._options_dfs('templateD', 'endpoint'), equal_to(True))
        assert_that(sip._options_dfs('templateE', 'endpoint'), equal_to(True))

    def test_sql_expression(self):
        option = EndpointSIP._options_dfs_sql

        sip_1 = self.add_endpoint_sip(label='1')
        sip_1.endpoint_section_options = [('key_1', 'value_1'), ('key_2', 'value_2')]
        sip_1.auth_section_options = [('foo', 'bar')]
        sip_1.outbound_auth_section_options = [('key_3', 'value_3')]

        sip_2 = self.add_endpoint_sip(label='2')
        sip_2.aor_section_options = [('fooz', 'baz')]
        sip_2.auth_section_options = []

        sip_3 = self.add_endpoint_sip(label='3')
        sip_3.registration_section_options = [('registration_1', 'test')]
        sip_3.endpoint_section_options = [('key_3', 'value_4')]

        scenarios = (
            (option('foo', 'auth') == 'bar', (sip_1,)),
            (option('fooz', 'aor') == 'baz', (sip_2,)),
            (option('key_3', 'outbound_auth') == 'value_3', (sip_1,)),
            (option('registration_1', 'registration') == 'test', (sip_3,)),
            (option('invalid', 'endpoint') == '?', None),
            (option('key_3').ilike('%value_%'), (sip_1, sip_3)),
        )

        for id_, (filter, expected) in enumerate(scenarios, 1):
            result = self.session.query(EndpointSIP).filter(filter).all()
            matcher = contains_inanyorder(*expected) if expected else empty()
            assert_that(result, matcher, f'scenario #{id_} failed')
