# -*- coding: utf-8 -*-

# Copyright (C) 2013-2017 Avencall
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

from xivo_dao.helpers.db_manager import Session
from xivo_dao.resources.user_line.persistor import Persistor


def persistor():
    return Persistor(Session, 'UserLine')


def get_by(**criteria):
    return persistor().get_by(**criteria)


def find_by(**criteria):
    return persistor().find_by(**criteria)


def find_all_by(**criteria):
    return persistor().find_all_by(**criteria)


def find_all_by_user_id(user_id):
    return find_all_by(user_id=user_id)


def find_all_by_line_id(line_id):
    return find_all_by(line_id=line_id)


def find_main_user_line(line_id):
    return find_by(line_id=line_id, main_user=True)


def associate(user, line):
    return persistor().associate_user_line(user, line)


def dissociate(user, line):
    return persistor().dissociate_user_line(user, line)


def associate_all_lines(user, lines):
    return persistor().associate_all_lines(user, lines)
