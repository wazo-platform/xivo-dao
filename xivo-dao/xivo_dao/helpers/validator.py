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

from xivo_dao.data_handler.context import services as context_services


def is_positive_number(string):
    if str(string).isdigit() and int(string) > 0:
        return True
    else:
        return False


def is_context_exist(context_name):
    return context_services.find_by_name(context_name)
