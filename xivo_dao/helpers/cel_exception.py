# Copyright 2009-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


class CELException(Exception):
    pass


class MissingCELEventException(CELException):
    pass
