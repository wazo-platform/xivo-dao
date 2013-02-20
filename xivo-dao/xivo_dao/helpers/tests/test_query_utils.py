# -*- coding: UTF-8 -*-

# Copyright (C) 2013 Avencall
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
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.record_campaigns import RecordCampaigns
from xivo_dao.alchemy.recordings import Recordings
from xivo_dao.helpers import query_utils
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.tests.test_preriquisites import recording_preriquisites
import copy


class TestQueryUtils(DAOTestCase):

    tables = [AgentFeatures, QueueFeatures, Recordings, RecordCampaigns]

    def setUp(self):
        self.empty_tables()
        recording_preriquisites(self.session)

    def test_paginate_valid_paginator(self):
        campaign1 = RecordCampaigns()
        campaign1.activated = True
        campaign1.base_filename = 'file-'
        campaign1.campaign_name = 'test'
        campaign1.end_date = '2012-12-12 00:00:00'
        campaign1.start_date = '2012-01-12 00:00:00'
        campaign1.queue_id = 1

        campaign2 = copy.deepcopy(campaign1)
        campaign2.campaign_name = 'test2'

        self.session.begin()
        self.session.add_all([campaign1, campaign2])
        self.session.commit()

        query = self.session.query(RecordCampaigns)
        paginator = (1, 1)
        (total, items) = query_utils.paginate(query, paginator)
        self.assertEqual(total, 2)
        self.assertEqual(items, [campaign1])

        paginator = (2, 1)
        (total, items) = query_utils.paginate(query, paginator)
        self.assertEqual(total, 2)
        self.assertEqual(items, [campaign2])

        paginator = (1, 2)
        (total, items) = query_utils.paginate(query, paginator)
        self.assertEqual(total, 2)
        self.assertEqual(items, [campaign1, campaign2])

    def test_paginate_invalid_paginator(self):
        campaign1 = RecordCampaigns()
        campaign1.activated = True
        campaign1.base_filename = 'file-'
        campaign1.campaign_name = 'test'
        campaign1.end_date = '2012-12-12 00:00:00'
        campaign1.start_date = '2012-01-12 00:00:00'
        campaign1.queue_id = 1

        campaign2 = copy.deepcopy(campaign1)
        campaign2.campaign_name = 'test2'

        self.session.begin()
        self.session.add_all([campaign1, campaign2])
        self.session.commit()

        query = self.session.query(RecordCampaigns)
        paginator = (0, 1)
        (total, items) = query_utils.paginate(query, paginator)
        self.assertEqual(total, 2)
        self.assertEqual(items, [campaign1, campaign2])
