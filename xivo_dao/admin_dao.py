# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy import and_

from xivo_dao.alchemy.user import User
from xivo_dao.alchemy.entity import Entity
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.helpers import errors


@daosession
def check_username_password(session, username, password):
    row = session.query(User).filter(and_(User.login == username,
                                          User.passwd == password,
                                          User.valid == 1)).first()

    return row is not None


@daosession
def get_admin_entity(session, username):
    filter_ = and_(
        User.login == username,
        User.valid == 1,
    )
    entity = session.query(Entity.name, Entity.tenant_uuid).join(User).filter(filter_).first()
    if not entity:
        return None, None

    return entity.name, entity.tenant_uuid


@daosession
def get_admin_uuid(session, username):
    filter_ = and_(User.login == username, User.valid == 1)
    uuid = session.query(User.uuid).filter(filter_).scalar()
    if not uuid:
        raise errors.not_found('User', {'username': username})

    return uuid
