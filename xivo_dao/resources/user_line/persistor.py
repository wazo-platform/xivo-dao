# Copyright 2015-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.helpers import errors
from xivo_dao.resources.extension.fixes import ExtensionFixes
from xivo_dao.resources.line.fixes import LineFixes
from xivo_dao.resources.line_extension import dao as line_extension_dao
from xivo_dao.resources.utils.search import CriteriaBuilderMixin


class Persistor(CriteriaBuilderMixin):
    _search_table = UserLine

    def __init__(self, session, resource):
        self.session = session
        self.resource = resource

    def find_query(self, criteria):
        query = self.session.query(UserLine)
        return self.build_criteria(query, criteria)

    def find_by(self, **criteria):
        return self.find_query(criteria).first()

    def get_by(self, **criteria):
        user_line = self.find_by(**criteria)
        if not user_line:
            raise errors.not_found(self.resource, **criteria)
        return user_line

    def find_all_by(self, **criteria):
        return self.find_query(criteria).all()

    def associate_user_line(self, user, line):
        user_line = self.find_by(user_id=user.id, line_id=line.id)
        if user_line:
            return user_line

        main_user_line = self.find_by(main_user=True, line_id=line.id)
        user_main_line = self.find_by(main_line=True, user_id=user.id)

        user_line = UserLine(
            user_id=user.id,
            line_id=line.id,
            main_line=(False if user_main_line else True),
            main_user=(False if main_user_line else True),
        )

        self.session.add(user_line)
        self.session.flush()
        self.fix_associations(user_line)

        return user_line

    def dissociate_user_line(self, user, line):
        user_line = self.find_by(user_id=user.id, line_id=line.id)
        if not user_line:
            return

        self.delete_queue_member(user_line, line)

        if user_line.main_line:
            self._set_oldest_main_line(user)

        self.session.delete(user_line)
        self.session.flush()
        self.fix_associations(user_line)

        return user_line

    def delete_queue_member(self, user_line, line):
        if line.endpoint_sip:
            interface = f'PJSIP/{line.endpoint_sip.name}'
        elif line.endpoint_sccp:
            interface = f'SCCP/{line.endpoint_sccp.name}'
        elif line.endpoint_custom:
            interface = line.endpoint_custom.interface
        else:
            return

        (
            self.session.query(QueueMember)
            .filter(QueueMember.usertype == 'user')
            .filter(QueueMember.userid == user_line.user_id)
            .filter(QueueMember.interface == interface)
            .delete()
        )

    def _set_oldest_main_line(self, user):
        oldest_user_line = (
            self.session.query(UserLine)
            .filter(UserLine.user_id == user.id)
            .filter(UserLine.main_line == False)  # noqa
            .order_by(UserLine.line_id.asc())
            .first()
        )
        if oldest_user_line:
            oldest_user_line.main_line = True
            self.session.add(oldest_user_line)

    def fix_associations(self, user_line):
        line_extension = line_extension_dao.find_by(line_id=user_line.line_id)
        if line_extension:
            ExtensionFixes(self.session).fix_extension(line_extension.extension_id)

        LineFixes(self.session).fix(user_line.line_id)

    def associate_all_lines(self, user, lines):
        # Do this only to execute dissociation's fixes
        for existing_line in user.lines:
            if existing_line not in lines:
                self.dissociate_user_line(user, existing_line)

        user.lines = lines

        for user_line in user.user_lines:
            main_user_line = self.find_by(main_user=True, line_id=user_line.line.id)
            if not main_user_line:
                user_line.main_user = True

        self.session.flush()
        for user_line in user.user_lines:
            self.fix_associations(user_line)

        return user.user_lines
