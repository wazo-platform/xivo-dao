# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_manager import Session
from xivo_dao.resources.line_extension.persistor import LineExtensionPersistor


def get_by(**criteria):
    return LineExtensionPersistor(Session).get_by(**criteria)


def find_by(**criteria):
    return LineExtensionPersistor(Session).find_by(**criteria)


def find_all_by(**criteria):
    return LineExtensionPersistor(Session).find_all_by(**criteria)


def associate(line, extension):
    return LineExtensionPersistor(Session).associate_line_extension(line, extension)


def dissociate(line, extension):
    return LineExtensionPersistor(Session).dissociate_line_extension(line, extension)


def find_all_by_line_id(line_id):
    return LineExtensionPersistor(Session).find_all_by(line_id=line_id)


def find_by_line_id(line_id):
    return LineExtensionPersistor(Session).find_by(line_id=line_id)


def find_by_extension_id(extension_id):
    return LineExtensionPersistor(Session).find_by(extension_id=extension_id)
