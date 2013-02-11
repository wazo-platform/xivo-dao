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
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.tests.test_preriquisites import recording_preriquisites
import copy


class TestRecordCampaignDao(DAOTestCase):

    tables = [QueueFeatures, AgentFeatures, Recordings, RecordCampaigns]

    def setUp(self):
        self.empty_tables()
        recording_preriquisites(self.session)
        self._create_sample_campaign()

    def test_get_records(self):
        campaign = copy.deepcopy(self.sample_campaign)
        self.session.add(campaign)
        self.session.commit()

        paginator = (1, 1)
        (total, items) = record_campaigns_dao.get_records(
                                                None,
                                                False,
                                                paginator)
        self.assertEquals([campaign], items)
        self.assertEqual(total, 1)

    def test_id_from_name(self):
        campaign = copy.deepcopy(self.sample_campaign)
        self.session.add(campaign)
        self.session.commit()
        retrieved_id = record_campaigns_dao\
                .id_from_name(campaign.campaign_name)
        self.assertEquals(retrieved_id, campaign.id)
        self.assertEqual(None, record_campaigns_dao.id_from_name('test'))

    def test_add(self):
        campaign = copy.deepcopy(self.sample_campaign)
        gen_id = record_campaigns_dao.add_or_update(campaign)
        self.assertTrue(gen_id > 0)
        result = self.session.query(RecordCampaigns).all()
        self.assertEqual([campaign], result)

    def test_update(self):
        campaign = copy.deepcopy(self.sample_campaign)
        self.session.add(campaign)
        self.session.commit()
        new_name = campaign.campaign_name + "1"
        new_queue_id = 2
        campaign.campaign_name = new_name
        campaign.queue_id = new_queue_id
        record_campaigns_dao.add_or_update(campaign)

        result = self.session.query(RecordCampaigns).all()
        self.assertEquals(len(result), 1)
        updated_campaign = result[0]
        self.assertEqual(updated_campaign.campaign_name,
                         new_name)
        self.assertEqual(updated_campaign.queue_id,
                         new_queue_id)

    def test_get(self):
        campaign = copy.deepcopy(self.sample_campaign)
        self.session.add(campaign)
        self.session.commit()
        returned_obj = record_campaigns_dao.get(campaign.id)
        self.assertEqual(returned_obj, campaign)

    def test_delete(self):
        campaign = copy.deepcopy(self.sample_campaign)
        self.session.add(campaign)
        self.session.commit()
        record_campaigns_dao.delete(campaign)
        self.assertEqual(None, record_campaigns_dao.get(campaign.id))

    def test_delete_integrity_error(self):
        campaign = copy.deepcopy(self.sample_campaign)
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

        self.assertRaises(IntegrityError,
                          record_campaigns_dao.delete,
                          campaign)

    def test_eager_loading(self):
        campaign = copy.deepcopy(self.sample_campaign)
        self.session.add(campaign)
        self.session.commit()
        my_id = campaign.id
        self.session.expunge_all()
        returned_obj = record_campaigns_dao.get(my_id)
        self.assertTrue('id' in returned_obj.__dict__.keys())

    def _create_sample_campaign(self):
        self.sample_campaign = RecordCampaigns()
        self.sample_campaign.activated = True
        self.sample_campaign.campaign_name = "campaign-àé"
        self.sample_campaign.queue_id = 1
        self.sample_campaign.base_filename = self.sample_campaign.campaign_name + "-"
        self.sample_campaign.start_date = datetime.strptime('2012-01-01 12:12:12',
                                                            "%Y-%m-%d %H:%M:%S")
        self.sample_campaign.end_date = datetime.strptime('2012-12-12 12:12:12',
                                                            "%Y-%m-%d %H:%M:%S")
