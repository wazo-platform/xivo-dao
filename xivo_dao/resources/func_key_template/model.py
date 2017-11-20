# -*- coding: UTF-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from collections import namedtuple

from xivo_dao.helpers import errors

from xivo_dao.helpers.new_model import NewModel


class FuncKeyTemplate(NewModel):

    FIELDS = ['id',
              'name',
              'private',
              'keys']

    MANDATORY = []

    _RELATION = {}

    def __init__(self, **parameters):
        parameters.setdefault('keys', {})
        parameters.setdefault('private', False)
        super(FuncKeyTemplate, self).__init__(**parameters)

    def merge(self, other):
        keys = dict(self.keys)
        other_keys = other.keys
        keys.update(other_keys)
        return FuncKeyTemplate(keys=keys)

    def get(self, position):
        if position not in self.keys:
            raise errors.not_found('FuncKey', template_id=self.id, position=position)
        return self.keys[position]


UserTemplate = namedtuple('UserTemplate', ['user_id', 'template_id'])
