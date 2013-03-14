'''
Created on Mar 14, 2013

@author: jean
'''
from xivo_dao.service_data_model.base_sdm import BaseSdm
import unittest
from xivo_dao.service_data_model.sdm_exception import IncorrectParametersException


class TestBaseSdm(unittest.TestCase):

    def test_todict(self):
        base_instance = BaseSdm()
        base_instance.attr1 = 'val1'
        base_instance.attr2 = 2
        base_instance.attr3 = None
        expected_result = {'attr1': 'val1',
                           'attr2': 2,
                           'attr3': None}

        result = base_instance.todict()
        self.assertEquals(result, expected_result)

    def test_validate_success(self):
        base_instance = BaseSdm()
        base_instance.attr1 = 'val1'
        base_instance.attr2 = 2
        base_instance.attr3 = None

        data = {'attr3': None,
                'attr2': 'value2'}
        self.assertTrue(base_instance.validate(data))

    def test_validate_fail(self):
        base_instance = BaseSdm()
        base_instance.attr1 = 'val1'
        base_instance.attr2 = 2
        base_instance.attr3 = None

        data = {'attr11': 1,
                'attr': 'value2',
                'attr3': None}
        try:
            base_instance.validate(data)
        except IncorrectParametersException as e:
            self.assertEqual(str(e), 'Incorrect parameters sent: attr11, attr')
            return

        self.assertTrue(False, 'Exception not raised!')

