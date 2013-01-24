# -*- coding: utf-8 -*-
#
# Copyright (C) 2013  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the source tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.callfilter import Callfilter
from xivo_dao.alchemy.callfiltermember import Callfiltermember
from sqlalchemy.sql.expression import and_, cast, func
from xivo_dao.alchemy.userfeatures import UserFeatures
from sqlalchemy.types import Integer

_DB_NAME = 'asterisk'


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def does_secretary_filter_boss(boss_user_id, secretary_user_id):
    query = '''\
SELECT COUNT(id) AS count
FROM "callfiltermember"
WHERE "callfilterid" = (SELECT "callfilterid" FROM "callfiltermember" WHERE "typeval"='%s' AND "bstype" = 'boss')
AND "typeval" = '%s'
AND "bstype" = 'secretary'
''' % (boss_user_id, secretary_user_id)

    res, = _session().query('count').from_statement(query).first()
    return res


def get(callfilter_id):
    return (_session().query(Callfilter, Callfiltermember)
            .join((Callfiltermember, Callfilter.id == Callfiltermember.callfilterid))
            .filter(Callfilter.id == callfilter_id)
            .all())


def get_secretaries_id_by_context(context):
    return (_session().query(Callfiltermember.id)
            .join((Callfilter, Callfilter.id == Callfiltermember.callfilterid))
            .filter(and_(Callfilter.context == context,
                         Callfiltermember.bstype == 'secretary'))
            .all())


def get_secretaries_by_callfiltermember_id(callfiltermember_id):
    return (_session().query(Callfiltermember, UserFeatures.ringseconds)
            .join((Callfilter, Callfilter.id == Callfiltermember.callfilterid))
            .join((UserFeatures, UserFeatures.id == cast(Callfiltermember.typeval, Integer)))
            .filter(and_(Callfilter.id == callfiltermember_id,
                         Callfiltermember.bstype == 'secretary'))
            .order_by(Callfiltermember.priority.desc())
            .all())


def get_by_callfiltermember_id(callfiltermember_id):
    return (_session().query(Callfiltermember)
            .filter(Callfiltermember.id == callfiltermember_id)
            .first())


def get_by_boss_id(boss_id):
    return (_session().query(Callfiltermember, Callfilter)
            .join((Callfilter, Callfilter.id == Callfiltermember.callfilterid))
            .filter(and_(Callfiltermember.typeval == str(boss_id),
                         Callfiltermember.bstype == 'boss'))
            .first())


def is_activated_by_callfilter_id(callfilter_id):
    return (_session().query(func.count(Callfiltermember.active))
            .join((Callfilter, Callfilter.id == Callfiltermember.callfilterid))
            .filter(and_(Callfiltermember.callfilterid == callfilter_id,
                         Callfiltermember.bstype == 'secretary',
                         Callfiltermember.active == 1))
            .first()[0])


def update_callfiltermember_state(callfiltermember_id, new_state):
    data_dict = {'active': int(new_state)}
    _session().query(Callfiltermember).filter(Callfiltermember.id == callfiltermember_id).update(data_dict)
    _session().commit()
