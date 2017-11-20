# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.sql.expression import and_, distinct
from xivo_dao.alchemy.accesswebservice import AccessWebService
from xivo_dao.helpers.db_manager import daosession


@daosession
def get_password(session, login):
    result = (session
              .query(AccessWebService.passwd)
              .filter(and_(AccessWebService.login == login,
                           AccessWebService.disable == 0)).first())
    if result is None:
        return None
    else:
        return result.passwd


@daosession
def get_allowed_hosts(session):
    result = (session
              .query(distinct(AccessWebService.host))
              .filter(and_(AccessWebService.host != None,
                           AccessWebService.disable == 0)).all())
    result = [item[0].encode('utf-8', 'ignore') for item in result]
    return result


@daosession
def get_user_uuid(session, login):
    result = (session
              .query(AccessWebService.uuid)
              .filter(and_(AccessWebService.login == login,
                           AccessWebService.disable == 0)).scalar())
    if result is None:
        raise LookupError('No such webservice user: {}'.format(login))
    return result


@daosession
def check_username_password(session, login, password):
    result = (session
              .query(AccessWebService.login)
              .filter(and_(AccessWebService.login == login,
                           AccessWebService.passwd == password,
                           AccessWebService.disable == 0)).all())

    return len(result) > 0


@daosession
def get_services(session):
    results = (session
               .query(AccessWebService.login,
                      AccessWebService.passwd)
               .filter(and_(AccessWebService.login != None,
                            AccessWebService.disable == 0)).all())
    return results


@daosession
def get_user_acl(session, login):
    result = (session
              .query(AccessWebService.acl)
              .filter(and_(AccessWebService.login == login,
                           AccessWebService.disable == 0)).first())
    return result.acl
