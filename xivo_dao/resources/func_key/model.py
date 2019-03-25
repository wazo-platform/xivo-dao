# -*- coding: utf-8 -*-
# Copyright 2014-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


class Hint(object):

    __slots__ = ['user_id', 'extension', 'argument']

    def __init__(self, user_id=None, extension=None, argument=None):
        self.user_id = user_id
        self.extension = extension
        self.argument = argument

    def __iter__(self):
        return self

    def __next__(self):
        yield self.user_id
        yield self.extension
        yield self.argument
        raise StopIteration

    def __eq__(self, other):
        return (
            self.user_id == other.user_id
            and self.extension == other.extension
            and self.argument == other.argument,
        )

    def __ne__(self, other):
        return not self == other
