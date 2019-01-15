#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao import voicemail_dao
from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao.alchemy.contextmember import ContextMember
from xivo_dao.tests.test_dao import DAOTestCase


class VoicemailDAOTestCase(DAOTestCase):

    def _insert_voicemail(self, mailbox, context='default'):
        voicemail = Voicemail()
        voicemail.mailbox = mailbox
        voicemail.context = context

        self.add_me(voicemail)

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
        self.assertEqual(returned_voicemail, voicemail)
        contextmember = (self.session.query(ContextMember).filter(ContextMember.type == 'voicemail')
                                                          .filter(ContextMember.typeval == str(voicemail.uniqueid))
                                                          .first())
        self.assertEqual(contextmember.context, voicemail.context)

    def test_update(self):
        voicemailid = self._insert_voicemail("123")
        data = {"mailbox": "456",
                "fullname": "test"}
        voicemail_dao.update(voicemailid, data)
        updated_voicemail = voicemail_dao.get(voicemailid)
        self.assertEqual(updated_voicemail.mailbox, "456")
        self.assertEqual(updated_voicemail.fullname, "test")

    def test_id_from_mailbox(self):
        generated_id = self._insert_voicemail("123", "default")
        result = voicemail_dao.id_from_mailbox("123", "default")
        self.assertEqual(result, generated_id)

    def test_id_from_mailbox_unexisting(self):
        result = voicemail_dao.id_from_mailbox("123", "default")
        self.assertEqual(result, None)

    def test_delete(self):
        generated_id = self._insert_voicemail("123", "default")
        self._insert_contextmember(generated_id)

        impacted_rows = voicemail_dao.delete(generated_id)

        self.assertEqual(impacted_rows, 1)
        inserted_contextmember = (self.session.query(ContextMember)
                                              .filter(ContextMember.type == 'voicemail')
                                              .filter(ContextMember.typeval == str(generated_id))
                                              .first())
        self.assertEqual(None, inserted_contextmember)

    def test_get_contextmember(self):
        voicemailid = self._insert_voicemail('123', 'default')
        self._insert_contextmember(voicemailid)

        member = voicemail_dao.get_contextmember(voicemailid)

        self.assertNotEquals(None, member)
