# Copyright 2023-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from uuid import uuid4

from hamcrest import (
    all_of,
    assert_that,
    contains_exactly,
    contains_inanyorder,
    equal_to,
    has_items,
    has_properties,
    has_property,
    none,
)

from xivo_dao.alchemy.feature_extension import FeatureExtension
from xivo_dao.helpers.exception import InputError, NotFoundError
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as feature_extension_dao
from ..database import (
    AgentActionFeatureExtension,
    ForwardFeatureExtension,
    ServiceFeatureExtension,
)


class TestExtension(DAOTestCase):
    def assert_search_returns_result(self, search_result, **parameters):
        result = feature_extension_dao.search(**parameters)
        expected_extensions = [
            has_properties(uuid=e.uuid, exten=e.exten, enabled=e.enabled)
            for e in search_result.items
        ]
        expected = has_properties(
            total=search_result.total, items=contains_inanyorder(*expected_extensions)
        )
        assert_that(result, expected)


class TestSimpleSearch(TestExtension):
    def test_given_no_extensions_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_disabled_feature_extension_then_returns_one_result(self):
        feature_extension = self.add_feature_extension(exten='1000', enabled=False)
        expected = SearchResult(1, [feature_extension])

        self.assert_search_returns_result(expected)

    def test_given_one_feature_extension_then_returns_one_result(self):
        extension1 = self.add_feature_extension(exten='1000')

        expected = SearchResult(1, [extension1])
        self.assert_search_returns_result(expected)


class TestSearchGivenMultipleExtensions(TestExtension):
    def setUp(self):
        TestExtension.setUp(self)
        self.extension1 = self.add_feature_extension(exten='1000')
        self.extension2 = self.add_feature_extension(exten='1001')
        self.extension3 = self.add_feature_extension(exten='1002')
        self.extension4 = self.add_feature_extension(exten='1103')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.extension2])

        self.assert_search_returns_result(expected, search='1001')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(
            4, [self.extension1, self.extension2, self.extension3, self.extension4]
        )

        self.assert_search_returns_result(expected, order='exten')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(
        self,
    ):
        expected = SearchResult(
            4, [self.extension4, self.extension3, self.extension2, self.extension1]
        )

        self.assert_search_returns_result(expected, order='exten', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.extension1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_offset_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.extension2, self.extension3, self.extension4])

        self.assert_search_returns_result(expected, offset=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.extension2])

        self.assert_search_returns_result(
            expected, search='100', order='exten', direction='desc', offset=1, limit=1
        )


class TestFind(TestExtension):
    def test_find_no_extension(self):
        result = feature_extension_dao.find(str(uuid4()))

        assert_that(result, none())

    def test_find(self):
        extension_row = self.add_feature_extension(exten='1234')

        result = feature_extension_dao.find(extension_row.uuid)

        assert_that(
            result,
            all_of(
                has_property('exten', extension_row.exten),
            ),
        )


class TestFindBy(TestExtension):
    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, feature_extension_dao.find_by, invalid=42)

    def test_given_extension_does_not_exist_then_returns_null(self):
        extension = feature_extension_dao.find_by(exten='invalid')

        assert_that(extension, none())

    def test_given_extension_exists_then_returns_extension(self):
        row = self.add_feature_extension(exten='1000')

        result = feature_extension_dao.find_by(exten='1000')

        assert_that(result.uuid, equal_to(row.uuid))


class TestGetBy(TestExtension):
    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, feature_extension_dao.get_by, invalid=42)

    def test_given_extension_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, feature_extension_dao.get_by, exten='42')

    def test_given_extension_exists_then_returns_extension(self):
        row = self.add_feature_extension(exten='1000')

        result = feature_extension_dao.get_by(exten='1000')

        assert_that(result.uuid, equal_to(row.uuid))


class TestFindAllBy(TestExtension):
    def test_find_all_by_no_extensions(self):
        result = feature_extension_dao.find_all_by(exten='invalid')

        assert_that(result, contains_exactly())

    def test_find_all_by_native_column(self):
        extension1 = self.add_feature_extension(exten='1000')
        extension2 = self.add_feature_extension(exten='1001')

        extensions = feature_extension_dao.find_all_by()

        assert_that(
            extensions,
            has_items(
                has_property('uuid', extension1.uuid),
                has_property('uuid', extension2.uuid),
            ),
        )


