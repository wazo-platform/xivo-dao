# Copyright 2021-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from functools import partial
from hamcrest import (
    assert_that,
    instance_of,
    calling,
    not_,
    raises,
    equal_to,
)
from sqlalchemy import select, Table
from sqlalchemy.exc import InvalidRequestError

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.helpers.db_manager import Base
from xivo_dao.helpers.db_views import MaterializedView, create_materialized_view


class TestCreateMaterializedView(DAOTestCase):
    def test_create_materialized_view(self):
        result = create_materialized_view('test', select([1]))
        assert_that(result, instance_of(Table))

    def test_create_materialized_view_with_no_name(self):
        assert_that(
            calling(create_materialized_view).with_args(None, select([1])),
            raises(ValueError)
        )

    def test_create_materialized_view_with_no_selectable(self):
        assert_that(
            calling(create_materialized_view).with_args('testview', None),
            raises(ValueError)
        )

    def test_create_materialized_view_with_invalid_selectable(self):
        assert_that(
            calling(create_materialized_view).with_args('testview', 'invalid'),
            raises(ValueError)
        )

    def test_create_materialized_view_with_invalid_indexes(self):
        assert_that(
            calling(create_materialized_view).with_args(
                'testview', select([1]), indexes=[object()]
            ),
            raises(ValueError)
        )

    def test_create_materialized_view_class(self):
        def create_view():
            class _(MaterializedView):
                __table__ = create_materialized_view('testview', select([1]))

            return _

        view = create_view()
        assert_that(issubclass(view, MaterializedView), equal_to(True))
