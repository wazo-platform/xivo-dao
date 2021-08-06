# -*- coding: utf-8 -*-
# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import six
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.line_extension import LineExtension
from sqlalchemy.sql.elements import and_, or_
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(table=LineFeatures,
                      columns={'context': LineFeatures.context,
                               'provisioning_code': LineFeatures.provisioningid,
                               'provisioning_extension': LineFeatures.provisioningid,
                               'position': LineFeatures.num,
                               'device_slot': LineFeatures.num,
                               'protocol': LineFeatures.protocol,
                               'device_id': LineFeatures.device,
                               'name': LineFeatures.name,
                               'caller_id_name': LineFeatures.caller_id_name,
                               'caller_id_num': LineFeatures.caller_id_num,
                               'exten': Extension.exten},
                      default_sort='name')


class LineSearchSystem(SearchSystem):

    def search_from_query(self, query, parameters):
        if 'exten' in parameters and isinstance(parameters['exten'], (str, six.text_type)):
            extens = parameters.pop('exten').split(',')
            query = self._filter_exact_match_extens(query, extens)

        query = self._search_on_extension(query)
        return super(LineSearchSystem, self).search_from_query(query, parameters)

    def _filter_exact_match_extens(self, query, extens):
        column = self.config.column_for_searching('extens')
        return query.filter(or_(column == exten for exten in extens))

    def _search_on_extension(self, query):
        return (
            query
            .outerjoin(LineExtension,
                       and_(LineExtension.line_id == LineFeatures.id,
                            LineFeatures.commented == 0))
            .outerjoin(Extension,
                       and_(LineExtension.extension_id == Extension.id,
                            LineExtension.line_id == LineFeatures.id,
                            Extension.commented == 0)))


line_search = LineSearchSystem(config)
