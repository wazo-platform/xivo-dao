# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo_dao.alchemy.callfilter import Callfilter
from xivo_dao.alchemy.callfiltermember import Callfiltermember
from sqlalchemy.sql.expression import and_, cast, func
from xivo_dao.alchemy.userfeatures import UserFeatures
from sqlalchemy.types import Integer
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.alchemy.extension import Extension as ExtensionSchema


@daosession
def does_secretary_filter_boss(session, boss_user_id, secretary_user_id):
    subquery = (session.query(Callfiltermember.callfilterid)
                .filter(Callfiltermember.bstype == 'boss')
                .filter(Callfiltermember.typeval == str(boss_user_id))
                .subquery())

    query = (session.query(Callfiltermember.id)
             .filter(Callfiltermember.typeval == str(secretary_user_id))
             .filter(Callfiltermember.bstype == 'secretary')
             .filter(Callfiltermember.callfilterid.in_(subquery)))

    return query.count()


@daosession
def get(session, callfilter_id):
    return (session.query(Callfilter, Callfiltermember)
            .join((Callfiltermember, Callfilter.id == Callfiltermember.callfilterid))
            .filter(Callfilter.id == callfilter_id)
            .all())


@daosession
def get_secretaries_id_by_context(session, context):
    return (session.query(Callfiltermember.id)
            .join(UserLine, and_(UserLine.user_id == cast(Callfiltermember.typeval, Integer),
                                 UserLine.main_user == True,  # noqa
                                 UserLine.main_line == True))  # noqa
            .join(LineExtension, and_(UserLine.line_id == LineExtension.line_id,
                                      LineExtension.main_extension == True))  # noqa
            .join(ExtensionSchema, and_(ExtensionSchema.context == context,
                                        LineExtension.extension_id == ExtensionSchema.id))
            .filter(and_(Callfiltermember.type == 'user',
                         Callfiltermember.bstype == 'secretary'))
            .all())


@daosession
def get_secretaries_by_callfiltermember_id(session, callfiltermember_id):
    return (session.query(Callfiltermember, UserFeatures.ringseconds)
            .join((Callfilter, Callfilter.id == Callfiltermember.callfilterid))
            .join((UserFeatures, UserFeatures.id == cast(Callfiltermember.typeval, Integer)))
            .filter(and_(Callfilter.id == callfiltermember_id,
                         Callfiltermember.bstype == 'secretary'))
            .order_by(Callfiltermember.priority.asc())
            .all())


@daosession
def get_by_callfiltermember_id(session, callfiltermember_id):
    return (session.query(Callfiltermember)
            .filter(Callfiltermember.id == callfiltermember_id)
            .first())


@daosession
def get_by_boss_id(session, boss_id):
    return (session.query(Callfiltermember, Callfilter)
            .join((Callfilter, Callfilter.id == Callfiltermember.callfilterid))
            .filter(and_(Callfiltermember.typeval == str(boss_id),
                         Callfiltermember.bstype == 'boss'))
            .first())


@daosession
def is_activated_by_callfilter_id(session, callfilter_id):
    return (session.query(func.count(Callfiltermember.active))
            .join((Callfilter, Callfilter.id == Callfiltermember.callfilterid))
            .filter(and_(Callfiltermember.callfilterid == callfilter_id,
                         Callfiltermember.bstype == 'secretary',
                         Callfiltermember.active == 1))
            .first()[0])


@daosession
def update_callfiltermember_state(session, callfiltermember_id, new_state):
    data_dict = {'active': int(new_state)}
    session.query(Callfiltermember).filter(Callfiltermember.id == callfiltermember_id).update(data_dict)
