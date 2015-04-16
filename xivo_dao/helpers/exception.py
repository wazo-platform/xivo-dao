# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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


class ServiceError(ValueError):

    template = "{prefix} - {message} {metadata}"
    prefix = "Error"

    def __init__(self, message=None, metadata=None):
        super(ServiceError, self).__init__(message)
        self.metadata = metadata


class InputError(ServiceError):

    prefix = "Input Error"


class ResourceError(ServiceError):

    prefix = "Resource Error"


class NotFoundError(ServiceError):

    prefix = "Resource Not Found"


class DataError(IOError):

    @classmethod
    def on_create(cls, resource, error):
        return cls.on_action('create', resource, error)

    @classmethod
    def on_edit(cls, resource, error):
        return cls.on_action('edit', resource, error)

    @classmethod
    def on_delete(cls, resource, error):
        return cls.on_action('delete', resource, error)

    @classmethod
    def on_action(cls, resource, action, error):
        msg = "Could not %s %s: %s" % (resource, action, error)
        return cls(msg)
