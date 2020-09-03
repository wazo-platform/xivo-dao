# -*- coding: utf-8 -*-
# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.func_key import FuncKey
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
        self.session.flush()

    def delete_user_func_key(self, user):
        destination = self.session.query(FuncKeyDestUser).filter_by(user_id=user.id).first()
        self.session.delete(destination)
