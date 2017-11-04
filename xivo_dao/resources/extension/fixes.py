# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy import Integer
from sqlalchemy.sql import and_, cast

from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.incall import Incall
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.resources.line.fixes import LineFixes


class ExtensionFixes(object):

    def __init__(self, session):
        self.session = session

    def fix(self, extension_id):
        self.fix_extension(extension_id)
        self.fix_lines(extension_id)
        self.session.flush()

    def fix_extension(self, extension_id):
        user_lines = self.find_all_user_line(extension_id)
        if user_lines:
            for user_line in user_lines:
                self.adjust_for_user(extension_id, user_line.user_id)
            return

        incall_id = self.find_incall_id(extension_id)
        if incall_id:
            self.adjust_incall(extension_id, incall_id)
            return

        self.reset_destination(extension_id)

    def fix_lines(self, extension_id):
        line_extensions = self.find_all_line_extension(extension_id)
        for line_extension in line_extensions:
            self.adjust_line(line_extension.line_id)

    def find_all_user_line(self, extension_id):
        return (self.session
                .query(UserLine.user_id)
                .join(LineExtension, LineExtension.line_id == UserLine.line_id)
                .filter(LineExtension.extension_id == extension_id)
                .filter(LineExtension.main_extension == True)  # noqa
                .filter(UserLine.main_user == True)  # noqa
                .all())

    def find_all_line_extension(self, extension_id):
        return (self.session
                .query(LineExtension.line_id)
                .filter(LineExtension.extension_id == extension_id)
                .filter(LineExtension.main_extension == True)  # noqa
                .all())

    def adjust_for_user(self, extension_id, user_id):
        (self.session
         .query(Extension)
         .filter(Extension.id == extension_id)
         .update({'type': 'user',
                  'typeval': str(user_id)}))

    def find_incall_id(self, extension_id):
        return (self.session.query(Incall.id)
                .join(Extension,
                      and_(Extension.type == 'incall',
                           cast(Extension.typeval, Integer) == Incall.id))
                .join(Dialaction,
                      and_(Dialaction.category == 'incall',
                           cast(Dialaction.categoryval, Integer) == Incall.id))
                .filter(Extension.id == extension_id)
                .scalar())

    def adjust_incall(self, extension_id, incall_id):
        row = (self.session.query(Extension.exten,
                                  Extension.context)
               .filter(Extension.id == extension_id)
               .first())

        (self.session.query(Incall)
         .filter(Incall.id == incall_id)
         .update({'exten': row.exten,
                  'context': row.context}))

    def reset_destination(self, extension_id):
        destination = self.get_destination(extension_id)
        if destination in ('user', 'incall'):
            self.remove_destination_id(extension_id)

    def get_destination(self, extension_id):
        return (self.session
                .query(Extension.type)
                .filter(Extension.id == extension_id)
                .scalar())

    def remove_destination_id(self, extension_id):
            (self.session
             .query(Extension)
             .filter(Extension.id == extension_id)
             .update({'type': 'user', 'typeval': '0'}))

    def adjust_line(self, line_id):
        LineFixes(self.session).fix(line_id)
