# -*- coding: utf-8 -*-

# Copyright 2014-2017 The Wazo Authors  (see the AUTHORS file)
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

import abc
import six

from xivo_dao.helpers import errors


class ViewSelector(object):

    def __init__(self, default, **views):
        self.default = default
        self.views = views

    def select(self, name=None):
        if name is None:
            return self.default
        if name not in self.views:
            raise errors.invalid_view(name)
        return self.views[name]


@six.add_metaclass(abc.ABCMeta)
class View(object):

    @abc.abstractmethod
    def query(self, session):
        return

    @abc.abstractmethod
    def convert(self, row):
        return

    def convert_list(self, rows):
        return [self.convert(row) for row in rows]


class ModelView(View):

    @abc.abstractproperty
    def table(self):
        return

    @abc.abstractproperty
    def db_converter(self):
        return

    def query(self, session):
        return session.query(self.table)

    def convert(self, row):
        return self.db_converter.to_model(row)
