# Copyright 2015-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.exception import InputError
from xivo_dao.helpers.exception import ResourceError
from xivo_dao.helpers.exception import NotFoundError


def format_error(category, error, metadata=None):
    metadata = metadata or {}
    template = "{category} - {error} {metadata}"
    message = template.format(
        category=category, error=error, metadata=_format_metadata(metadata)
    )
    return message.strip()


def _format_metadata(metadata):
    if len(metadata) == 0:
        return ''
    return f"({str(metadata).strip('{}')})"


def _format_list(elements):
    return ', '.join(elements)


class FormattedError:
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


minimum_length = FormattedError(
    InputError, "field '{}': must have a minimum length of {}"
)
invalid_direction = FormattedError(InputError, "direction: must be 'asc' or 'desc'")
invalid_ordering = FormattedError(InputError, "order: column '{}' was not found")
wrong_type = FormattedError(InputError, "field '{}': wrong type. Should be a {}")
outside_context_range = FormattedError(
    InputError, "Extension '{}' is outside of range for context '{}'"
)
outside_park_range = FormattedError(
    InputError, "Parking position '{}' is outside of range"
)
outside_range = FormattedError(InputError, "{} is outside of range")
invalid_func_key_type = FormattedError(InputError, "FuncKey type '{}' does not exist")
invalid_destination_type = FormattedError(
    InputError, "FuncKey destination type '{}' does not exist"
)
param_not_found = FormattedError(InputError, "field '{}': {} was not found")
invalid_query_parameter = FormattedError(
    InputError, "parameter '{}': '{}' is not valid"
)
invalid_view = FormattedError(InputError, "view '{}' does not exist")
ivr_exten_used = FormattedError(InputError, "exten '{}' used in more than one choice")
invalid_exten_pattern = FormattedError(InputError, "exten '{}' cannot be a pattern")
moh_custom_no_app = FormattedError(InputError, "custom mode must have an application")

not_found = FormattedError(NotFoundError, "{} was not found")

resource_exists = FormattedError(ResourceError, "{} already exists")
resource_associated = FormattedError(ResourceError, "{} is associated with a {}")
resource_not_associated = FormattedError(ResourceError, "{} is not associated with {}")
missing_association = FormattedError(ResourceError, "{} must be associated with a {}")
forward_destination_null = FormattedError(
    ResourceError, "Forward must be disabled to remove destination"
)
unhandled_context_type = FormattedError(
    ResourceError, "ContextType '{}' cannot be associated"
)
secondary_users = FormattedError(
    ResourceError, "There are secondary users associated to the line"
)
not_permitted = FormattedError(ResourceError, "Operation not permitted. {}")
different_tenants = FormattedError(ResourceError, "different tenants")
quota_exceeded = FormattedError(ResourceError, "Quota for {} exceeded. Maximum: {}")
extension_conflict = FormattedError(
    ResourceError, "{} is already used for a destination or parking slot"
)
