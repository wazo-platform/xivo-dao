# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.sql import and_, cast
from sqlalchemy.sql.sqltypes import String

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.incall import Incall
from xivo_dao.alchemy.switchboard import Switchboard
from xivo_dao.resources.utils.search import SearchConfig, SearchSystem

config = SearchConfig(
    table=Switchboard,
    columns={
        "name": Switchboard.name,
        "exten": Incall.exten,
    },
    search=[
        "name",
        "exten",
    ],
    sort=[
        "name",
    ],
    default_sort="name",
)


class SwitchboardSearchSystem(SearchSystem):
    def _search_on_extension(self, query):
        return (
            query.outerjoin(
                Dialaction,
                and_(
                    Dialaction.action == "switchboard",
                    Dialaction.actionarg1 == Switchboard.uuid,
                ),
            )
            .outerjoin(
                Incall,
                and_(
                    Dialaction.category == "incall",
                    Dialaction.categoryval == cast(Incall.id, String),
                    Incall.commented == 0,
                ),
            )
            .group_by(Switchboard)
        )

    def search_from_query(self, query, parameters):
        query = self._search_on_extension(query)
        return super().search_from_query(query, parameters)


switchboard_search = SwitchboardSearchSystem(config)
