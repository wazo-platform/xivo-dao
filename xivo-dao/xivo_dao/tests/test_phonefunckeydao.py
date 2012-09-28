# -*- coding: UTF-8 -*-

from xivo_dao.alchemy.phonefunckey import PhoneFunckey
from xivo_dao.phonefunckeydao import PhoneFunckeyDAO
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

        self.session.add(fwd_unc)

        fwd_unc_no_dest = PhoneFunckey()
        fwd_unc_no_dest.iduserfeatures = self._user_id_no_dest
        fwd_unc_no_dest.fknum = 2
        fwd_unc_no_dest.typeextenumbers = 'extenfeatures'
        fwd_unc_no_dest.typevalextenumbers = 'fwdunc'
        fwd_unc_no_dest.supervision = 1
        fwd_unc_no_dest.progfunckey = 1

        self.session.add(fwd_unc_no_dest)

        fwd_rna = PhoneFunckey()
        fwd_rna.iduserfeatures = self._user_id
        fwd_rna.fknum = 3
        fwd_rna.exten = self._destination_rna
        fwd_rna.typeextenumbers = 'extenfeatures'
        fwd_rna.typevalextenumbers = 'fwdrna'
        fwd_rna.supervision = 1
        fwd_rna.progfunckey = 1

        self.session.add(fwd_rna)

        self.session.commit()

    def test_get_destination_unc(self):
        dao = PhoneFunckeyDAO(self.session)

        reply = dao.get_dest_unc(self._user_id)

        self.assertEqual(reply, [self._destination_unc])

    def test_get_destination_unc_no_destination(self):
        dao = PhoneFunckeyDAO(self.session)

        reply = dao.get_dest_unc(self._user_id_no_dest)

        self.assertEqual(reply, [''])

    def test_get_destination_rna(self):
        dao = PhoneFunckeyDAO(self.session)

        reply = dao.get_dest_rna(self._user_id)

        self.assertEqual(reply, [self._destination_rna])
