# -*- coding: utf-8 -*-

# Copyright (C) 2012-2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
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

from __future__ import unicode_literals

from sqlalchemy.orm import relationship
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

    line = relationship('LineFeatures',
                        primaryjoin="""and_(
                            LineFeatures.protocol == 'sccp',
                            LineFeatures.protocolid == SCCPLine.id
                        )""",
                        foreign_keys='LineFeatures.protocolid',
                        uselist=False,
                        viewonly=True,
                        back_populates='endpoint_sccp')

    @property
    def options(self):
        options = []
        if self.cid_name != "":
            options.append(["cid_name", self.cid_name])
        if self.cid_num != "":
            options.append(["cid_num", self.cid_num])

        if self.disallow is not None:
            options.append(["disallow", self.disallow])
        if self.allow is not None:
            options.append(["allow", self.allow])

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
                self.allow = value
            elif name == "disallow":
                self.disallow = value
            else:
                raise InputError("Unknown SCCP options: {}".format(name))

    def same_protocol(self, protocol, id):
        return protocol == 'sccp' and self.id == id

    def update_extension(self, extension):
        self.name = extension.exten
        self.context = extension.context

    def update_caller_id(self, user, extension=None):
        name, user_num = user.extrapolate_caller_id(extension)
        self.cid_name = name or ''
        if extension:
            self.cid_num = extension.exten
        elif user_num:
            self.cid_num = user_num
        else:
            self.cid_num = ''

    def endpoint_protocol(self):
        return 'sccp'
