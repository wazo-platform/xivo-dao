# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import Session
from xivo_dao.resources.user_line.persistor import Persistor


def persistor():
    return Persistor(Session, 'UserLine')


def get_by(**criteria):
    return persistor().get_by(**criteria)


def find_by(**criteria):
    return persistor().find_by(**criteria)


def find_all_by(**criteria):
    return persistor().find_all_by(**criteria)


def find_all_by_user_id(user_id):
    return find_all_by(user_id=user_id)


def find_all_by_line_id(line_id):
    return find_all_by(line_id=line_id)


def find_main_user_line(line_id):
    return find_by(line_id=line_id, main_user=True)


def associate(user, line):
    return persistor().associate_user_line(user, line)


def dissociate(user, line):
    return persistor().dissociate_user_line(user, line)


def associate_all_lines(user, lines):
    return persistor().associate_all_lines(user, lines)
