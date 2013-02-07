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
from sqlalchemy.exc import IntegrityError
from xivo_dao import record_campaigns_dao
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.record_campaigns import RecordCampaigns
from xivo_dao.alchemy.recordings import Recordings
from xivo_dao.helpers.cel_exception import InvalidInputException
from xivo_dao.helpers.dynamic_formatting import table_list_to_list_dict
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.tests.test_preriquisites import recording_preriquisites
import copy


class TestRecordCampaignDao(DAOTestCase):

    tables = [QueueFeatures, AgentFeatures, Recordings, RecordCampaigns]

    def setUp(self):
        self.empty_tables()
        recording_preriquisites(self.session)

    def test_get_records(self):
        campaign_name = "campaign-àé"
        queue_id = "1"
        base_filename = campaign_name + "-"

        expected_dict = {
            "campaign_name": campaign_name,
            "activated": "False",
            "base_filename": base_filename,
            "queue_id": queue_id,
            "start_date": '2012-01-01 12:12:12',
            "end_date": '2012-12-12 12:12:12',
        }

        obj = RecordCampaigns()
        for k, v in expected_dict.items():
            setattr(obj, k, v)

        self.session.add(obj)
        self.session.commit()
        expected_dict['id'] = str(obj.id)
        records = record_campaigns_dao.get_records()['data']
        self.assertTrue(expected_dict == records[0])

    def test_id_from_name(self):
        campaign_name = "campaign-àé"
        queue_id = "1"
        base_filename = campaign_name + "-"

        expected_dict = {
            "campaign_name": campaign_name,
            "activated": "False",
            "base_filename": base_filename,
            "queue_id": queue_id,
            "start_date": '2012-01-01 12:12:12',
            "end_date": '2012-12-12 12:12:12',
        }

        obj = RecordCampaigns()
        for k, v in expected_dict.items():
            setattr(obj, k, v)

        self.session.add(obj)
        self.session.commit()
        retrieved_id = record_campaigns_dao\
                .id_from_name(expected_dict['campaign_name'])
        self.assertTrue(retrieved_id == obj.id)

        self.assertEqual(None, record_campaigns_dao.id_from_name('test'))

    def test_add(self):
        campaign_name = "campaign-àé"
        queue_id = "1"
        base_filename = campaign_name + "-"

        expected_dict = {
            "campaign_name": campaign_name,
            "activated": "False",
            "base_filename": base_filename,
            "queue_id": queue_id,
            "start_date": '2012-01-01 12:12:12',
            "end_date": '2012-12-12 12:12:12',
        }

        gen_id = record_campaigns_dao.add(expected_dict)

        expected_dict['id'] = str(gen_id)
        result = self.session.query(RecordCampaigns).all()
        self.assertTrue(len(result) == 1)
        result = table_list_to_list_dict(result)
        self.assertEquals(result[0], expected_dict)

    def test_update(self):
        campaign_name = "campaign-àé"
        queue_id = "1"
        base_filename = campaign_name + "-"

        inserted_dict = {
            "campaign_name": campaign_name,
            "activated": "False",
            "base_filename": base_filename,
            "queue_id": queue_id,
            "start_date": '2012-01-01 12:12:12',
            "end_date": '2012-12-12 12:12:12',
        }

        obj = RecordCampaigns()
        for k, v in inserted_dict.items():
            setattr(obj, k, v)

        self.session.add(obj)
        self.session.commit()
        queue_id2 = '2'

        updated_dict = {
            "campaign_name": campaign_name + str(1),
            "activated": "True",
            "base_filename": base_filename + str(1),
            "queue_id": queue_id2,
            "start_date": '2012-01-01 12:12:13',
            "end_date": '2012-12-12 12:12:13',
        }
        record_campaigns_dao.update(obj.id, updated_dict)
        updated_dict['id'] = str(obj.id)
        result = self.session.query(RecordCampaigns).all()
        self.assertTrue(len(result) == 1)
        result = table_list_to_list_dict(result)
        self.assertTrue(result[0] == updated_dict)

    def test_validate_campaign(self):
        campaign = RecordCampaigns()
        campaign.campaign_name = None
        campaign.start_date = datetime.strptime('2012-12-31',
                                                "%Y-%m-%d")
        campaign.end_date = datetime.strptime('2012-01-31',
                                              "%Y-%m-%d")
        gotException = False
        try:
            record_campaigns_dao._validate_campaign(campaign)
        except InvalidInputException as e:
            self.assertTrue('empty_name' in e.errors_list)
            self.assertTrue('start_greater_than_end' in e.errors_list)
            gotException = True
        self.assertTrue(gotException)

        #we check that overlapping campaigns are rejected
        campaign1 = RecordCampaigns()
        campaign1.campaign_name = 'name1'
        campaign1.start_date = datetime.strptime('2012-01-31',
                                              "%Y-%m-%d")
        campaign1.end_date = datetime.strptime('2012-12-31',
                                                "%Y-%m-%d")
        campaign1.base_filename = 'file-'
        campaign1.activated = True
        campaign1.queue_id = 1
        campaign2 = copy.deepcopy(campaign1)
        self.session.add(campaign1)
        self.session.commit()
        campaign2.start_date = datetime.strptime('2012-02-28',
                                              "%Y-%m-%d")
        campaign2.end_date = datetime.strptime('2013-01-31',
                                                "%Y-%m-%d")
        gotException = False
        try:
            record_campaigns_dao._validate_campaign(campaign2)
        except InvalidInputException as e:
            self.assertTrue('concurrent_campaigns' in e.errors_list)
            gotException = True
        self.assertTrue(gotException)

    def test_get(self):
        campaign_name = "campaign-àé"
        queue_id = "1"
        base_filename = campaign_name + "-"

        obj = RecordCampaigns()

        obj.campaign_name = campaign_name
        obj.activated = False
        obj.base_filename = base_filename,
        obj.queue_id = queue_id,
        obj.start_date = '2012-01-01 12:12:12',
        obj.end_date = '2012-12-12 12:12:12',

        self.session.add(obj)
        self.session.commit()
        returned_obj = record_campaigns_dao.get(obj.id)
        self.assertEqual(returned_obj, obj)

    def test_delete(self):
        campaign_name = "campaign-àé"
        queue_id = "1"
        base_filename = campaign_name + "-"

        obj = RecordCampaigns()

        obj.campaign_name = campaign_name
        obj.activated = False
        obj.base_filename = base_filename
        obj.queue_id = queue_id
        obj.start_date = '2012-01-01 12:12:12'
        obj.end_date = '2012-12-12 12:12:12'

        self.session.add(obj)
        self.session.commit()
        record_campaigns_dao.delete(obj)
        self.assertEqual(None, record_campaigns_dao.get(obj.id))

    def test_delete_integrity_error(self):
        campaign_name = "campaign-àé"
        queue_id = "1"
        base_filename = campaign_name + "-"

        campaign = RecordCampaigns()

        campaign.campaign_name = campaign_name
        campaign.activated = False
        campaign.base_filename = base_filename
        campaign.queue_id = queue_id
        campaign.start_date = '2012-01-01 12:12:12'
        campaign.end_date = '2012-12-12 12:12:12'
        self.session.add(campaign)
        self.session.commit()

        recording = Recordings()
        recording.campaign_id = campaign.id
        recording.filename = 'file'
        recording.cid = '123'
        recording.agent_id = 1
        recording.caller = '2002'
        self.session.add(recording)
        self.session.commit()

        self.assertRaises(IntegrityError, record_campaigns_dao.delete, campaign)
