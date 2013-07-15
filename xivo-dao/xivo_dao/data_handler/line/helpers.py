# -*- coding: UTF-8 -*-
#
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

import random
import string

from xivo_dao.alchemy.linefeatures import LineFeatures as LineSchema


def make_provisioning_id(session, provd_id=None):
    if provd_id is None:
        provd_id = ''.join(random.choice(string.digits) for _ in range(6))
    if not _is_valid_provisioning_id(provd_id) or _is_exist_provisioning_id(session, provd_id):
        return make_provisioning_id(session)
    return int(provd_id)


def _is_exist_provisioning_id(session, provd_id):
    line = session.query(LineSchema.id).filter(LineSchema.provisioningid == provd_id).count()
    if line > 0:
        return True
    return False


def _is_valid_provisioning_id(provd_id):
    print provd_id
    if str(provd_id).startswith('0'):
        return False
    elif len(str(provd_id)) != 6:
        return False
    return True
