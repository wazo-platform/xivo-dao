# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
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

from xivo_dao.data_handler.user_voicemail import validator, dao, notifier


def associate(user_voicemail):
    validator.validate_association(user_voicemail)
    dao.associate(user_voicemail)
    notifier.associated(user_voicemail)
    return user_voicemail


def get_by_user_id(user_id):
    return dao.get_by_user_id(user_id)


def dissociate(user_voicemail):
    validator.validate_dissociation(user_voicemail)
    dao.dissociate(user_voicemail)
    notifier.dissociated(user_voicemail)
