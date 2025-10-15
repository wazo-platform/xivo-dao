# Copyright 2021-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from collections.abc import Callable, Sequence

from hamcrest import assert_that, calling, equal_to, not_, raises
from sqlalchemy import Column, Index, Integer, MetaData, Table, select
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.sql import Select
from sqlalchemy_utils import create_materialized_view

from xivo_dao.helpers.db_manager import Base
from xivo_dao.helpers.db_views import MaterializedView
from xivo_dao.tests.test_dao import DAOTestCase


def _create_materialized_view_class(
    func: Callable[[str, Select, MetaData, Sequence[Index]], Table],
    name: str = '_',
    selectable: Base | None = None,
    dependencies: tuple[type[Base], ...] | None = None,
    indexes: Sequence[Index] | None = None,
) -> type:
    kwargs = {
        '__table__': func(name, selectable, Base.metadata, indexes)
        if callable(func)
        else func,
    }
    if dependencies:
        kwargs['__view_dependencies__'] = dependencies
    return type(name, (MaterializedView,), kwargs)


class TestMaterializedView(DAOTestCase):
    def test_view_init_table(self):
        assert_that(
            calling(_create_materialized_view_class).with_args(
                create_materialized_view, name='view-init-table', selectable=select(1)
            ),
            not_(raises(InvalidRequestError)),
        )

    def test_view_class_creation(self):
        view = _create_materialized_view_class(
            create_materialized_view, 'view-class-creation', select(1)
        )
        assert_that(issubclass(view, MaterializedView), equal_to(True))

    def test_view_init_with_none(self):
        assert_that(
            calling(_create_materialized_view_class).with_args(None),
            raises(InvalidRequestError),
        )

    def test_view_without_helper_function(self):
        def some_func(name, selectable, metadata, indexes=None):
            return 'bad return'

        assert_that(
            calling(_create_materialized_view_class).with_args(
                some_func, 'view-without-helper-function', select(1)
            ),
            raises(InvalidRequestError),
        )

    def test_view_init_with_invalid_view(self):
        assert_that(
            calling(_create_materialized_view_class).with_args(
                ('view-init-with-invalid-view', None)
            ),
            raises(InvalidRequestError),
        )

    def test_view_init_without_view_attribute(self):
        def _create_class():
            return type('TestMaterializedView', (MaterializedView,), {})

        assert_that(calling(_create_class), raises(InvalidRequestError))

    def test_view_dependencies_event_correctly_bound(self):
        class MockModel(Base):
            __tablename__ = 'mock_model'
            id = Column(Integer, primary_key=True)

        view = _create_materialized_view_class(
            create_materialized_view,
            'view-deps-event-found',
            select(1),
            dependencies=(MockModel,),
        )
        assert_that(view.autorefresh, equal_to(True))

    def test_view_dependencies_no_event_bound(self):
        view = _create_materialized_view_class(
            create_materialized_view, 'view-deps-no-event-found', select(1)
        )
        assert_that(view.autorefresh, equal_to(False))
