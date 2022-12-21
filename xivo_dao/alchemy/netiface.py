# Copyright 2014-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.types import Integer, String, Text, Enum

from xivo_dao.helpers.db_manager import Base
from xivo_dao.alchemy import enum


class Netiface(Base):

    __tablename__ = 'netiface'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('ifname'),
    )

    id = Column(Integer, nullable=False)
    ifname = Column(String(64), nullable=False, server_default='')
    hwtypeid = Column(Integer, nullable=False, server_default='65534')
    networktype = Column(Enum('data',
                              'voip',
                              name='netiface_networktype',
                              metadata=Base.metadata),
                         nullable=False)
    type = Column(enum.netiface_type, nullable=False)
    family = Column(Enum('inet',
                         'inet6',
                         name='netiface_family',
                         metadata=Base.metadata),
                    nullable=False)
    method = Column(Enum('static',
                         'dhcp',
                         'manual',
                         name='netiface_method',
                         metadata=Base.metadata))
    address = Column(String(39))
    netmask = Column(String(39))
    broadcast = Column(String(15))
    gateway = Column(String(39))
    mtu = Column(Integer)
    vlanrawdevice = Column(String(64))
    vlanid = Column(Integer)
    options = Column(Text, nullable=False)
    disable = Column(Integer, nullable=False, server_default='0')
    dcreate = Column(Integer, nullable=False, server_default='0')
    description = Column(Text)
