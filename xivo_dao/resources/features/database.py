# -*- coding: utf-8 -*-

# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

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
