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
from xivo_dao.helpers.cel_exception import InvalidInputException
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.helpers.dynamic_formatting import str_to_datetime
from xivo_dao.helpers.query_utils import get_all_data, get_paginated_data
from xivo_dao.helpers.time_interval import TimeInterval
import logging

logger = logging.getLogger(__name__)
logging.basicConfig()


@daosession
def get_records(session, search = None, checkCurrentlyRunning = False, pagination = None):
    my_query = session.query(RecordCampaigns)
    if search != None:
        logger.debug("Search search_pattern: " + str(search))
        my_query = my_query.filter_by(**search)

    if checkCurrentlyRunning:
        now = datetime.now()
        my_query = my_query.filter(
                           and_(RecordCampaigns.start_date <= str(now),
                                RecordCampaigns.end_date >= str(now)))

    if (pagination == None):
        return get_all_data(session, my_query)
    else:
        return get_paginated_data(session, my_query, pagination)


@daosession
def id_from_name(session, name):
    result = session.query(RecordCampaigns)\
                .filter_by(campaign_name = name)\
                .first()
    if result != None:
        return result.id
    else:
        return None


@daosession
def add(session, params):
    record = RecordCampaigns()
    for k, v in params.items():
        if((k == "start_date" or k == "end_date") and type(v) != datetime):
            v = str_to_datetime(v)
        setattr(record, k, v)
    _validate_campaign(record)
    try:
        session.add(record)
        session.commit()
    except Exception as e:
        try:
            session.rollback()
        except e:
            logger.error("Rollback failed with exception " + str(e))
        logger.error("RecordCampaignDbBinder - add: " + str(e))
        raise e
    logger.debug("returning")
    return record.id


@daosession
def update(session, campaign_id, params):
    try:
        logger.debug('entering update')
        campaignsList = session.query(RecordCampaigns)\
                    .filter(RecordCampaigns.id == campaign_id).all()
        logger.debug("Campaigns list for update: " + str(campaignsList))
        if(len(campaignsList) == 0):
            return False
        campaign = campaignsList[0]
        logger.debug('got original')
        for k, v in params.items():
            if((k == "start_date" or k == "end_date")
                                    and type(v) != datetime):
                v = str_to_datetime(v)
            setattr(campaign, k, v)
        logger.debug('attributes modified')
        _validate_campaign(campaign)
        session.add(campaign)
        session.commit()
        logger.debug('commited')
    except Exception as e:
        session.rollback()
        logger.debug('Impossible to update the campaign: ' + str(e))
        raise e
    return True


@daosession
def _validate_campaign(session, record):
    '''Check if the campaign is valid, throws 
    with a list of errors if it is not the case.'''
    errors_list = []
    logger.debug("validating campaign")
    if(record.campaign_name == None):
        errors_list.append("empty_name")

    if(record.start_date > record.end_date):
        errors_list.append("start_greater_than_end")
    else:
        #check if another campaign exists on the same queue,
        #with a concurrent time interval:
        campaigns_list = session.query(RecordCampaigns)\
            .filter(RecordCampaigns.queue_id == record.queue_id)\
            .filter(RecordCampaigns.id != record.id).all()
        record_interval = TimeInterval(record.start_date, record.end_date)
        intersects = False
        for campaign in campaigns_list:
            campaign_interval = TimeInterval(campaign.start_date,
                                             campaign.end_date)
            if(record_interval.intersect(campaign_interval) != None):
                intersects = True
                break
        if(intersects):
            errors_list.append("concurrent_campaigns")

    if(len(errors_list) > 0):
        raise InvalidInputException("Invalid data provided", errors_list)


@daosession
def get(session, campaign_id):
    return session.query(RecordCampaigns)\
        .filter(RecordCampaigns.id == campaign_id).first()


@daosession
def delete(session, campaign):
    try:
        session.delete(campaign)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
