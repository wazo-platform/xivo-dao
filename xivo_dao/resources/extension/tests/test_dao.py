# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from hamcrest import assert_that, all_of, equal_to, has_items, has_length, has_property, none, contains
from sqlalchemy.exc import SQLAlchemyError

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.extension import Extension as ExtensionSchema
from xivo_dao.helpers.exception import DataError
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.resources.extension import dao as extension_dao
from xivo_dao.resources.extension.model import Extension, \
    ServiceExtension, ForwardExtension, AgentActionExtension
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.helpers.session import mocked_dao_session


class TestExtension(DAOTestCase):

    def prepare_extension(self, **kwargs):
        extension_row = self.add_extension(**kwargs)
        return Extension(id=extension_row.id,
                         exten=extension_row.exten,
                         context=extension_row.context,
                         commented=bool(extension_row.commented))

    def assert_search_returns_result(self, search_result, **parameters):
        result = extension_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


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
        self.extension1 = self.prepare_extension(exten='1000')
        self.extension2 = self.prepare_extension(exten='1001')
        self.extension3 = self.prepare_extension(exten='1002')
        self.extension4 = self.prepare_extension(exten='1103')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.extension2])

        self.assert_search_returns_result(expected, search='1001')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4, [self.extension1, self.extension2, self.extension3, self.extension4])

        self.assert_search_returns_result(expected, order='exten')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(4, [self.extension4, self.extension3, self.extension2, self.extension1])

        self.assert_search_returns_result(expected, order='exten', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.extension1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_skipping_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.extension2, self.extension3, self.extension4])

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


class TestFindByExten(DAOTestCase):

    def test_find_by_exten_no_extens(self):
        expected = []
        extens = extension_dao.find_by_exten('123')

        assert_that(extens, equal_to(expected))

    def test_find_by_exten(self):
        expected_exten = '1234'

        exten = self.add_extension(exten=expected_exten)
        self.add_extension(exten='1236')
        self.add_extension(exten='8652')

        extens = extension_dao.find_by_exten(expected_exten)

        assert_that(extens, has_length(1))
        assert_that(extens, has_items(
            all_of(
                has_property('id', exten.id),
                has_property('exten', expected_exten))
        ))


class TestFindByContext(DAOTestCase):

    def test_find_by_context_no_extens(self):
        expected = []
        extens = extension_dao.find_by_context('fuh')

        assert_that(extens, equal_to(expected))

    def test_find_by_context(self):
        expected_context = 'hhi'

        exten = self.add_extension(context=expected_context)
        self.add_extension(context='guj')
        self.add_extension(context='asc')

        extens = extension_dao.find_by_context(expected_context)

        assert_that(extens, has_length(1))
        assert_that(extens, has_items(
            all_of(
                has_property('id', exten.id),
                has_property('context', expected_context))
        ))


class TestGet(DAOTestCase):

    def test_get_no_exist(self):
        self.assertRaises(NotFoundError, extension_dao.get, 666)

    def test_get(self):
        exten = 'sdklfj'

        expected_extension = self.add_extension(exten=exten)

        extension = extension_dao.get(expected_extension.id)

        assert_that(extension.exten, equal_to(exten))


class TestGetByExten(DAOTestCase):

    def test_get_by_exten_context_no_exist(self):
        self.assertRaises(NotFoundError, extension_dao.get_by_exten_context, '1234', 'default')

    def test_get_by_exten_context(self):
        exten = 'sdklfj'
        context = 'toto'

        expected_extension = self.add_extension(exten=exten,
                                                context=context)

        extension = extension_dao.get_by_exten_context(exten, context)

        assert_that(extension.id, equal_to(expected_extension.id))
        assert_that(extension.exten, equal_to(exten))
        assert_that(extension.context, equal_to(context))


class TestFindByExtenContext(DAOTestCase):

    def test_find_by_exten_context_no_extensions(self):
        expected = None
        result = extension_dao.find_by_exten_context('1000', 'default')

        assert_that(expected, equal_to(result))

    def test_find_by_exten_context_one_extension(self):
        exten = 'sdklfj'
        context = 'toto'
        extension_row = self.add_extension(exten=exten,
                                           context=context)

        result = extension_dao.find_by_exten_context(exten, context)

        assert_that(result, all_of(
            has_property('id', extension_row.id),
            has_property('exten', exten),
            has_property('context', context)
        ))


