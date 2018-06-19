# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy import and_

from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.alchemy.func_key_dest_bsfilter import FuncKeyDestBSFilter
from xivo_dao.alchemy.func_key_dest_user import FuncKeyDestUser


class DestinationPersistor(object):

    def __init__(self, session):
        self.session = session

    def create_user_destination(self, user):
        func_key = FuncKey.new_for_user()
        destination = FuncKeyDestUser(func_key=func_key, userfeatures=user)
        self.session.add(func_key)
        self.session.add(destination)
        self.session.flush()

    def delete_user_destination(self, user):
        self.delete_user_func_key(user)
        self.delete_bsfilter_func_key(user)
        self.session.flush()

    def delete_user_func_key(self, user):
        destination = self.session.query(FuncKeyDestUser).filter_by(user_id=user.id).first()
        self.session.delete(destination)

    def delete_bsfilter_func_key(self, user):
        for destination in self.find_secretary_destinations(user):
            self.session.delete(destination)

    def find_secretary_destinations(self, user):
        return (self.session.query(FuncKeyDestBSFilter)
                .join(Callfiltermember,
                      and_(FuncKeyDestBSFilter.filtermember_id == Callfiltermember.id,
                           Callfiltermember.bstype == 'secretary',
                           Callfiltermember.typeval == str(user.id))))
