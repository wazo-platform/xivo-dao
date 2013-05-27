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
from xivo_dao.alchemy.contextmember import ContextMember


class VoicemailDAOTestCase(DAOTestCase):

    tables = [Voicemail, ContextMember]

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

    def _insert_contextmember(self, voicemailid):
        member = ContextMember(context='default', type='voicemail', typeval=str(voicemailid), varname='context')
        self.add_me(member)

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

    def test_add(self):
        voicemail = Voicemail()
        voicemail.mailbox = "123"
        voicemail.context = "default"

        voicemail_dao.add(voicemail)

        self.assertTrue(voicemail.uniqueid > 0)
        returned_voicemail = (self.session.query(Voicemail).filter(Voicemail.uniqueid == voicemail.uniqueid)
                                                           .first())
        self.assertEquals(returned_voicemail, voicemail)
        contextmember = (self.session.query(ContextMember).filter(ContextMember.type == 'voicemail')
                                                          .filter(ContextMember.typeval == str(voicemail.uniqueid))
                                                          .first())
        self.assertEquals(contextmember.context, voicemail.context)

    def test_update(self):
        voicemailid = self._insert_voicemail("123")
        data = {"mailbox": "456",
                "fullname": "test"}
        voicemail_dao.update(voicemailid, data)
        updated_voicemail = voicemail_dao.get(voicemailid)
        self.assertEquals(updated_voicemail.mailbox, "456")
        self.assertEquals(updated_voicemail.fullname, "test")

    def test_id_from_mailbox(self):
        generated_id = self._insert_voicemail("123", "default")
        result = voicemail_dao.id_from_mailbox("123", "default")
        self.assertEquals(result, generated_id)

    def test_id_from_mailbox_unexisting(self):
        result = voicemail_dao.id_from_mailbox("123", "default")
        self.assertEquals(result, None)

    def test_delete(self):
        generated_id = self._insert_voicemail("123", "default")
        self._insert_contextmember(generated_id)

        impacted_rows = voicemail_dao.delete(generated_id)

        self.assertEquals(impacted_rows, 1)
        inserted_contextmember = (self.session.query(ContextMember)
                                             .filter(ContextMember.type == 'voicemail')
                                             .filter(ContextMember.typeval == str(generated_id))
                                             .first())
        self.assertEquals(None, inserted_contextmember)

    def test_get_contextmember(self):
        voicemailid = self._insert_voicemail('123', 'default')
        self._insert_contextmember(voicemailid)

        member = voicemail_dao.get_contextmember(voicemailid)

        self.assertNotEquals(None, member)