class TestCreate(DAOTestCase):

    def test_create(self):
        exten = 'extension'
        context = 'toto'
        commented = True

        extension = Extension(exten=exten,
                              context=context,
                              commented=commented)

        created_extension = extension_dao.create(extension)

        row = self.session.query(ExtensionSchema).filter(ExtensionSchema.id == created_extension.id).first()

        assert_that(row.id, equal_to(created_extension.id))
        assert_that(row.exten, equal_to(exten))
        assert_that(row.context, equal_to(context))
        assert_that(row.commented, equal_to(1))
        assert_that(row.type, equal_to('user'))
        assert_that(row.typeval, equal_to('0'))

    def test_create_same_exten_and_context(self):
        exten = 'extension'
        context = 'toto'

        extension = Extension(exten=exten,
                              context=context)

        extension_dao.create(extension)

        extension = Extension(exten=exten,
                              context=context)

        self.assertRaises(DataError, extension_dao.create, extension)

    @mocked_dao_session
    def test_create_extension_with_error_from_dao(self, session):
        session.commit.side_effect = SQLAlchemyError()

        exten = 'extension'
        context = 'toto'

        extension = Extension(exten=exten,
                              context=context)

        self.assertRaises(DataError, extension_dao.create, extension)
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()


class TestEdit(DAOTestCase):

    def setUp(self):
        DAOTestCase.setUp(self)
        self.existing_extension = self.add_extension(exten='1635', context='my_context', type='user', typeval='0')

    def test_edit(self):
        exten = 'extension'
        context = 'toto'
        commented = True

        extension = Extension(id=self.existing_extension.id,
                              exten=exten,
                              context=context,
                              commented=commented)

        extension_dao.edit(extension)

        row = self.session.query(ExtensionSchema).get(extension.id)

        assert_that(row.id, equal_to(extension.id))
        assert_that(row.exten, equal_to(exten))
        assert_that(row.context, equal_to(context))
        assert_that(row.commented, equal_to(1))
        assert_that(row.type, equal_to('user'))
        assert_that(row.typeval, equal_to('0'))

    @mocked_dao_session
    def test_edit_extension_with_error_from_dao(self, session):
        session.commit.side_effect = SQLAlchemyError()

        extension = Extension(exten='extension',
                              context='context')

        self.assertRaises(DataError, extension_dao.edit, extension)
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()


class TestDelete(DAOTestCase):

    def test_delete(self):
        exten = 'sdklfj'
        context = 'toto'

        expected_extension = self.add_extension(exten=exten,
                                                context=context)

        extension = extension_dao.get(expected_extension.id)

        extension_dao.delete(extension)

        row = self.session.query(ExtensionSchema).filter(ExtensionSchema.id == expected_extension.id).first()

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
                        .query(ExtensionSchema.id)
                        .filter(ExtensionSchema.typeval == service)
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


class TestGetByType(DAOTestCase):

    def test_when_getting_by_type_typeval_then_returns_extension_model(self):
        extension_row = self.add_extension(context='xivo-extrafeatures',
                                           exten='*25',
                                           type='extenfeatures',
                                           typeval='enablednd')

        expected = Extension(id=extension_row.id,
                             exten='*25',
                             context='xivo-extrafeatures')

        result = extension_dao.get_by_type('extenfeatures', 'enablednd')

        assert_that(result, equal_to(expected))

    def test_given_no_extension_when_getting_then_raises_error(self):
        self.assertRaises(NotFoundError, extension_dao.get_by_type, 'extenfeatures', 'bla')

    def test_when_getting_by_group_id_then_returns_extension(self):
        extension_row = self.add_extension(exten='2000',
                                           type='group',
                                           typeval='123')

        expected = Extension(id=extension_row.id,
                             exten='2000',
                             context=extension_row.context)

        result = extension_dao.get_by_group_id(123)

        assert_that(result, equal_to(expected))

    def test_when_getting_by_queue_id_then_returns_extension(self):
        extension_row = self.add_extension(exten='3000',
                                           type='queue',
                                           typeval='123')

        expected = Extension(id=extension_row.id,
                             exten='3000',
                             context=extension_row.context)

        result = extension_dao.get_by_queue_id(123)

        assert_that(result, equal_to(expected))

    def test_when_getting_by_conference_id_then_returns_extension(self):
        extension_row = self.add_extension(exten='4000',
                                           type='meetme',
                                           typeval='123')

        expected = Extension(id=extension_row.id,
                             exten='4000',
                             context=extension_row.context)

        result = extension_dao.get_by_conference_id(123)

        assert_that(result, equal_to(expected))
