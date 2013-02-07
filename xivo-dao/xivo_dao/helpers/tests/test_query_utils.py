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
from sqlalchemy.sql.expression import asc
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.record_campaigns import RecordCampaigns
from xivo_dao.alchemy.recordings import Recordings
from xivo_dao.helpers import query_utils
from xivo_dao.helpers.cel_exception import InvalidPaginatorException
from xivo_dao.tests.test_dao import DAOTestCase
import random
from xivo_dao.tests.test_preriquisites import recording_preriquisites


class TestQueryUtils(DAOTestCase):

    tables = [AgentFeatures, QueueFeatures, Recordings, RecordCampaigns]

    def setUp(self):
        self.empty_tables()
        recording_preriquisites(self.session)
        self.campaign = RecordCampaigns()
        self.campaign.campaign_name = 'name'
        self.campaign.base_filename = 'file-'
        self.campaign.queue_id = 1
        self.campaign.start_date = datetime.strptime('2012-01-31',
                                              "%Y-%m-%d")
        self.campaign.end_date = datetime.strptime('2012-01-31',
                                              "%Y-%m-%d")
        self.campaign.activated = True
        self.session.add(self.campaign)
        self.session.commit()

    def test_get_all_data(self):

        cid1 = '001'
        cid2 = '002'
        call_direction = "incoming"
        start_time = "2004-10-19 10:23:54"
        end_time = "2004-10-19 10:23:56"
        caller = "+" + str(random.randint(1000, 9999))
        agent_id = 1

        expected_dir1 = {"cid": cid1,
                        "campaign_id": self.campaign.id,
                        "call_direction": call_direction,
                        "start_time": start_time,
                        "end_time": end_time,
                        "caller": caller,
                        "agent_id": agent_id
                        }

        expected_object1 = Recordings()
        for k, v in expected_dir1.items():
            setattr(expected_object1, k, v)

        expected_dir2 = {"cid": cid2,
                        "campaign_id": self.campaign.id,
                        "call_direction": call_direction,
                        "start_time": start_time,
                        "end_time": end_time,
                        "caller": caller,
                        "agent_id": agent_id
                        }

        expected_object2 = Recordings()
        for k, v in expected_dir2.items():
            setattr(expected_object2, k, v)

        self.session.add(expected_object1)
        self.session.add(expected_object2)
        self.session.commit()

        expected_list = [expected_object1, expected_object2].sort()
        result = query_utils.get_all_data(self.session,
                                          self.session\
                                          .query(Recordings))['data']\
                                          .sort()

        self.assertTrue(expected_list == result, "Expected: " + \
                             str(expected_list) + ", actual: " + str(result))

    def test_get_paginated_data(self):
        cid1 = "001"
        cid2 = "002"
        call_direction = "incoming"
        start_time = "2004-10-19 10:23:54"
        end_time = "2004-10-19 10:23:56"
        caller = "2002"
        agent_id = '1'

        expected_dir1 = {"cid": cid1,
                        "campaign_id": str(self.campaign.id),
                        "call_direction": call_direction,
                        "start_time": start_time,
                        "end_time": end_time,
                        "caller": caller,
                        "agent_id": agent_id,
                        'filename': '',
                        'client_id': '',
                        'callee': ''
                        }

        expected_object1 = Recordings()
        for k, v in expected_dir1.items():
            setattr(expected_object1, k, v)

        expected_dir2 = {"cid": cid2,
                        "campaign_id": str(self.campaign.id),
                        "call_direction": call_direction,
                        "start_time": start_time,
                        "end_time": end_time,
                        "caller": caller,
                        "agent_id": agent_id,
                        'filename': '',
                        'client_id': '',
                        'callee': ''
                        }

        expected_object2 = Recordings()
        for k, v in expected_dir2.items():
            setattr(expected_object2, k, v)

        self.session.add(expected_object1)
        self.session.add(expected_object2)
        self.session.commit()

        list_paginators = [(1, 1), (2, 1), (1, 0), (0, 0), (999, 999), ('')]
        list_expected_results = [[expected_dir1], [expected_dir2]]
        list_expected_results.sort(key = (lambda x: x[0]['cid']))
        list_expected_results.append([])
        list_expected_results.append([])
        list_expected_results.append([])
        list_expected_results.append([])

        i = 0
        for paginator in list_paginators:
            expected_list = list_expected_results[i]
            if(i == 3):
                self.assertRaises(InvalidPaginatorException,
                                  query_utils.get_paginated_data,
                                  self.session,
                                  self.session.query(Recordings).order_by(asc("cid")),
                                        paginator)

            elif(i == 4):
                result = query_utils.get_paginated_data(
                                    self.session,
                                    self.session\
                                      .query(Recordings)\
                                      .order_by(asc("cid")),
                                    paginator)
                self.assertEqual(result, None)
            elif(i == 5):
                self.assertRaises(InvalidPaginatorException,
                                  query_utils.get_paginated_data,
                                  self.session,
                                  self.session.query(Recordings).order_by(asc("cid")),
                                  paginator)
            else:
                result = query_utils.get_paginated_data(
                                        self.session,
                                        self.session\
                                          .query(Recordings)\
                                          .order_by(asc("cid")),
                                        paginator)['data']
                self.assertTrue(expected_list == result)
            i += 1

        self.session.query(Recordings).delete()
        self.session.commit()
