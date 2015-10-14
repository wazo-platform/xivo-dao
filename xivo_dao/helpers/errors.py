# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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

from __future__ import unicode_literals

from xivo_dao.helpers.exception import InputError
from xivo_dao.helpers.exception import ResourceError
from xivo_dao.helpers.exception import NotFoundError


def format_error(category, error, metadata=None):
    metadata = metadata or {}
    template = "{category} - {error} {metadata}"
    message = template.format(category=category,
                              error=error,
                              metadata=_format_metadata(metadata))
    return message.strip()


def _format_metadata(metadata):
    if len(metadata) == 0:
        return ''
    return "({})".format(unicode(metadata).strip("{}"))


def _format_list(elements):
    return ', '.join(elements)


class FormattedError(object):

    def __init__(self, exception, error_template):
        self.exception = exception
        self.error_template = error_template

    def __call__(self, *args, **metadata):
        message = self._format_message(args, metadata)
        error = self.exception(message, metadata)
        return error

    def _format_message(self, args, metadata):
        error = self.error_template.format(*args)
        message = format_error(self.exception.prefix, error, metadata)
        return message


def missing(*params):
    template = "missing parameters: {params}"
    message = template.format(params=_format_list(params))
    error = format_error('Input Error', message)
    return InputError(error)


def unknown(*params):
    template = "unknown parameters: {params}"
    message = template.format(params=_format_list(params))
    error = format_error('Input Error', message)
    return InputError(error)


def invalid_choice(field, choices, **metadata):
    template = "'{field}' must be one of ({choices})"
    message = template.format(field=field, choices=_format_list(choices))
    error = format_error('Input Error', message, metadata)
    return InputError(error)


minimum_length = FormattedError(InputError, "field '{}': must have a minimum length of {}")
invalid_direction = FormattedError(InputError, "direction: must be 'asc' or 'desc'")
invalid_ordering = FormattedError(InputError, "order: column '{}' was not found")
wrong_type = FormattedError(InputError, "field '{}': wrong type. Should be a {}")
outside_context_range = FormattedError(InputError, "Extension '{}' is outside of range for context '{}'")
outside_park_range = FormattedError(InputError, "Parking position '{}' is outside of range")
invalid_func_key_type = FormattedError(InputError, "FuncKey type '{}' does not exist")
invalid_destination_type = FormattedError(InputError, "FuncKey destination type '{}' does not exist")
param_not_found = FormattedError(InputError, "field '{}': {} was not found")
invalid_query_parameter = FormattedError(InputError, "parameter '{}': '{}' is not valid")
invalid_view = FormattedError(InputError, "view '{}' does not exist")

not_found = FormattedError(NotFoundError, "{} was not found")

resource_exists = FormattedError(ResourceError, "{} already exists")
resource_associated = FormattedError(ResourceError, "{} is associated with a {}")
resource_not_associated = FormattedError(ResourceError, "{} is not associated with {}")
missing_association = FormattedError(ResourceError, "{} must be associated with a {}")
missing_cti_parameters = FormattedError(ResourceError, "User must have a username and password to enable a CtiProfile")
unhandled_context_type = FormattedError(ResourceError, "ContextType '{}' cannot be associated")
secondary_users = FormattedError(ResourceError, "There are secondary users associated to the line")
not_permitted = FormattedError(ResourceError, "Operation not permitted. {}")
