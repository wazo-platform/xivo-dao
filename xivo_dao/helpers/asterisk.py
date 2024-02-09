# Copyright 2016-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from collections.abc import Collection, Iterable
from typing import Literal

from xivo_dao.helpers import errors
from sqlalchemy import Table


# taken from the definition of the "ast_true" function in Asterisk source code
_TRUTH_VALUES = [
    'yes',
    'true',
    'y',
    't',
    '1',
    'on',
]

AST_TRUE = Literal[
    'yes',
    'true',
    'y',
    't',
    '1',
    'on',
]


def convert_ast_true_to_int(value: AST_TRUE) -> int:
    return int(value in _TRUTH_VALUES)


StrBool = Literal['yes', 'no']


def convert_int_to_ast_true(value: int) -> StrBool:
    if value:
        return 'yes'
    return 'no'


class AsteriskOptionsMixin:
    EXCLUDE_OPTIONS: set[str] = set()
    EXCLUDE_OPTIONS_CONFD: set[str] = set()
    AST_TRUE_INTEGER_COLUMNS: set[str] = set()

    _options: list[list[str]]
    __table__: Table

    @property
    def options(self) -> list[list[str]]:
        return self.all_options(self.EXCLUDE_OPTIONS_CONFD)

    def all_options(self, exclude=None) -> list[list[str]]:
        native_options = list(self.native_options(exclude))
        return native_options + self._options

    def native_options(self, exclude=None) -> Iterable[list[str]]:
        for column in self.native_option_names(exclude):
            value = self.native_option(column)
            if value is not None:
                yield [column, value]

    def native_option(self, column_name: str) -> str | None:
        value = getattr(self, self._attribute(column_name), None)
        if value is not None and value != "":
            if column_name in self.AST_TRUE_INTEGER_COLUMNS:
                return convert_int_to_ast_true(value)
            else:
                return str(value)
        return None

    @options.setter  # type: ignore[attr-defined,no-redef]
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

    def validate_options(self, options: Iterable[Collection[str]]):
        if not isinstance(options, Iterable):
            raise errors.wrong_type('options', 'list of pair of strings')

    def validate_option(self, option: Collection[str]):
        if not isinstance(option, Iterable):
            raise errors.wrong_type('options', 'list of pair of strings')
        if not len(option) == 2:
            raise errors.wrong_type('options', 'list of pair of strings')
        for i in option:
            if not isinstance(i, str):
                raise errors.wrong_type('options', f"value '{i}' is not a string")

    def set_native_option(self, column: str, value):
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
