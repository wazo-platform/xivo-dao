# -*- coding: utf-8 -*-
# Copyright 2014-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

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
