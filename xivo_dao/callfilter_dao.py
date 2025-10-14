# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.sql.expression import and_, cast, func, select
from sqlalchemy.types import Integer

from xivo_dao.alchemy.callfilter import Callfilter
from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.alchemy.extension import Extension as ExtensionSchema
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.helpers.db_manager import daosession


@daosession
def does_secretary_filter_boss(session, boss_user_id, secretary_user_id):
    boss_members = (
        select(Callfiltermember.callfilterid)
        .where(Callfiltermember.bstype == 'boss')
        .where(Callfiltermember.typeval == str(boss_user_id))
    )

    query = (
        session.query(Callfiltermember.id)
        .filter(Callfiltermember.typeval == str(secretary_user_id))
        .filter(Callfiltermember.bstype == 'secretary')
        .filter(Callfiltermember.callfilterid.in_(boss_members))
    )

    return query.count()


@daosession
def get(session, callfilter_id):
    return (
        session.query(Callfilter, Callfiltermember)
        .join((Callfiltermember, Callfilter.id == Callfiltermember.callfilterid))
        .filter(Callfilter.id == callfilter_id)
        .all()
    )


@daosession
def get_secretaries_id_by_context(session, context):
    return (
        session.query(Callfiltermember.id)
        .join(
            UserLine,
            and_(
                UserLine.user_id == cast(Callfiltermember.typeval, Integer),
                UserLine.main_user == True,  # noqa
                UserLine.main_line == True,  # noqa
            ),
        )
        .join(
            LineExtension,
            and_(
                UserLine.line_id == LineExtension.line_id,
                LineExtension.main_extension == True,  # noqa
            ),
        )
        .join(
            ExtensionSchema,
            and_(
                ExtensionSchema.context == context,
                LineExtension.extension_id == ExtensionSchema.id,
            ),
        )
        .filter(
            and_(
                Callfiltermember.type == 'user', Callfiltermember.bstype == 'secretary'
            )
        )
        .all()
    )


@daosession
def get_secretaries_by_callfiltermember_id(session, callfiltermember_id):
    return (
        session.query(Callfiltermember, UserFeatures.ringseconds)
        .join((Callfilter, Callfilter.id == Callfiltermember.callfilterid))
        .join(
            (UserFeatures, UserFeatures.id == cast(Callfiltermember.typeval, Integer))
        )
        .filter(
            and_(
                Callfilter.id == callfiltermember_id,
                Callfiltermember.bstype == 'secretary',
            )
        )
        .order_by(Callfiltermember.priority.asc())
        .all()
    )


@daosession
def get_by_callfiltermember_id(session, callfiltermember_id):
    return (
        session.query(Callfiltermember)
        .filter(Callfiltermember.id == callfiltermember_id)
        .first()
    )


@daosession
def find_boss(session, boss_id):
    return (
        session.query(Callfiltermember)
        .filter(
            and_(
                Callfiltermember.typeval == str(boss_id),
                Callfiltermember.bstype == 'boss',
            )
        )
        .first()
    )


@daosession
def find(session, call_filter_id):
    return session.query(Callfilter).filter(Callfilter.id == call_filter_id).first()


@daosession
def is_activated_by_callfilter_id(session, callfilter_id):
    return (
        session.query(func.count(Callfiltermember.active))
        .join((Callfilter, Callfilter.id == Callfiltermember.callfilterid))
        .filter(
            and_(
                Callfiltermember.callfilterid == callfilter_id,
                Callfiltermember.bstype == 'secretary',
                Callfiltermember.active == 1,
            )
        )
        .first()[0]
    )


@daosession
def update_callfiltermember_state(session, callfiltermember_id, new_state):
    data_dict = {'active': int(new_state)}
    session.query(Callfiltermember).filter(
        Callfiltermember.id == callfiltermember_id
    ).update(data_dict)
