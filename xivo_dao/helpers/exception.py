# Copyright 2013-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


class ServiceError(ValueError):
    template = "{prefix} - {message} {metadata}"
    prefix = "Error"

    def __init__(self, message=None, metadata=None):
        super().__init__(message)
        self.metadata = metadata


class InputError(ServiceError):
    prefix = "Input Error"


class ResourceError(ServiceError):
    prefix = "Resource Error"


class NotFoundError(ServiceError):
    prefix = "Resource Not Found"
