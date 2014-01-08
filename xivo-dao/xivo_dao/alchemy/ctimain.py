# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
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

from sqlalchemy.schema import Column, Sequence
from sqlalchemy.types import Integer, String
from xivo_dao.helpers.db_manager import Base


class CtiMain(Base):

    __tablename__ = 'ctimain'

    id = Column(Integer, Sequence('ctimain_id_seq'), primary_key=True)
    commandset = Column(String(20))
    ami_ip = Column(String(16))
    ami_port = Column(Integer)
    ami_login = Column(String(64))
    ami_password = Column(String(64))
    cti_ip = Column(String(16))
    cti_port = Column(Integer)
    cti_active = Column(Integer, nullable=False, default=1)
    ctis_ip = Column(String(16))
    ctis_port = Column(Integer)
    ctis_active = Column(Integer, nullable=False, default=1)
    webi_ip = Column(String(16))
    webi_port = Column(Integer)
    webi_active = Column(Integer, nullable=False, default=1)
    info_ip = Column(String(16))
    info_port = Column(Integer)
    info_active = Column(Integer, nullable=False, default=1)
    tlscertfile = Column(String(128))
    tlsprivkeyfile = Column(String(128))
    socket_timeout = Column(Integer)
    login_timeout = Column(Integer)
    context_separation = Column(Integer)
    live_reload_conf = Column(Integer)
