# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later


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
