# -*- coding: UTF-8 -*-

# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from sqlalchemy.sql.expression import or_, and_
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.recordings import Recordings
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.helpers.query_utils import get_all_data, get_paginated_data
import logging

logger = logging.getLogger(__name__)
logging.basicConfig()


@daosession
def get_recordings_as_list(session, campaign_id, search = None, pagination = None):
    search_pattern = {}
    search_pattern['campaign_id'] = campaign_id
    if search != None:
        for item in search:
                search_pattern[item] = search[item]

    logger.debug("Search search_pattern: " + str(search_pattern))
    my_query = session.query(Recordings)\
                                   .filter_by(**search_pattern)
    if (pagination == None):
        return get_all_data(session, my_query)
    else:
        return get_paginated_data(session, my_query, pagination)


@daosession
def add_recording(session, params):
    record = Recordings()
    for k, v in params.items():
        setattr(record, k, v)
    try:
        session.add(record)
        session.commit()
    except Exception as e:
        logger.error("SQL exception:" + e.message)
        session.rollback()
        raise e
    return True


@daosession
def search_recordings(session, campaign_id, key, pagination = None):
    logger.debug("campaign id = " + str(campaign_id)\
                  + ", key = " + str(key))
    #jointure interne:
    #Recordings r inner join AgentFeatures a on r.agent_id = a.id
    my_query = session.query(Recordings)\
                    .join((AgentFeatures, Recordings.agent_id == AgentFeatures.id))\
                    .filter(and_(Recordings.campaign_id == campaign_id, \
                                 or_(Recordings.caller == key,
                                     AgentFeatures.number == key)))
    if (pagination == None):
        return get_all_data(session, my_query)
    else:
        return get_paginated_data(session, my_query, pagination)


@daosession
def delete(session, campaign_id, recording_id):
    logger.debug("Going to delete " + str(recording_id))
    recording = session.query(Recordings)\
                .filter(and_(Recordings.cid == recording_id,
                             Recordings.campaign_id == campaign_id)) \
                .first()

    if(recording == None):
        return None
    else:
        filename = recording.filename
        session.delete(recording)
        session.commit()
        return filename


@daosession
def count_recordings(session, campaign_id):
    return session.query(Recordings)\
        .filter(Recordings.campaign_id == campaign_id).count()
