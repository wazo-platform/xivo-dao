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

from xivo_dao.alchemy.phonefunckey import PhoneFunckey
from xivo_dao import phonefunckey_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestPhoneFunckey(DAOTestCase):

    tables = [PhoneFunckey]

    def setUp(self):
        self.empty_tables()
        self._user_id = 19
        self._user_id_no_dest = 21
        self._destination_unc = '123'
        self._destination_rna = '234'

        self._insert_funckeys()

    def _insert_funckeys(self):
        fwd_unc = PhoneFunckey()
        fwd_unc.iduserfeatures = self._user_id
        fwd_unc.fknum = 2
        fwd_unc.exten = self._destination_unc
        fwd_unc.typeextenumbers = 'extenfeatures'
        fwd_unc.typevalextenumbers = 'fwdunc'
        fwd_unc.supervision = 1
        fwd_unc.progfunckey = 1

        fwd_unc_no_dest = PhoneFunckey()
        fwd_unc_no_dest.iduserfeatures = self._user_id_no_dest
        fwd_unc_no_dest.fknum = 2
        fwd_unc_no_dest.typeextenumbers = 'extenfeatures'
        fwd_unc_no_dest.typevalextenumbers = 'fwdunc'
        fwd_unc_no_dest.supervision = 1
        fwd_unc_no_dest.progfunckey = 1

        fwd_rna = PhoneFunckey()
        fwd_rna.iduserfeatures = self._user_id
        fwd_rna.fknum = 3
        fwd_rna.exten = self._destination_rna
        fwd_rna.typeextenumbers = 'extenfeatures'
        fwd_rna.typevalextenumbers = 'fwdrna'
        fwd_rna.supervision = 1
        fwd_rna.progfunckey = 1

        self.session.begin()
        self.session.add(fwd_unc)
        self.session.add(fwd_unc_no_dest)
        self.session.add(fwd_rna)
        self.session.commit()

    def test_get_destination_unc(self):
        reply = phonefunckey_dao.get_dest_unc(self._user_id)

        self.assertEqual(reply, [self._destination_unc])

    def test_get_destination_unc_no_destination(self):
        reply = phonefunckey_dao.get_dest_unc(self._user_id_no_dest)

        self.assertEqual(reply, [''])

    def test_get_destination_rna(self):
        reply = phonefunckey_dao.get_dest_rna(self._user_id)

        self.assertEqual(reply, [self._destination_rna])

    def test_add(self):
        fwd_unc = PhoneFunckey()
        fwd_unc.iduserfeatures = self._user_id
        fwd_unc.fknum = 9
        fwd_unc.exten = self._destination_unc
        fwd_unc.typeextenumbers = 'extenfeatures'
        fwd_unc.typevalextenumbers = 'fwdunc'
        fwd_unc.supervision = 1
        fwd_unc.progfunckey = 1
        fwd_unc.label = 'my label for test_add'

        phonefunckey_dao.add(fwd_unc)
        self.assertNotEquals(None, self.session.query(PhoneFunckey)\
                                               .filter(PhoneFunckey.label == 'my label for test_add')\
                                               .first())

    def test_get_by_userid(self):
        result = phonefunckey_dao.get_by_userid(self._user_id)
        self.assertEquals(2, len(result))
        self.assertEquals(self._user_id, result[0].iduserfeatures)
        self.assertEquals(self._user_id, result[1].iduserfeatures)

    def test_delete_by_userid(self):
        phonefunckey_dao.delete_by_userid(self._user_id)
        result = self.session.query(PhoneFunckey).all()
        self.assertEquals(1, len(result))
        self.assertEquals(self._user_id_no_dest, result[0].iduserfeatures)
