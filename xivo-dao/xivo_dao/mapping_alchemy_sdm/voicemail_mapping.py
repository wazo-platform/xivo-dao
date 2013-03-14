# -*- coding: UTF-8 -*-
#
# Copyright (C) 2012  Avencall
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
from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao.service_data_model.voicemail_sdm import VoicemailSdm
from xivo_dao.helpers import object_mapping


#mapping = {alchemy_field: sdm_field}
mapping = {'uniqueid': 'id',
           'email': 'email',
           'fullname': 'fullname',
           'mailbox': 'mailbox',
           'password': 'password',
           'attach': 'attach',
           'skipcheckpass': 'skipcheckpass',
           'deletevoicemail': 'deleteaftersend'
           }

reverse_mapping = dict([[v, k] for k, v in mapping.items()])

alchemy_default_values = {'context': 'default',
                          'tz': 'eu-fr'}

alchemy_types = {
                'uniqueid': int,
                   'email': str,
                   'fullname': str,
                   'mailbox': str,
                   'password': str,
                   'attach': int,
                   'skipcheckpass': int,
                   'deletevoicemail': int
                 }


def alchemy_to_sdm(voicemail_alchemy):
    voicemail_sdm = VoicemailSdm()
    return object_mapping.map_attributes(voicemail_alchemy,
                                         voicemail_sdm,
                                         mapping)


def sdm_to_alchemy(voicemail_sdm):
    voicemail_alchemy = Voicemail()

    return object_mapping.map_attributes(voicemail_sdm,
                                         voicemail_alchemy,
                                         reverse_mapping,
                                         alchemy_default_values)


def sdm_to_alchemy_dict(voicemail_dict):

    result = {}
    for k in voicemail_dict:
        if k in reverse_mapping:
            new_key = reverse_mapping[k]
            result[new_key] = voicemail_dict[k]
            result[new_key] = alchemy_types[new_key](result[new_key])
        else:
            raise AttributeError()

    return result
