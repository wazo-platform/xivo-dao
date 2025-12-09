# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.extension import Extension as ExtensionTable
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.helpers.db_manager import daosession


@daosession
def get_interface_from_exten_and_context(session, extension, context):
    res = (
        session.query(
            LineFeatures.endpoint_sip_uuid,
            LineFeatures.endpoint_sccp_id,
            LineFeatures.endpoint_custom_id,
            LineFeatures.name,
            UserLine.main_line,
        )
        .join(LineExtension, LineExtension.line_id == LineFeatures.id)
        .join(ExtensionTable, LineExtension.extension_id == ExtensionTable.id)
        .outerjoin(UserLine, UserLine.line_id == LineFeatures.id)
        .filter(ExtensionTable.exten == extension)
        .filter(ExtensionTable.context == context)
    )

    interface = None
    for row in res.all():
        interface = _format_interface(row)
        if row.main_line:
            return interface

    if not interface:
        raise LookupError(f'no line with extension {extension} and context {context}')

    return interface


@daosession
def get_interfaces_from_exten_and_context(session, extension, context):
    res = (
        session.query(
            LineFeatures.endpoint_sip_uuid,
            LineFeatures.endpoint_sccp_id,
            LineFeatures.endpoint_custom_id,
            LineFeatures.name,
        )
        .join(LineExtension, LineExtension.line_id == LineFeatures.id)
        .join(ExtensionTable, LineExtension.extension_id == ExtensionTable.id)
        .outerjoin(UserLine, UserLine.line_id == LineFeatures.id)
        .filter(ExtensionTable.exten == extension)
        .filter(ExtensionTable.context == context)
    )

    interfaces = [_format_interface(row) for row in res.all()]

    if not interfaces:
        raise LookupError(f'no line with extension {extension} and context {context}')

    return interfaces


@daosession
def get_interface_from_line_id(session, line_id):
    query = session.query(
        LineFeatures.endpoint_sip_uuid,
        LineFeatures.endpoint_sccp_id,
        LineFeatures.endpoint_custom_id,
        LineFeatures.name,
    ).filter(LineFeatures.id == line_id)

    line_row = query.first()

    if not line_row:
        raise LookupError(f'no line with id {line_id}')

    return _format_interface(line_row)


@daosession
def get_main_extension_context_from_line_id(session, line_id):
    query = (
        session.query(ExtensionTable.exten, ExtensionTable.context)
        .join(LineExtension, LineExtension.extension_id == ExtensionTable.id)
        .filter(LineExtension.line_id == line_id)
        .filter(LineExtension.main_extension.is_(True))
    )

    line_row = query.first()
    return line_row


@daosession
def is_line_owned_by_user(session, user_uuid, line_id):
    query = (
        session.query(UserLine)
        .join(UserFeatures)
        .filter(UserLine.line_id == line_id)
        .filter(UserFeatures.uuid == user_uuid)
    )

    user_line_row = query.first()
    return user_line_row is not None


def _format_interface(row):
    if row.endpoint_sip_uuid:
        return f'PJSIP/{row.name}'
    elif row.endpoint_sccp_id:
        return f'SCCP/{row.name}'
    elif row.endpoint_custom_id:
        return row.name
