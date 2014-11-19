# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

from xivo_dao.helpers import bus_manager
from xivo_bus.resources.func_key import event as func_key_event

from xivo_dao.data_handler.func_key.model import UserFuncKey


def create_user_func_key(func_key):
    return func_key_event.UserCreateFuncKeyEvent(func_key.id, func_key.user_id)


def delete_user_func_key(func_key):
    return func_key_event.UserDeleteFuncKeyEvent(func_key.id, func_key.user_id)


create_events = {UserFuncKey: create_user_func_key}

delete_events = {UserFuncKey: delete_user_func_key}


def created(func_key):
    builder = create_events[func_key.__class__]
    event = builder(func_key)
    bus_manager.send_bus_command(event)


def deleted(func_key):
    builder = delete_events[func_key.__class__]
    event = builder(func_key)
    bus_manager.send_bus_command(event)
