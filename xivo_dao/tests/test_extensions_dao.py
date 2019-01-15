# -*- coding: utf-8 -*-
# Copyright (C) 2007-2015 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao import extensions_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestExtensionsDAO(DAOTestCase):

    def test_exten_by_name(self):
        self.add_extension(type='extenfeatures',
                           typeval='enablednd',
                           exten='*25')
        self.add_extension(type='extenfeatures',
                           typeval='phoneprogfunckey',
                           exten='_*735')
        enablednd = extensions_dao.exten_by_name('enablednd')
        phoneprogfunckey = extensions_dao.exten_by_name('phoneprogfunckey')
        foo = extensions_dao.exten_by_name('foo')

        self.assertEqual(enablednd, '*25')
        self.assertEqual(phoneprogfunckey, '_*735')
        self.assertEqual(foo, '')
