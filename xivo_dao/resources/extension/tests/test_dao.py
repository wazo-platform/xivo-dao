# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from hamcrest import assert_that, all_of, equal_to, has_items, has_property, none, contains, has_properties, contains_inanyorder

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.extension import Extension
from xivo_dao.helpers.exception import NotFoundError, InputError
from xivo_dao.resources.extension import dao as extension_dao
from xivo_dao.resources.extension.model import ServiceExtension, ForwardExtension, AgentActionExtension
from xivo_dao.resources.utils.search import SearchResult


class TestExtension(DAOTestCase):

    def prepare_extension(self, **kwargs):
        extension_row = self.add_extension(**kwargs)
        return Extension(id=extension_row.id,
                         exten=extension_row.exten,
                         context=extension_row.context,
                         commented=bool(extension_row.commented))

    def assert_search_returns_result(self, search_result, **parameters):
        result = extension_dao.search(**parameters)
        expected_extensions = [
            has_properties(id=e.id, exten=e.exten, context=e.context, commented=e.commented)
            for e in search_result.items
        ]
        expected = has_properties(total=search_result.total,
                                  items=contains_inanyorder(*expected_extensions))
        assert_that(result, expected)


class TestSimpleSearch(TestExtension):

    def setUp(self):
        TestExtension.setUp(self)

    def test_given_no_extensions_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_commented_extension_then_returns_one_result(self):
        extension = self.prepare_extension(exten='1000', commented=1)
        expected = SearchResult(1, [extension])

        self.assert_search_returns_result(expected)


class TestSearchGivenMultipleExtensions(TestExtension):

    def setUp(self):
        TestExtension.setUp(self)
        self.extension1 = self.prepare_extension(exten='1000', context='inside')
        self.extension2 = self.prepare_extension(exten='1001', context='inside')
        self.extension3 = self.prepare_extension(exten='1002', context='inside')
        self.extension4 = self.prepare_extension(exten='1103', context='inside')
        self.extension5 = self.prepare_extension(exten='1103', context='default')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.extension2])

        self.assert_search_returns_result(expected, search='1001')

    def test_when_searching_with_a_context(self):
        expected_all_1103 = SearchResult(2, [self.extension4, self.extension5])
        self.assert_search_returns_result(expected_all_1103, search='1103')

        expected_1103_inside = SearchResult(1, [self.extension4])
        self.assert_search_returns_result(expected_1103_inside, search='1103', context='inside')

        expected_all_inside = SearchResult(4, [self.extension1, self.extension2,
                                               self.extension3, self.extension4])
        self.assert_search_returns_result(expected_all_inside, context='inside', order='exten')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4, [self.extension1, self.extension2, self.extension3, self.extension4])

        self.assert_search_returns_result(expected, order='exten', context='inside')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(4, [self.extension4, self.extension3, self.extension2, self.extension1])

        self.assert_search_returns_result(expected, order='exten', direction='desc', context='inside')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(5, [self.extension1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_skipping_then_returns_right_number_of_items(self):
        expected = SearchResult(5, [self.extension2, self.extension3, self.extension4, self.extension5])

        self.assert_search_returns_result(expected, skip=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.extension2])

        self.assert_search_returns_result(expected,
                                          search='100',
                                          order='exten',
                                          direction='desc',
                                          skip=1,
                                          limit=1)


class TestSearchGivenInternalExtensionType(TestExtension):

    def setUp(self):
        TestExtension.setUp(self)

        self.add_context(name='internal_context', contexttype='internal')
        self.extension1 = self.prepare_extension(exten='1000', context='internal_context')
        self.extension2 = self.prepare_extension(exten='1001', context='internal_context')

    def test_when_searching_type_internal_extensions_then_returns_internal_extensions(self):
        expected = SearchResult(2, [self.extension1, self.extension2])

        self.assert_search_returns_result(expected, type='internal')

    def test_when_searching_type_internal_and_limit_then_returns_internal_extensions(self):
        expected = SearchResult(2, [self.extension1])

        self.assert_search_returns_result(expected, type='internal', limit=1)

    def test_when_searching_type_incall_then_returns_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected, type='incall')


class TestSearchGivenIncallExtensionType(TestExtension):

    def setUp(self):
        TestExtension.setUp(self)

        self.add_context(name='incall_context', contexttype='incall')
        self.extension1 = self.prepare_extension(exten='1000', context='incall_context')
        self.extension2 = self.prepare_extension(exten='1001', context='incall_context')

    def test_when_searching_type_internal_then_returns_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected, type='internal')

    def test_when_searching_type_incall_then_returns_incall_extensions(self):
        expected = SearchResult(2, [self.extension1, self.extension2])

        self.assert_search_returns_result(expected, type='incall')

    def test_when_searching_type_incall_and_limit_then_returns_interal_extensions(self):
        expected = SearchResult(2, [self.extension1])

        self.assert_search_returns_result(expected, type='incall', limit=1)


