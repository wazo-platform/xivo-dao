# Copyright 2014-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import Column
from sqlalchemy.sql import and_, or_, visitors

from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchConfig, SearchSystem

config = SearchConfig(
    table=UserFeatures,
    columns={
        'id': UserFeatures.id,
        'uuid': UserFeatures.uuid,
        'firstname': UserFeatures.firstname,
        'lastname': UserFeatures.lastname,
        'fullname': (UserFeatures.firstname + " " + UserFeatures.lastname),
        'caller_id': UserFeatures.callerid,
        'description': UserFeatures.description,
        'userfield': UserFeatures.userfield,
        'email': UserFeatures.email,
        'mobile_phone_number': UserFeatures.mobilephonenumber,
        'music_on_hold': UserFeatures.musiconhold,
        'outgoing_caller_id': UserFeatures.outcallerid,
        'preprocess_subroutine': UserFeatures.preprocess_subroutine,
        'voicemail_number': Voicemail.mailbox,
        'provisioning_code': LineFeatures.provisioning_code,
        'exten': Extension.exten,
        'extension': Extension.exten,
        'context': Extension.context,
        'username': UserFeatures.loginclient,
        'enabled': UserFeatures.enabled,
        'subscription_type': UserFeatures.subscription_type,
    },
    search=[
        'fullname',
        'caller_id',
        'description',
        'userfield',
        'email',
        'mobile_phone_number',
        'preprocess_subroutine',
        'outgoing_caller_id',
        'exten',
        'username',
        'provisioning_code',
        'subscription_type',
    ],
    default_sort='lastname',
    sort_insensitive=[
        'firstname',
        'lastname',
        'fullname',
        'description',
    ],
)


class UserSearchSystem(SearchSystem):
    def search_from_query_collated(self, query, parameters):
        # `search_from_query_collated` pops `order` off `parameters` before
        # calling `search_from_query`, so the line_presence check there never
        # sees it for this path. Run it here first, on the untouched params.
        if parameters.get('view') == 'line_presence':
            self._reject_unsupported_line_presence_params(parameters)
        return super().search_from_query_collated(query, parameters)

    def search_from_query(self, query, parameters):
        line_presence_view = parameters.get('view') == 'line_presence'
        searching = bool(parameters.get('search') or parameters.get('exten'))

        if line_presence_view:
            # params that require additional joins will generate incorrect results
            # against the line_presence view
            self._reject_unsupported_line_presence_params(parameters)

        if 'uuid' in parameters and isinstance(parameters['uuid'], str):
            uuids = parameters.pop('uuid').split(',')
            query = self._filter_exact_match_uuids(query, uuids)

        if 'exten' in parameters and isinstance(parameters['exten'], str):
            extens = parameters.pop('exten').split(',')
            query = self._filter_exact_match_extens(query, extens)

        if 'mobile_phone_number' in parameters and isinstance(
            parameters['mobile_phone_number'], str
        ):
            extens = parameters.pop('mobile_phone_number').split(',')
            query = self._filter_exact_match_mobile_phone_numbers(query, extens)

        if not line_presence_view or searching:
            query = self._search_on_extension(query)
            if line_presence_view:
                query = query.distinct()
        return super().search_from_query(query, parameters)

    def _reject_unsupported_line_presence_params(self, parameters):
        # `exten` as a filter already forces `_search_on_extension()` via
        # `searching`, so it's safe here even though it's a joined column.
        for name, value in parameters.items():
            if name == 'exten':
                continue
            column = self.config.column_for_searching(name)
            if column is not None and self._requires_extension_join(column):
                raise errors.invalid_query_parameter(name, value)

        order = parameters.get('order')
        if order:
            column = self.config.column_for_searching(order)
            if column is not None and self._requires_extension_join(column):
                raise errors.invalid_query_parameter('order', order)

    @staticmethod
    def _requires_extension_join(column):
        # need to handle actual Column objects as well as column expressions
        # which don't have .table
        table = getattr(column, 'table', None)
        if table is not None:
            return table is not UserFeatures.__table__
        tables = {
            elem.table for elem in visitors.iterate(column) if isinstance(elem, Column)
        }
        return any(table is not UserFeatures.__table__ for table in tables)

    def _filter_exact_match_uuids(self, query, uuids):
        column = self.config.column_for_searching('uuid')
        return query.filter(or_(column == uuid for uuid in uuids))

    def _filter_exact_match_extens(self, query, extens):
        column = self.config.column_for_searching('exten')
        return query.filter(or_(column == exten for exten in extens))

    def _filter_exact_match_mobile_phone_numbers(self, query, extens):
        column = self.config.column_for_searching('mobile_phone_number')
        return query.filter(or_(column == exten for exten in extens))

    def _search_on_extension(self, query):
        return (
            query.outerjoin(
                UserLine,
                and_(
                    UserLine.user_id == UserFeatures.id,
                    UserLine.main_line == True,  # noqa
                ),
            )
            .outerjoin(
                LineFeatures,
                and_(LineFeatures.id == UserLine.line_id, LineFeatures.commented == 0),
            )
            .outerjoin(LineExtension, UserLine.line_id == LineExtension.line_id)
            .outerjoin(
                Extension,
                and_(
                    LineExtension.extension_id == Extension.id,
                    LineExtension.main_extension == True,  # noqa
                    Extension.commented == 0,
                ),
            )
            .outerjoin(
                Voicemail,
                and_(
                    UserFeatures.voicemailid == Voicemail.uniqueid,
                    Voicemail.commented == 0,
                ),
            )
        )


user_search = UserSearchSystem(config)
