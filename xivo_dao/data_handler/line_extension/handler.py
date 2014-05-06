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


class LineExtensionHandler(object):

    def __init__(self, context_dao, validator, registry):
        self.context_dao = context_dao
        self.validator = validator
        self.registry = registry

    def associate(self, line_extension):
        handler = self._get_handler(line_extension)

        self.validate(line_extension)
        handler.associate(line_extension)

    def _get_handler(self, line_extension):
        context = self.context_dao.get_by_extension_id(line_extension.extension_id)

        if context.type not in self.registry:
            raise NotImplementedError("Handler for contexts of type '%s' not implemented" % context.type)

        return self.registry[context.type]

    def validate(self, line_extension):
        handler = self._get_handler(line_extension)

        self.validator.validate_model(line_extension)
        self.validator.validate_line(line_extension)
        self.validator.validate_extension(line_extension)
        handler.validate(line_extension)

    def dissociate(self, line_extension):
        handler = self._get_handler(line_extension)

        self.validate(line_extension)
        handler.dissociate(line_extension)
