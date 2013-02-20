#!/usr/bin/python
# -*- coding: utf-8 -*-

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


from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao import voicemail_dao


class VoicemailDAOTestCase(DAOTestCase):

    tables = [Voicemail]

    def setUp(self):
        self.empty_tables()

    def _insert_voicemail(self, mailbox, context='default'):
        voicemail = Voicemail()
        voicemail.mailbox = mailbox
        voicemail.context = context

        self.session.begin()
        self.session.add(voicemail)
        self.session.commit()

        return voicemail.uniqueid

    def test_get(self):
        voicemail_mailbox = 'mailbox'
        voicemail_id = self._insert_voicemail(voicemail_mailbox)

        voicemail = voicemail_dao.get(voicemail_id)

        self.assertEqual(voicemail.mailbox, voicemail_mailbox)

    def test_all(self):
        voicemail1 = self._insert_voicemail('mailbox1')
        voicemail2 = self._insert_voicemail('mailbox2')
        voicemail3 = self._insert_voicemail('mailbox3')

        result = voicemail_dao.all()[0]

        self.assertEqual(result.uniqueid, voicemail1)

        result = voicemail_dao.all()[1]

        self.assertEqual(result.uniqueid, voicemail2)

        result = voicemail_dao.all()[2]

        self.assertEqual(result.uniqueid, voicemail3)

    def test_all_empty(self):
        result = voicemail_dao.all()
        self.assertEqual([], result)