class TestGet(TestExtension):
    def test_get_no_exist(self):
        self.assertRaises(NotFoundError, feature_extension_dao.get, str(uuid4()))

    def test_get(self):
        exten = 'sdklfj'

        expected_extension = self.add_feature_extension(exten=exten)

        extension = feature_extension_dao.get(expected_extension.uuid)

        assert_that(extension.exten, equal_to(exten))


class TestCreate(TestExtension):
    def test_create(self):
        exten = 'extension'
        feature = 'myfeature'
        extension = FeatureExtension(exten=exten, feature=feature)

        created_extension = feature_extension_dao.create(extension)

        row = (
            self.session.query(FeatureExtension)
            .filter(FeatureExtension.uuid == created_extension.uuid)
            .first()
        )

        assert_that(row.uuid, equal_to(created_extension.uuid))
        assert_that(row.exten, equal_to(exten))
        assert_that(row.enabled, equal_to(True))
        assert_that(row.feature, equal_to(feature))

    def test_create_all_parameters(self):
        feature = 'myfeature'
        extension = FeatureExtension(exten='1000', feature=feature, enabled=False)

        created_extension = feature_extension_dao.create(extension)

        row = (
            self.session.query(FeatureExtension)
            .filter(FeatureExtension.uuid == created_extension.uuid)
            .first()
        )

        assert_that(row.uuid, equal_to(created_extension.uuid))
        assert_that(row.exten, equal_to('1000'))
        assert_that(row.enabled, equal_to(False))
        assert_that(row.feature, equal_to(feature))


class TestEdit(TestExtension):
    def setUp(self):
        super().setUp()
        self.existing_extension = self.add_feature_extension(
            exten='1635', feature='myfeature'
        )

    def test_edit(self):
        exten = 'extension'
        enabled = False
        row = self.add_feature_extension()

        extension = feature_extension_dao.get(row.uuid)
        extension.exten = exten
        extension.enabled = enabled

        feature_extension_dao.edit(extension)

        row = self.session.get(FeatureExtension, extension.uuid)

        assert_that(row.uuid, equal_to(extension.uuid))
        assert_that(row.exten, equal_to(exten))
        assert_that(row.enabled, equal_to(False))
        assert_that(row.feature, equal_to(''))


class TestDelete(TestExtension):
    def test_delete(self):
        exten = 'sdklfj'

        expected_extension = self.add_feature_extension(exten=exten)

        extension = feature_extension_dao.get(expected_extension.uuid)

        feature_extension_dao.delete(extension)

        row = (
            self.session.query(FeatureExtension)
            .filter(FeatureExtension.uuid == expected_extension.uuid)
            .first()
        )

        assert row is None


class TestFindAllServiceExtensions(DAOTestCase):
    SERVICES = [
        ("*90", "enablevm"),
        ("*98", "vmusermsg"),
        ("*92", "vmuserpurge"),
        ("*10", "phonestatus"),
        ("*9", "recsnd"),
        ("*34", "calllistening"),
        ("*36", "directoryaccess"),
        ("*20", "fwdundoall"),
        ("_*8.", "pickup"),
        ("*26", "callrecord"),
        ("*27", "incallfilter"),
        ("*25", "enablednd"),
    ]

    EXPECTED_SERVICES = [
        ("*90", "enablevm"),
        ("*98", "vmusermsg"),
        ("*92", "vmuserpurge"),
        ("*10", "phonestatus"),
        ("*9", "recsnd"),
        ("*34", "calllistening"),
        ("*36", "directoryaccess"),
        ("*20", "fwdundoall"),
        ("*8", "pickup"),
        ("*26", "callrecord"),
        ("*27", "incallfilter"),
        ("*25", "enablednd"),
        ("*20", "fwdundoall"),
    ]

    def add_feature_extensions(self):
        service_extensions = []

        for exten, service in self.SERVICES:
            self.add_feature_extension(exten=exten, feature=service)

        for exten, service in self.EXPECTED_SERVICES:
            exten_uuid = (
                self.session.query(FeatureExtension.uuid)
                .filter(FeatureExtension.feature == service)
                .scalar()
            )

            service_extension = ServiceFeatureExtension(
                uuid=exten_uuid, exten=exten, service=service
            )

            service_extensions.append(service_extension)

        return service_extensions

    def test_given_no_extension_then_return_empty_list(self):
        extensions = feature_extension_dao.find_all_service_extensions()

        assert_that(extensions, contains_exactly())

    def test_given_all_service_extensions_then_returns_models(self):
        expected = self.add_feature_extensions()

        result = feature_extension_dao.find_all_service_extensions()

        assert_that(result, has_items(*expected))

    def test_given_extension_is_disabled_then_returns_extension(self):
        extension_row = self.add_feature_extension(
            exten='*92', feature='vmuserpurge', enabled=False
        )

        expected = ServiceFeatureExtension(
            uuid=extension_row.uuid,
            exten=extension_row.exten,
            service=extension_row.feature,
        )

        result = feature_extension_dao.find_all_service_extensions()

        assert_that(result, contains_exactly(expected))


