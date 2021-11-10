# -*- coding: utf-8 -*-
# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries, instance_of, calling, not_, raises
from sqlalchemy import select, Table
from sqlalchemy.exc import InvalidRequestError

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.helpers.db_views import MaterializedView, create_materialized_view


class TestCreateMaterializedView(DAOTestCase):
    def test_create_materialized_view(self):
        result = create_materialized_view('test', select([1]))
        assert_that(result, has_entries(table=instance_of(Table), dependencies=[]))

    def test_create_materialized_view_with_no_name(self):
        assert_that(
            calling(create_materialized_view).with_args(None, select([1])),
            raises(ValueError),
        )

    def test_create_materialized_view_with_no_selectable(self):
        assert_that(
            calling(create_materialized_view).with_args('testview', None),
            raises(ValueError),
        )

    def test_create_materialized_view_with_invalid_selector(self):
        assert_that(
            calling(create_materialized_view).with_args('testview', 'invalid'),
            raises(ValueError),
        )

    def test_create_materialized_view_with_invalid_dependencies(self):
        assert_that(
            calling(create_materialized_view).with_args(
                'testview', select([1]), dependencies=[Table]
            ),
            raises(ValueError),
        )


class TestMaterializedView(DAOTestCase):
    def _create_view_class(
        self, view, name=None, selectable=None, dependencies=None, indexes=None
    ):
        class _(MaterializedView):
            __view__ = (
                view(name, selectable, dependencies=dependencies, indexes=indexes)
                if callable(view)
                else view
            )

        return _

    def test_view_init_table(self):
        assert_that(
            calling(self._create_view_class).with_args(
                create_materialized_view, 'test', select([1])
            ),
            not_(raises(InvalidRequestError)),
        )

    def test_view_init_with_none(self):
        assert_that(
            calling(self._create_view_class).with_args(None),
            raises(InvalidRequestError),
        )

    def test_view_init_with_invalid_view(self):
        assert_that(
            calling(self._create_view_class).with_args(
                {'table': None, 'dependencies': None}
            ),
            raises(InvalidRequestError),
        )

    def test_view_init_without_view_attribute(self):
        def _create_class():
            class _(MaterializedView):
                pass

            return _

        assert_that(calling(_create_class), raises(InvalidRequestError))
