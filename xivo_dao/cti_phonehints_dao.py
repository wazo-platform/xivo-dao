# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_manager import daosession
from xivo_dao.alchemy.ctiphonehintsgroup import CtiPhoneHintsGroup
from xivo_dao.alchemy.ctiphonehints import CtiPhoneHints


@daosession
def get_config(session):
    res = {}
    hintsgroups = (session.query(CtiPhoneHintsGroup).all())
    for hintsgroup in hintsgroups:
        res[hintsgroup.name] = {}
        hints = get_hints_with_group_id(hintsgroup.id)
        for hint in hints:
            res[hintsgroup.name][hint.number] = {}
            res[hintsgroup.name][hint.number]['longname'] = hint.name
            res[hintsgroup.name][hint.number]['color'] = hint.color
    return res


@daosession
def get_hints_with_group_id(session, group_id):
    return session.query(CtiPhoneHints).filter(CtiPhoneHints.idgroup == group_id).all()
