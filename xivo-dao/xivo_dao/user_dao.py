# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
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

from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.contextinclude import ContextInclude
from xivo_dao.alchemy.userfeatures import UserFeatures
from sqlalchemy import and_
from xivo_dao.helpers.db_manager import DbSession


def enable_dnd(user_id):
    _update(user_id, {'enablednd': 1})


def disable_dnd(user_id):
    _update(user_id, {'enablednd': 0})


def enable_filter(user_id):
    _update(user_id, {'incallfilter': 1})


def disable_filter(user_id):
    _update(user_id, {'incallfilter': 0})


def enable_unconditional_fwd(user_id, destination):
    _update(user_id, {'enableunc': 1, 'destunc': destination})


def disable_unconditional_fwd(user_id, destination):
    _update(user_id, {'enableunc': 0, 'destunc': destination})


def enable_rna_fwd(user_id, destination):
    _update(user_id, {'enablerna': 1, 'destrna': destination})


def disable_rna_fwd(user_id, destination):
    _update(user_id, {'enablerna': 0, 'destrna': destination})


def enable_busy_fwd(user_id, destination):
    _update(user_id, {'enablebusy': 1, 'destbusy': destination})


def disable_busy_fwd(user_id, destination):
    _update(user_id, {'enablebusy': 0, 'destbusy': destination})


def _update(user_id, user_data_dict):
    DbSession().query(UserFeatures).filter(UserFeatures.id == user_id).update(user_data_dict)
    DbSession().commit()


def get(user_id):
    result = DbSession().query(UserFeatures).filter(UserFeatures.id == int(user_id)).first()
    if result is None:
        raise LookupError()
    return result


def find_by_agent_id(agent_id):
    res = DbSession().query(UserFeatures).filter(UserFeatures.agentid == int(agent_id))
    return [user.id for user in res]


def agent_id(user_id):
    try:
        return get(user_id).agentid
    except LookupError:
        return None


def is_agent(user_id):
    try:
        id = agent_id(user_id)
        return id is not None
    except LookupError:
        return False


def get_profile(user_id):
    return get(user_id).cti_profile_id


def _get_included_contexts(context):
    return [line.include for line in (DbSession().query(ContextInclude.include)
                                       .filter(ContextInclude.context == context))]


def _get_nested_contexts(contexts):
    checked = []
    to_check = set(contexts) - set(checked)
    while to_check:
        context = to_check.pop()
        contexts.extend(_get_included_contexts(context))
        checked.append(context)
        to_check = set(contexts) - set(checked)

    return list(set(contexts))


def get_reachable_contexts(user_id):
    line_contexts = [line.context for line in (DbSession().query(LineFeatures)
                                                .filter(LineFeatures.iduserfeatures == user_id))]

    return _get_nested_contexts(line_contexts)


def all_join_line_id():
    return (DbSession().query(UserFeatures, LineFeatures.id)
            .outerjoin((LineFeatures, UserFeatures.id == LineFeatures.iduserfeatures))
            .all())


def get_join_line_id_with_user_id(user_id):
    return (DbSession().query(UserFeatures, LineFeatures.id)
            .outerjoin((LineFeatures, UserFeatures.id == LineFeatures.iduserfeatures))
            .filter(UserFeatures.id == int(user_id))
            .first())


def find_by_line_id(line_id):
    return DbSession().query(LineFeatures.iduserfeatures).filter(LineFeatures.id == line_id).first().iduserfeatures


def get_line_identity(user_id):
    try:
        line = (DbSession().query(LineFeatures.protocol, LineFeatures.name)
                         .filter(LineFeatures.iduserfeatures == user_id)).first()
    except IndexError:
        raise LookupError('Could not find a line for user %s', user_id)
    if not line:
        raise LookupError('Could not find a line for user %s', user_id)
    return '%s/%s' % (line.protocol, line.name)


def get_agent_number(user_id):
    row = (DbSession().query(AgentFeatures.number, UserFeatures.agentid)
            .filter(and_(UserFeatures.id == user_id,
                         AgentFeatures.id == UserFeatures.agentid))
            .first())
    if not row:
        raise LookupError('Could not find a agent number for user %s', user_id)
    return row.number


def get_dest_unc(user_id):
    return DbSession().query(UserFeatures.destunc).filter(UserFeatures.id == int(user_id)).first().destunc


def get_fwd_unc(user_id):
    return (DbSession().query(UserFeatures.enableunc).filter(UserFeatures.id == int(user_id)).first().enableunc == 1)


def get_dest_busy(user_id):
    return DbSession().query(UserFeatures.destbusy).filter(UserFeatures.id == int(user_id)).first().destbusy


def get_fwd_busy(user_id):
    return (DbSession().query(UserFeatures.enablebusy).filter(UserFeatures.id == int(user_id)).first().enablebusy == 1)


def get_dest_rna(user_id):
    return DbSession().query(UserFeatures.destrna).filter(UserFeatures.id == int(user_id)).first().destrna


def get_fwd_rna(user_id):
    return (DbSession().query(UserFeatures.enablerna).filter(UserFeatures.id == int(user_id)).first().enablerna == 1)


def get_name_number(user_id):
    res = (DbSession().query(UserFeatures.firstname, UserFeatures.lastname, LineFeatures.number).
           filter(and_(UserFeatures.id == LineFeatures.iduserfeatures, UserFeatures.id == user_id))).first()
    return '%s %s' % (res.firstname, res.lastname), res.number


def get_device_id(user_id):
    row = (DbSession()
           .query(LineFeatures.iduserfeatures, LineFeatures.device)
           .filter(LineFeatures.iduserfeatures == user_id)
           .first())
    if not row:
        raise LookupError('Cannot find a device from this user id %s' % user_id)
    return int(row.device)


def get_context(user_id):
    res = (DbSession()
           .query(LineFeatures.context)
           .filter(LineFeatures.iduserfeatures == user_id)
           .first())

    if not res:
        return None

    return res.context
