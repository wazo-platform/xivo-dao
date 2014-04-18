# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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


def associate_line_extension(line_extension):
    raise NotImplementedError()


def associate_user_line(user_line):
    raise NotImplementedError()


def make_user_line_associations(user_line):
    main_user_line = dao.find_main_user_line(user_line.line_id)
    line_extension = line_extension_dao.find_by_line_id(user_line.line_id)
    extension_id = line_extension.extension_id if line_extension else None
    ule_helper.make_associations(main_user_line.user_id, user_line.line_id, extension_id)
