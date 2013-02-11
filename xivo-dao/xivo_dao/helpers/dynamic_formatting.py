# -*- coding: UTF-8 -*-
#
# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from datetime import datetime
from xivo_dao.helpers.cel_exception import InvalidInputException
import logging
import sys
import traceback
#from xivo_restapi.dao.recording_details_dao import RecordingDetailsDao

logger = logging.getLogger(__name__)


def table_to_string(class_instance):
    members = vars(class_instance)
    result = ""
    for n in sorted(set(members)):
        if not n.startswith('_'):
            result += str(n) + ": " + \
                        str(getattr(class_instance, n)) + \
                        ','

    return result.rstrip(',')


def str_to_datetime(string):
    if(type(string) != str and type(string) != unicode):
        raise InvalidInputException("Invalid data provided",
                                    ["invalid_date_format"])
    if (len(string) != 10 and len(string) != 19):
        raise InvalidInputException("Invalid data provided",
                                    ["invalid_date_format"])
    try:
        if(len(string) == 10):
            result = datetime.strptime(string, "%Y-%m-%d")
            return result
        elif(len(string) == 19):
            return datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.error(repr(traceback.format_exception(exc_type, exc_value,
                                          exc_traceback)))
        raise InvalidInputException("Invalid data provided",
                                    ["invalid_date_format"])
