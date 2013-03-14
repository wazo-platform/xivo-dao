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

from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao.mapping_alchemy_sdm import voicemail_mapping
from xivo_dao.service_data_model.voicemail_sdm import VoicemailSdm
import unittest


class TestVoicemailMapping(unittest.TestCase):

    def test_alchemy_to_sdm(self):
        voicemail_alchemy = Voicemail()
        voicemail_sdm = VoicemailSdm()

        voicemail_alchemy.uniqueid = voicemail_sdm.id = 1
        voicemail_alchemy.email = voicemail_sdm.email = "test@xivo.org"
        voicemail_alchemy.fullname = voicemail_sdm.fullname = "John doe sdf &é'é- "
        voicemail_alchemy.mailbox = voicemail_sdm.mailbox = "123@default.com"
        voicemail_alchemy.password = voicemail_sdm.password = "delamortqui tue"
        voicemail_alchemy.attach = voicemail_sdm.attach = False
        voicemail_alchemy.skipcheckpass = voicemail_sdm.skipcheckpass = True
        voicemail_alchemy.deletevoicemail = voicemail_sdm.deleteaftersend = True

        result = voicemail_mapping.alchemy_to_sdm(voicemail_alchemy)
        self.assertEquals(voicemail_sdm.__dict__, result.__dict__)

    def test_sdm_to_alchemy(self):
        voicemail_sdm = VoicemailSdm()
        voicemail_alchemy = Voicemail()

        voicemail_alchemy.uniqueid = voicemail_sdm.id = 1
        voicemail_alchemy.email = voicemail_sdm.email = "test@xivo.org"
        voicemail_alchemy.fullname = voicemail_sdm.fullname = "John doe sdf &é'é- "
        voicemail_alchemy.mailbox = voicemail_sdm.mailbox = "123@default.com"
        voicemail_alchemy.password = voicemail_sdm.password = "delamortqui tue"
        voicemail_alchemy.attach = voicemail_sdm.attach = False
        voicemail_alchemy.skipcheckpass = voicemail_sdm.skipcheckpass = True
        voicemail_alchemy.deletevoicemail = voicemail_sdm.deleteaftersend = True
        voicemail_alchemy.context = "default"
        voicemail_alchemy.tz = "eu-fr"

        result = voicemail_mapping.sdm_to_alchemy(voicemail_sdm)
        self.assertEquals(voicemail_alchemy.todict(), result.todict())

    def test_sdm_to_alchemy_dict(self):
        voicemail_dict_sdm = {}
        voicemail_dict_alchemy = {}
        fullname = "John doe sdf &é'é- "
        deletevoicemail = True
        voicemail_dict_alchemy['fullname'] = fullname
        voicemail_dict_sdm['fullname'] = fullname
        voicemail_dict_alchemy['deletevoicemail'] = deletevoicemail
        voicemail_dict_sdm['deleteaftersend'] = deletevoicemail

        result = voicemail_mapping.sdm_to_alchemy_dict(voicemail_dict_sdm)
        self.assertEquals(voicemail_dict_alchemy, result)

    def test_sdm_to_alchemy_dict_fails(self):
        voicemail_dict_sdm = {}
        fullname = "John doe sdf &é'é- "
        deletevoicemail = True
        voicemail_dict_sdm['fullname'] = fullname
        voicemail_dict_sdm['notExistingKey'] = deletevoicemail

        self.assertRaises(AttributeError, voicemail_mapping.sdm_to_alchemy_dict, voicemail_dict_sdm)






