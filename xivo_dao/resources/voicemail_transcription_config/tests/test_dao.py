# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import uuid

from hamcrest import (
    assert_that,
    calling,
    equal_to,
    has_properties,
    none,
    not_none,
    raises,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.inspection import inspect

from xivo_dao.alchemy.voicemail_transcription_config import VoicemailTranscriptionConfig
from xivo_dao.helpers.exception import InputError, NotFoundError
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao

UNKNOWN_UUID = uuid.uuid4()


class TestFindBy(DAOTestCase):
    def test_given_column_does_not_exist_then_raise_error(self):
        self.assertRaises(InputError, dao.find_by, column=1)

    def test_given_row_does_not_exist_then_returns_null(self):
        result = dao.find_by(tenant_uuid='nonexistent')
        assert_that(result, none())

    def test_find_by(self):
        config = self.add_voicemail_transcription_config()
        result = dao.find_by(tenant_uuid=config.tenant_uuid)
        assert_that(result.uuid, equal_to(config.uuid))

    def test_find_by_multi_tenant(self):
        tenant = self.add_tenant()

        config = self.add_voicemail_transcription_config()
        result = dao.find_by(tenant_uuid=config.tenant_uuid, tenant_uuids=[tenant.uuid])
        assert_that(result, none())

        config = self.add_voicemail_transcription_config(tenant_uuid=tenant.uuid)
        result = dao.find_by(tenant_uuid=config.tenant_uuid, tenant_uuids=[tenant.uuid])
        assert_that(result, equal_to(config))


class TestGet(DAOTestCase):
    def test_given_no_rows_then_raises_error(self):
        self.assertRaises(NotFoundError, dao.get, UNKNOWN_UUID)

    def test_given_row_then_returns_model(self):
        row = self.add_voicemail_transcription_config()

        model = dao.get(row.uuid)
        assert_that(
            model,
            has_properties(
                uuid=row.uuid,
                tenant_uuid=self.default_tenant.uuid,
                enabled=False,
            ),
        )

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()

        row = self.add_voicemail_transcription_config(tenant_uuid=tenant.uuid)
        model = dao.get(row.uuid, tenant_uuids=[tenant.uuid])
        assert_that(model, equal_to(row))

        row = self.add_voicemail_transcription_config()
        self.assertRaises(
            NotFoundError,
            dao.get,
            row.uuid,
            tenant_uuids=[tenant.uuid],
        )


class TestCreate(DAOTestCase):
    def test_create(self):
        model = VoicemailTranscriptionConfig(
            tenant_uuid=self.default_tenant.uuid,
        )

        result = dao.create(model)

        assert_that(inspect(result).persistent)
        assert_that(
            result,
            has_properties(
                uuid=not_none(),
                tenant_uuid=self.default_tenant.uuid,
                enabled=False,
            ),
        )

    def test_create_with_enabled(self):
        model = VoicemailTranscriptionConfig(
            tenant_uuid=self.default_tenant.uuid,
            enabled=True,
        )

        result = dao.create(model)

        assert_that(
            result,
            has_properties(
                enabled=True,
            ),
        )

    def test_unique_constraint_on_tenant_uuid(self):
        self.add_voicemail_transcription_config()

        model = VoicemailTranscriptionConfig(
            tenant_uuid=self.default_tenant.uuid,
        )
        assert_that(
            calling(dao.create).with_args(model),
            raises(IntegrityError),
        )


class TestEdit(DAOTestCase):
    def test_edit_enabled(self):
        row = self.add_voicemail_transcription_config()

        model = dao.get(row.uuid)
        model.enabled = True
        dao.edit(model)

        self.session.expire_all()
        assert_that(
            model,
            has_properties(
                uuid=row.uuid,
                enabled=True,
            ),
        )


class TestDelete(DAOTestCase):
    def test_delete(self):
        model = self.add_voicemail_transcription_config()

        dao.delete(model)

        assert_that(inspect(model).deleted)
