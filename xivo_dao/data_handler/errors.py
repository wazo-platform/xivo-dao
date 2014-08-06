from __future__ import unicode_literals

from xivo_dao.data_handler.exception import InputError
from xivo_dao.data_handler.exception import ResourceError
from xivo_dao.data_handler.exception import NotFoundError


def format_error(category, error, metadata=None):
    template = "{category} - {error} {metadata}"
    message = template.format(category=category,
                              error=error,
                              metadata=_format_metadata(metadata))
    return message.strip()


def _format_metadata(metadata):
    if metadata is None:
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


minimum_length = FormattedError(InputError, "{} has a minimum length of {}")
invalid_direction = FormattedError(InputError, "direction '{}' invalid (must be 'asc or 'desc')")
invalid_ordering = FormattedError(InputError, "'{}' invalid")
wrong_type = FormattedError(InputError, "'{}' should be typed as a {}")
outside_context_range = FormattedError(InputError, "Extension '{}' is outside of range for context '{}'")
invalid_func_key_type = FormattedError(InputError, "FuncKey type '{}' does not exist")
invalid_destination_type = FormattedError(InputError, "FuncKey destination type '{}' does not exist")
param_not_found = FormattedError(InputError, "{} was not found")

not_found = FormattedError(NotFoundError, "{} was not found")

resource_exists = FormattedError(ResourceError, "{} already exists")
resource_associated = FormattedError(ResourceError, "'{}' is associated with a '{}'")
missing_association = FormattedError(ResourceError, "{} must be associated with a {}")
missing_cti_parameters = FormattedError(ResourceError, "User must have a username and password to enable a CtiProfile")
unhandled_context_type = FormattedError(ResourceError, "ContextType {} cannot be associated")
secondary_users = FormattedError(ResourceError, "there are secondary users associated to the line")
