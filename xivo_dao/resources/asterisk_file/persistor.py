# Copyright 2017-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.asterisk_file import AsteriskFile


class AsteriskFilePersistor:
    def __init__(self, session):
        self.session = session

    def find_by(self, **kwargs):
        query = self.session.query(AsteriskFile).filter_by(**kwargs)
        return query.first()

    def edit(self, asterisk_file):
        self.session.add(asterisk_file)
        self.session.flush()

    def edit_section_variables(self, section, variables):
        section.variables = variables
        self.session.flush()
