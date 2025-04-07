# Copyright 2014-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock

from hamcrest import assert_that, equal_to

from xivo_dao.helpers.exception import InputError
from xivo_dao.resources.utils.view import ModelView, View, ViewSelector


class TestViewSelector(unittest.TestCase):
    def test_given_no_view_name_then_selects_default_view(self):
        view = Mock(View)
        selector = ViewSelector(default=view)

        result = selector.select()

        assert_that(result, equal_to(view))

    def test_given_view_name_then_selects_proper_view(self):
        default_view = Mock(View)
        other_view = Mock(View)
        selector = ViewSelector(default=default_view, other=other_view)

        result = selector.select('other')

        assert_that(result, equal_to(other_view))

    def test_given_view_that_does_not_exist_then_raises_error(self):
        default_view = Mock(View)
        selector = ViewSelector(default=default_view)

        self.assertRaises(InputError, selector.select, 'other')


class TestView(unittest.TestCase):
    def test_given_list_of_rows_then_converts_each_row(self):
        class ConcreteView(View):
            def __init__(self):
                self.count = 0

            def convert(self, row):
                self.count += 1

            def query(self, session):
                pass

        view = ConcreteView()
        view.convert_list([Mock(), Mock()])

        assert_that(view.count, equal_to(2))


class TestModelView(unittest.TestCase):
    def test_given_session_when_queried_then_returns_query_with_table(self):
        mock_table = Mock()
        session = Mock()

        class ConcreteModelView(ModelView):
            table = mock_table
            db_converter = None

        result = ConcreteModelView().query(session)

        assert_that(result, equal_to(session.query.return_value))
        session.query.assert_called_once_with(mock_table)

    def test_given_db_converter_when_row_converted_then_calls_converter(self):
        mock_db_converter = Mock()
        row = Mock()

        class ConcreteModelView(ModelView):
            table = None
            db_converter = mock_db_converter

        result = ConcreteModelView().convert(row)

        assert_that(result, equal_to(mock_db_converter.to_model.return_value))
        mock_db_converter.to_model.assert_called_once_with(row)
