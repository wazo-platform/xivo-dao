from xivo_dao.tests import test_dao
from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.phonefunckey import PhoneFunckey
from xivo_dao.phonefunckeydao import PhoneFunckeyDAO


class TestPhoneFunckey(test_dao.DAOTestCase):

    required_tables = [PhoneFunckey.__table__]

    def setUp(self):
        self._user_id = 19
        self._destination_unc = '123'
        self._destination_rna = '234'
        db_connection_pool = dbconnection.DBConnectionPool(dbconnection.DBConnection)
        dbconnection.register_db_connection_pool(db_connection_pool)

        uri = 'postgresql://asterisk:asterisk@localhost/asterisktest'
        dbconnection.add_connection_as(uri, 'asterisk')
        connection = dbconnection.get_connection('asterisk')

        self.cleanTables()

        self.session = connection.get_session()

        self._insert_funckeys()

        self.session.commit()

    def tearDown(self):
        dbconnection.unregister_db_connection_pool()

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

        fwd_rna = PhoneFunckey()
        fwd_rna.iduserfeatures = self._user_id
        fwd_rna.fknum = 3
        fwd_rna.exten = self._destination_rna
        fwd_rna.typeextenumbers = 'extenfeatures'
        fwd_rna.typevalextenumbers = 'fwdrna'
        fwd_rna.supervision = 1
        fwd_rna.progfunckey = 1

        self.session.add(fwd_rna)

    def test_get_destination_unc(self):
        dao = PhoneFunckeyDAO(self.session)

        reply = dao.get_dest_unc(self._user_id)

        self.assertEqual(reply, [self._destination_unc])

    def test_get_destination_rna(self):
        dao = PhoneFunckeyDAO(self.session)

        reply = dao.get_dest_rna(self._user_id)

        self.assertEqual(reply, [self._destination_rna])