class TestFind(DAOTestCase):

    def test_find_no_extension(self):
        result = extension_dao.find(1)

        assert_that(result, none())

    def test_find(self):
        extension_row = self.add_extension(exten='1234', context='default')

        result = extension_dao.find(extension_row.id)

        assert_that(result, all_of(
            has_property('exten', extension_row.exten),
            has_property('context', extension_row.context)))


class TestFindBy(TestExtension):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, extension_dao.find_by, invalid=42)

    def test_given_extension_does_not_exist_then_returns_null(self):
        extension = extension_dao.find_by(exten='invalid')

        assert_that(extension, none())

    def test_given_extension_exists_then_returns_extension(self):
        row = self.add_extension(exten='1000')

        result = extension_dao.find_by(exten='1000')

        assert_that(result.id, equal_to(row.id))


class TestGetBy(TestExtension):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, extension_dao.get_by, invalid=42)

    def test_given_extension_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, extension_dao.get_by, exten='42')

    def test_given_extension_exists_then_returns_extension(self):
        row = self.add_extension(exten='1000')

        result = extension_dao.find_by(exten='1000')

        assert_that(result.id, equal_to(row.id))


class TestFindAllBy(TestExtension):

    def test_find_all_by_no_extensions(self):
        result = extension_dao.find_all_by(exten='invalid')

        assert_that(result, contains())

    def test_find_all_by_native_column(self):
        extension1 = self.add_extension(exten='1000', context='mycontext')
        extension2 = self.add_extension(exten='1001', context='mycontext')

        extensions = extension_dao.find_all_by(context='mycontext')

        assert_that(extensions, has_items(has_property('id', extension1.id),
                                          has_property('id', extension2.id)))


class TestGet(DAOTestCase):

    def test_get_no_exist(self):
        self.assertRaises(NotFoundError, extension_dao.get, 666)

    def test_get(self):
        exten = 'sdklfj'

        expected_extension = self.add_extension(exten=exten)

        extension = extension_dao.get(expected_extension.id)

        assert_that(extension.exten, equal_to(exten))


class TestCreate(DAOTestCase):

    def test_create(self):
        exten = 'extension'
        context = 'toto'

        extension = Extension(exten=exten,
                              context=context)

        created_extension = extension_dao.create(extension)

        row = self.session.query(Extension).filter(Extension.id == created_extension.id).first()

        assert_that(row.id, equal_to(created_extension.id))
        assert_that(row.exten, equal_to(exten))
        assert_that(row.context, equal_to(context))
        assert_that(row.commented, equal_to(0))
        assert_that(row.type, equal_to('user'))
        assert_that(row.typeval, equal_to('0'))

    def test_create_all_parameters(self):
        extension = Extension(exten='1000',
                              context='default',
                              commented=1)

        created_extension = extension_dao.create(extension)

        row = self.session.query(Extension).filter(Extension.id == created_extension.id).first()

        assert_that(row.id, equal_to(created_extension.id))
        assert_that(row.exten, equal_to('1000'))
        assert_that(row.context, equal_to('default'))
        assert_that(row.commented, equal_to(1))
        assert_that(row.type, equal_to('user'))
        assert_that(row.typeval, equal_to('0'))


class TestEdit(DAOTestCase):

    def setUp(self):
        DAOTestCase.setUp(self)
        self.existing_extension = self.add_extension(exten='1635', context='my_context', type='user', typeval='0')

    def test_edit(self):
        exten = 'extension'
        context = 'toto'
        commented = 1
        row = self.add_extension()

        extension = extension_dao.get(row.id)
        extension.exten = exten
        extension.context = context
        extension.commented = commented

        extension_dao.edit(extension)

        row = self.session.query(Extension).get(extension.id)

        assert_that(row.id, equal_to(extension.id))
        assert_that(row.exten, equal_to(exten))
        assert_that(row.context, equal_to(context))
        assert_that(row.commented, equal_to(1))
        assert_that(row.type, equal_to('user'))
        assert_that(row.typeval, equal_to('0'))


class TestDelete(DAOTestCase):

    def test_delete(self):
        exten = 'sdklfj'
        context = 'toto'

        expected_extension = self.add_extension(exten=exten,
                                                context=context)

        extension = extension_dao.get(expected_extension.id)

        extension_dao.delete(extension)

        row = self.session.query(Extension).filter(Extension.id == expected_extension.id).first()

        self.assertEquals(row, None)


