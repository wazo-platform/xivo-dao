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

from datetime import datetime
from sqlalchemy.sql.expression import and_
from xivo_dao.alchemy.record_campaigns import RecordCampaigns
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.helpers.query_utils import paginate
import logging

logger = logging.getLogger(__name__)
logging.basicConfig()


@daosession
def get_records(session, search, checkCurrentlyRunning, paginator):
    my_query = session.query(RecordCampaigns)
    if search != None:
        logger.debug("Search search_pattern: " + str(search))
        my_query = my_query.filter_by(**search)

    if checkCurrentlyRunning:
        now = datetime.now()
        my_query = my_query.filter(
                           and_(RecordCampaigns.start_date <= str(now),
                                RecordCampaigns.end_date >= str(now)))

    return paginate(my_query, paginator)


@daosession
def id_from_name(session, name):
    result = session.query(RecordCampaigns)\
                .filter_by(campaign_name=name)\
                .first()
    if result != None:
        return result.id
    else:
        return None


@daosession
def add_or_update(session, campaign):
    try:
        session.begin()
        session.add(campaign)
        session.commit()
    except Exception as e:
        try:
            session.rollback()
        except e:
            logger.error("Rollback failed with exception " + str(e))
        logger.error("RecordCampaignDbBinder - add or update: " + str(e))
        raise e
    return campaign.id


@daosession
def get(session, campaign_id):
    return session.query(RecordCampaigns)\
        .filter(RecordCampaigns.id == campaign_id).first()


@daosession
def delete(session, campaign):
    try:
        session.begin()
        session.delete(campaign)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


@daosession
def delete_all(session):
    try:
        session.begin()
        session.query(RecordCampaigns).delete()
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


