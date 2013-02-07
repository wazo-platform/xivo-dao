# -*- coding: UTF-8 -*-
#
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
from xivo_dao import recordings_dao
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.record_campaigns import RecordCampaigns
from xivo_dao.alchemy.recordings import Recordings
from xivo_dao.helpers.dynamic_formatting import table_list_to_list_dict
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.tests.test_preriquisites import recording_preriquisites
import copy


class TestRecordingDao(DAOTestCase):

    tables = [QueueFeatures, AgentFeatures, Recordings, RecordCampaigns]

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

        self.default_dict_data = {'cid': '001',
                                  'caller': '2002',
                                  'callee': '',
                                  'agent_id': '1',
                                  'filename': 'file.wav',
                                  'start_time': '2012-01-01 00:00:00',
                                  'end_time': '2012-01-01 00:10:00',
                                  'campaign_id': str(self.campaign.id),
                                  'client_id': ''
                                  }

    def test_get_recordings_as_list(self):
        dict_data1 = copy.deepcopy(self.default_dict_data)
        dict_data2 = copy.deepcopy(dict_data1)
        dict_data2['cid'] = '002'
        dict_data2['caller'] = '3003'
        my_recording1 = Recordings()
        my_recording2 = Recordings()
        for k, v in dict_data1.items():
            setattr(my_recording1, k, v)
        for k, v in dict_data2.items():
            setattr(my_recording2, k, v)
        self.session.add(my_recording1)
        self.session.add(my_recording2)
        self.session.commit()

        search = {'caller': '2002'}
        result = recordings_dao\
                     .get_recordings_as_list(self.campaign.id, search)
        self.assertTrue(result['total'] == 1)
        self.assertEquals(dict_data1, result['data'][0])

    def test_add_recording(self):
        dict_data1 = copy.deepcopy(self.default_dict_data)
        recordings_dao.add_recording(dict_data1)
        result = self.session.query(Recordings).all()
        result = table_list_to_list_dict(result)
        self.assertTrue(len(result) == 1)
        self.assertEqual(dict_data1, result[0])

    def test_search_recordings(self):
        dict_data1 = copy.deepcopy(self.default_dict_data)
        dict_data2 = copy.deepcopy(dict_data1)
        dict_data2['cid'] = '002'
        dict_data2['caller'] = '3003'
        my_recording1 = Recordings()
        my_recording2 = Recordings()
        for k, v in dict_data1.items():
            setattr(my_recording1, k, v)
        for k, v in dict_data2.items():
            setattr(my_recording2, k, v)
        self.session.add(my_recording1)
        self.session.add(my_recording2)
        self.session.commit()

        key = '3003'
        result = recordings_dao\
                     .search_recordings(self.campaign.id, key)
        self.assertTrue(result['total'] == 1)
        self.assertEquals(dict_data2, result['data'][0])

        key = '1000'
        result = recordings_dao\
                     .search_recordings(self.campaign.id, key)
        self.assertTrue(result['total'] == 2)
        self.assertEquals(dict_data1, result['data'][0])
        self.assertEquals(dict_data2, result['data'][1])

    def test_delete(self):
        result = recordings_dao.delete(1, '001')
        assert result == None
        dict_data1 = copy.deepcopy(self.default_dict_data)
        my_recording1 = Recordings()
        for k, v in dict_data1.items():
            setattr(my_recording1, k, v)
        self.session.add(my_recording1)
        self.session.commit()
        data = self.session.query(Recordings).all()
        self.assertTrue(len(data) == 1)
        data = table_list_to_list_dict(data)
        self.assertEqual(dict_data1, data[0])
        result = recordings_dao.delete(self.campaign.id,
                                                  my_recording1.cid)
        data = self.session.query(Recordings).all()
        self.assertTrue(len(data) == 0)
        self.assertTrue(result == my_recording1.filename)
