'''
Created on Mar 14, 2013

@author: jean
'''
from xivo_dao.service_data_model.base_sdm import BaseSdm
import unittest


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