class TestFindAllForwardExtensions(DAOTestCase):
    def add_feature_extensions(self):
        extensions = []

        row = self.add_feature_extension(exten='_*23.', feature='fwdbusy')
        model = ForwardFeatureExtension(uuid=row.uuid, exten='*23', forward='busy')
        extensions.append(model)

        row = self.add_feature_extension(exten='_*22.', feature='fwdrna')
        model = ForwardFeatureExtension(uuid=row.uuid, exten='*22', forward='noanswer')
        extensions.append(model)

        row = self.add_feature_extension(exten='_*21.', feature='fwdunc')
        model = ForwardFeatureExtension(
            uuid=row.uuid, exten='*21', forward='unconditional'
        )
        extensions.append(model)

        return extensions

    def test_given_no_extension_then_return_empty_list(self):
        extensions = feature_extension_dao.find_all_forward_extensions()

        assert_that(extensions, contains_exactly())

    def test_given_all_forward_extensions_then_returns_models(self):
        expected = self.add_feature_extensions()

        result = feature_extension_dao.find_all_forward_extensions()

        assert_that(result, has_items(*expected))

    def test_given_extension_is_disabled_then_returns_extension(self):
        extension_row = self.add_feature_extension(
            exten='_*23.', feature='fwdbusy', enabled=False
        )

        expected = ForwardFeatureExtension(
            uuid=extension_row.uuid, exten='*23', forward='busy'
        )

        result = feature_extension_dao.find_all_forward_extensions()

        assert_that(result, contains_exactly(expected))


class TestFindAllAgentActionExtensions(DAOTestCase):
    def add_feature_extensions(self):
        extensions = []

        row = self.add_feature_extension(exten='_*31.', feature='agentstaticlogin')
        model = AgentActionFeatureExtension(uuid=row.uuid, exten='*31', action='login')
        extensions.append(model)

        row = self.add_feature_extension(exten='_*32.', feature='agentstaticlogoff')
        model = AgentActionFeatureExtension(uuid=row.uuid, exten='*32', action='logout')
        extensions.append(model)

        row = self.add_feature_extension(exten='_*30.', feature='agentstaticlogtoggle')
        model = AgentActionFeatureExtension(uuid=row.uuid, exten='*30', action='toggle')
        extensions.append(model)

        return extensions

    def test_given_no_extension_then_return_empty_list(self):
        extensions = feature_extension_dao.find_all_agent_action_extensions()

        assert_that(extensions, contains_exactly())

    def test_given_all_agent_action_extensions_then_returns_models(self):
        expected = self.add_feature_extensions()

        result = feature_extension_dao.find_all_agent_action_extensions()

        assert_that(result, has_items(*expected))

    def test_given_extension_is_disabled_then_returns_extension(self):
        extension_row = self.add_feature_extension(
            exten='_*30.', feature='agentstaticlogtoggle', enabled=False
        )

        expected = AgentActionFeatureExtension(
            uuid=extension_row.uuid, exten='*30', action='toggle'
        )

        result = feature_extension_dao.find_all_agent_action_extensions()

        assert_that(result, contains_exactly(expected))
