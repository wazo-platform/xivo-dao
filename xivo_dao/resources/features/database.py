# -*- coding: utf-8 -*-

# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

import six

from xivo_dao.resources.features.model import TransferExtension


class TransferExtensionConverter(object):

    TRANSFERS = {'blindxfer': 'blind',
                 'atxfer': 'attended'}

    VAR_NAMES = {value: key for key, value in six.iteritems(TRANSFERS)}

    def var_names(self):
        return list(self.TRANSFERS.keys())

    def to_var_name(self, transfer):
        return self.VAR_NAMES[transfer]

    def to_transfer(self, var_name):
        return self.TRANSFERS[var_name]

    def to_model(self, row):
        transfer = self.TRANSFERS[row.var_name]
        exten = row.var_val
        return TransferExtension(id=row.id,
                                 exten=exten,
                                 transfer=transfer)


transfer_converter = TransferExtensionConverter()
