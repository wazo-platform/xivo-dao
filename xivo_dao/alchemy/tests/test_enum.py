# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.types import Enum

import xivo_dao.alchemy.all  # noqa: F401 - load every model so all enums register
from xivo_dao.helpers.db_manager import Base


def test_metadata_bound_enums_have_consistent_value_orders():
    declarations: dict[str, set[tuple[str, ...]]] = {}
    for table in Base.metadata.tables.values():
        for column in table.columns:
            column_type = column.type
            if isinstance(column_type, Enum) and column_type.name:
                declarations.setdefault(column_type.name, set()).add(
                    tuple(column_type.enums)
                )

    conflicts = {
        name: orders for name, orders in declarations.items() if len(orders) > 1
    }
    assert not conflicts, (
        "Enum types declared with conflicting value orders across modules; "
        "define each enum once (e.g. in xivo_dao/alchemy/enum.py) and reuse it: "
        f"{conflicts}"
    )
