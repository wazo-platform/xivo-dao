# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
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
from xivo_dao.resources.line_extension.persistor import LineExtensionPersistor


def get_by(**criteria):
    return LineExtensionPersistor(Session).get_by(**criteria)


def find_by(**criteria):
    return LineExtensionPersistor(Session).find_by(**criteria)


def find_all_by(**criteria):
    return LineExtensionPersistor(Session).find_all_by(**criteria)


def associate(line, extension):
    return LineExtensionPersistor(Session).associate_line_extension(line, extension)


def dissociate(line, extension):
    return LineExtensionPersistor(Session).dissociate_line_extension(line, extension)


def find_all_by_line_id(line_id):
    return LineExtensionPersistor(Session).find_all_by(line_id=line_id)


def find_by_line_id(line_id):
    return LineExtensionPersistor(Session).find_by(line_id=line_id)


def find_by_extension_id(extension_id):
    return LineExtensionPersistor(Session).find_by(extension_id=extension_id)
