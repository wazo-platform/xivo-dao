# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from collections.abc import Iterable

from xivo_dao.helpers import errors

# taken from the definition of the "ast_true" function in Asterisk source code
_TRUTH_VALUES = [
    'yes',
    'true',
    'y',
    't',
    '1',
    'on',
]


def convert_ast_true_to_int(value):
    return int(value in _TRUTH_VALUES)


def convert_int_to_ast_true(value):
    if value:
        return 'yes'
    return 'no'


class AsteriskOptionsMixin:

    EXCLUDE_OPTIONS = set()
    EXCLUDE_OPTIONS_CONFD = set()
    AST_TRUE_INTEGER_COLUMNS = set()

    @property
    def options(self):
        return self.all_options(self.EXCLUDE_OPTIONS_CONFD)

    def all_options(self, exclude=None):
        native_options = list(self.native_options(exclude))
        return native_options + self._options

    def native_options(self, exclude=None):
        for column in self.native_option_names(exclude):
            value = self.native_option(column)
            if value is not None:
                yield [column, value]

    def native_option(self, column_name):
        value = getattr(self, self._attribute(column_name), None)
        if value is not None and value != "":
            if column_name in self.AST_TRUE_INTEGER_COLUMNS:
                return convert_int_to_ast_true(value)
            else:
                return str(value)
        return None

    @options.setter
    def options(self, options):
        option_names = self.native_option_names(self.EXCLUDE_OPTIONS_CONFD)
        self.reset_options()
        self.set_options(option_names, options)

    def reset_options(self):
        self.reset_extra_options()
        self.reset_native_options()

    def reset_extra_options(self):
        self._options = []

    def reset_native_options(self):
        defaults = self.option_defaults()
        for column in self.native_option_names(self.EXCLUDE_OPTIONS_CONFD):
            value = defaults.get(column, None)
            setattr(self, self._attribute(column), value)

    def set_options(self, option_names, options):
        self.validate_options(options)
        for option in options:
            self.validate_option(option)
            column, value = option
            if column in option_names:
                self.set_native_option(column, value)
            else:
                self.add_extra_option(column, value)

    def validate_options(self, options):
        if not isinstance(options, Iterable):
            raise errors.wrong_type('options', 'list of pair of strings')

    def validate_option(self, option):
        if not isinstance(option, Iterable):
            raise errors.wrong_type('options', 'list of pair of strings')
        if not len(option) == 2:
            raise errors.wrong_type('options', 'list of pair of strings')
        for i in option:
            if not isinstance(i, str):
                raise errors.wrong_type('options', f"value '{i}' is not a string")

    def set_native_option(self, column, value):
        if column in self.AST_TRUE_INTEGER_COLUMNS:
            value = convert_ast_true_to_int(value)
        setattr(self, self._attribute(column), value)

    def add_extra_option(self, name, value):
        self._options.append([name, value])

    def native_option_names(self, exclude=None):
        exclude = set(exclude or []).union(self.EXCLUDE_OPTIONS)
        return {column.name for column in self.__table__.columns} - exclude

    def option_defaults(self):
        defaults = {}
        for column in self.__table__.columns:
            if column.server_default:
                defaults[column.name] = column.server_default.arg
        return defaults

    def _attribute(self, column_name):
        return column_name.replace("-", "_")
