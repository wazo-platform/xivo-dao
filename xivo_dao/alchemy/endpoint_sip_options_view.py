# -*- coding: utf-8 -*-
# Copyright 2020-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import select, join, cast, literal, func, String, Index, text
from sqlalchemy.dialects.postgresql import JSONB, aggregate_order_by

from xivo_dao.helpers.db_views import MaterializedView, create_materialized_view

from xivo_dao.alchemy import (
    EndpointSIP,
    EndpointSIPSection,
    EndpointSIPSectionOption,
    EndpointSIPTemplate,
)


def _generate_selectable():
    cte = select(
        [
            EndpointSIP.uuid.label('uuid'),
            literal(0).label('level'),
            literal('0', String).label('path'),
            EndpointSIP.uuid.label('root'),
        ]
    ).cte(recursive=True)

    endpoints = cte.union(
        select(
            [
                EndpointSIPTemplate.parent_uuid.label('uuid'),
                (cte.c.level + 1).label('level'),
                (
                    cte.c.path
                    + cast(
                        func.row_number().over(
                            partition_by='level',
                            order_by=EndpointSIPTemplate.priority,
                        ),
                        String,
                    )
                ).label('path'),
                (cte.c.root),
            ]
        ).select_from(
            join(
                cte,
                EndpointSIPTemplate,
                cte.c.uuid == EndpointSIPTemplate.child_uuid,
            )
        )
    )

    return (
        select(
            [
                cast(
                    func.jsonb_object(
                        func.array_agg(
                            aggregate_order_by(
                                EndpointSIPSectionOption.key,
                                endpoints.c.path.desc(),
                            )
                        ),
                        func.array_agg(
                            aggregate_order_by(
                                EndpointSIPSectionOption.value,
                                endpoints.c.path.desc(),
                            )
                        ),
                    ),
                    JSONB,
                ).label('options'),
                endpoints.c.root,
            ]
        )
        .select_from(
            join(
                endpoints,
                EndpointSIPSection,
                EndpointSIPSection.endpoint_sip_uuid == endpoints.c.uuid,
            ).join(
                EndpointSIPSectionOption,
                EndpointSIPSectionOption.endpoint_sip_section_uuid
                == EndpointSIPSection.uuid,
            )
        )
        .group_by('root')
    )


class EndpointSIPOptionsView(MaterializedView):
    __view__ = create_materialized_view(
        'endpoint_sip_options_view',
        _generate_selectable(),
        dependencies=[EndpointSIPSectionOption],
        indexes=[
            Index('endpoint_sip_options_view__idx_root', text('root'), unique=True),
        ],
    )

    @classmethod
    def get_option_value(cls, option):
        return cls.options[option].astext
