# -*- coding: utf-8 -*-

# Copyright (C) 2012-2015 Avencall
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

from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String, Text

from xivo_dao.helpers.exception import InputError
from xivo_dao.helpers.db_manager import Base
from xivo_dao.alchemy import enum


class SCCPLine(Base):

    __tablename__ = 'sccpline'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
    )

    id = Column(Integer)
    name = Column(String(80), nullable=False)
    context = Column(String(80), nullable=False)
    cid_name = Column(String(80), nullable=False)
    cid_num = Column(String(80), nullable=False)
    disallow = Column(String(100))
    allow = Column(Text)
    protocol = Column(enum.trunk_protocol, nullable=False, server_default='sccp')
    commented = Column(Integer, nullable=False, server_default='0')

    @property
    def options(self):
        options = []
        if self.cid_name != "":
            options.append(["cid_name", self.cid_name])
        if self.cid_num != "":
            options.append(["cid_num", self.cid_num])

        if self.allow is not None:
            for value in self.allow.split(","):
                options.append(["allow", value])
        if self.disallow is not None:
            for value in self.disallow.split(","):
                options.append(["disallow", value])

        return options

    @options.setter
    def options(self, values):
        self.clear_options()
        self.set_options(values)

    def clear_options(self):
        self.allow = None
        self.disallow = None

    def set_options(self, values):
        for name, value in values:
            if name == "cid_name":
                self.cid_name = value
            elif name == "cid_num":
                self.cid_num = value
            elif name == "allow":
                self.add_comma_option("allow", value)
            elif name == "disallow":
                self.add_comma_option("disallow", value)
            else:
                raise InputError("Unknown SCCP options: {}".format(name))

    def add_comma_option(self, column, value):
        text = getattr(self, column, None)
        values = text.split(",") if text else []
        values.append(value)
        setattr(self, column, ",".join(values))

    def same_protocol(self, protocol, id):
        return protocol == 'sccp' and self.id == id

    def update_extension(self, extension):
        self.name = extension.exten
        self.context = extension.context

    def update_caller_id(self, user, extension=None):
        name, num = user.extrapolate_caller_id(extension)
        self.cid_name = name or ''
        self.cid_num = num or ''

    def endpoint_protocol(self):
        return 'sccp'
