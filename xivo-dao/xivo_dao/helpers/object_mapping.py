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


def map_attributes(src_object, dst_object, mapping, default_values={}):
    for dst_field in default_values:
        value = default_values[dst_field]
        setattr(dst_object, dst_field, value)
    for src_field in mapping:
        if src_field in src_object.__dict__:
            dst_field = mapping[src_field]
            value = getattr(src_object, src_field)
            setattr(dst_object, dst_field, value)
    return dst_object