class TestFindAllServiceExtensions(DAOTestCase):

    SERVICES = [("*90", "enablevm"),
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
                ("*25", "enablednd")]

    EXPECTED_SERVICES = [("*90", "enablevm"),
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
                         ("*20", "fwdundoall")]

    def prepare_extensions(self):
        service_extensions = []

        for exten, service in self.SERVICES:
            self.add_extension(type='extenfeatures',
                               context='xivo-features',
                               exten=exten,
                               typeval=service)

        for exten, service in self.EXPECTED_SERVICES:
            exten_id = (self.session
                        .query(Extension.id)
                        .filter(Extension.typeval == service)
                        .scalar())

            service_extension = ServiceExtension(id=exten_id,
                                                 exten=exten,
                                                 service=service)

            service_extensions.append(service_extension)

        return service_extensions

    def test_given_no_extension_then_return_empty_list(self):
        extensions = extension_dao.find_all_service_extensions()

        assert_that(extensions, contains())

    def test_given_all_service_extensions_then_returns_models(self):
        expected = self.prepare_extensions()

        result = extension_dao.find_all_service_extensions()

        assert_that(result, has_items(*expected))

    def test_given_extension_is_commented_then_returns_extension(self):
        extension_row = self.add_extension(type='extenfeatures',
                                           context='xivo-features',
                                           exten='*92',
                                           typeval='vmuserpurge',
                                           commented=1)

        expected = ServiceExtension(id=extension_row.id,
                                    exten=extension_row.exten,
                                    service=extension_row.typeval)

        result = extension_dao.find_all_service_extensions()

        assert_that(result, contains(expected))


class TestFindAllForwardExtensions(DAOTestCase):

    def prepare_extensions(self):
        extensions = []

        row = self.add_extension(type='extenfeatures',
                                 context='xivo-features',
                                 exten='_*23.',
                                 typeval='fwdbusy')
        model = ForwardExtension(id=row.id,
                                 exten='*23',
                                 forward='busy')
        extensions.append(model)

        row = self.add_extension(type='extenfeatures',
                                 context='xivo-features',
                                 exten='_*22.',
                                 typeval='fwdrna')
        model = ForwardExtension(id=row.id,
                                 exten='*22',
                                 forward='noanswer')
        extensions.append(model)

        row = self.add_extension(type='extenfeatures',
                                 context='xivo-features',
                                 exten='_*21.',
                                 typeval='fwdunc')
        model = ForwardExtension(id=row.id,
                                 exten='*21',
                                 forward='unconditional')
        extensions.append(model)

        return extensions

    def test_given_no_extension_then_return_empty_list(self):
        extensions = extension_dao.find_all_forward_extensions()

        assert_that(extensions, contains())

    def test_given_all_forward_extensions_then_returns_models(self):
        expected = self.prepare_extensions()

        result = extension_dao.find_all_forward_extensions()

        assert_that(result, has_items(*expected))

    def test_given_extension_is_commented_then_returns_extension(self):
        extension_row = self.add_extension(type='extenfeatures',
                                           context='xivo-features',
                                           exten='_*23.',
                                           typeval='fwdbusy',
                                           commented=1)

        expected = ForwardExtension(id=extension_row.id,
                                    exten='*23',
                                    forward='busy')

        result = extension_dao.find_all_forward_extensions()

        assert_that(result, contains(expected))


class TestFindAllAgentActionExtensions(DAOTestCase):

    def prepare_extensions(self):
        extensions = []

        row = self.add_extension(type='extenfeatures',
                                 context='xivo-features',
                                 exten='_*31.',
                                 typeval='agentstaticlogin')
        model = AgentActionExtension(id=row.id,
                                     exten='*31',
                                     action='login')
        extensions.append(model)

        row = self.add_extension(type='extenfeatures',
                                 context='xivo-features',
                                 exten='_*32.',
                                 typeval='agentstaticlogoff')
        model = AgentActionExtension(id=row.id,
                                     exten='*32',
                                     action='logout')
        extensions.append(model)

        row = self.add_extension(type='extenfeatures',
                                 context='xivo-features',
                                 exten='_*30.',
                                 typeval='agentstaticlogtoggle')
        model = AgentActionExtension(id=row.id,
                                     exten='*30',
                                     action='toggle')
        extensions.append(model)

        return extensions

    def test_given_no_extension_then_return_empty_list(self):
        extensions = extension_dao.find_all_agent_action_extensions()

        assert_that(extensions, contains())

    def test_given_all_agent_action_extensions_then_returns_models(self):
        expected = self.prepare_extensions()

        result = extension_dao.find_all_agent_action_extensions()

        assert_that(result, has_items(*expected))

    def test_given_extension_is_commented_then_returns_extension(self):
        extension_row = self.add_extension(type='extenfeatures',
                                           context='xivo-features',
                                           exten='_*30.',
                                           typeval='agentstaticlogtoggle',
                                           commented=1)

        expected = AgentActionExtension(id=extension_row.id,
                                        exten='*30',
                                        action='toggle')

        result = extension_dao.find_all_agent_action_extensions()

        assert_that(result, contains(expected))
