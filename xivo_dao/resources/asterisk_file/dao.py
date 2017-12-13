# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_manager import daosession

from .persistor import AsteriskFilePersistor


@daosession
def find_by(session, **kwargs):
    return AsteriskFilePersistor(session).find_by(**kwargs)


@daosession
def edit(session, asterisk_file):
    AsteriskFilePersistor(session).edit(asterisk_file)


@daosession
def edit_section_variables(session, section, variables):
    AsteriskFilePersistor(session).edit_section_variables(section, variables)
