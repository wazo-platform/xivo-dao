# -*- coding: utf-8 -*-

# XiVO CTI Server
# Copyright (C) 2009-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


class QueueMemberFormatter(object):

    @classmethod
    def format_queuemembers(cls, queuemembers):
        ret = {}
        for queuemember in queuemembers:
            queuemember_formatted = cls._convert_row_to_dict(queuemember)
            key = cls._generate_key(queuemember_formatted)
            ret[key] = queuemember_formatted
        return ret

    @staticmethod
    def _generate_key(queuemember):
        return '%s,%s' % (queuemember['interface'], queuemember['queue_name'])

    @staticmethod
    def _convert_row_to_dict(row):
        return {
            'queue_name': row.queue_name,
            'interface': row.interface,
            'penalty': row.penalty,
            'call_limit': row.call_limit,
            'paused': row.paused,
            'commented': row.commented,
            'usertype': row.usertype,
            'userid': row.userid,
            'channel': row.channel,
            'category': row.category,
            'skills': row.skills,
            'state_interface': row.state_interface
        }

    @classmethod
    def format_queuemember_from_ami_add(cls, ami_event):
        fields_to_extract = ['queue_name',
                             'interface',
                             'membership',
                             'penalty',
                             'status',
                             'paused']
        formatted_queuemembers = cls._extract_ami(fields_to_extract, ami_event)
        return formatted_queuemembers

    @classmethod
    def format_queuemember_from_ami_remove(cls, ami_event):
        fields_to_extract = ['queue_name',
                             'interface']
        formatted_queuemember = cls._extract_ami(fields_to_extract, ami_event)
        return formatted_queuemember

    @classmethod
    def format_queuemember_from_ami_update(cls, ami_event):
        fields_to_extract = ['queue_name',
                             'interface',
                             'membership',
                             'penalty',
                             'status',
                             'paused']
        formatted_queuemember = cls._extract_ami(fields_to_extract, ami_event)
        return formatted_queuemember

    @classmethod
    def format_queuemember_from_ami_pause(cls, ami_event):
        fields_to_extract = ['queue_name',
                             'interface',
                             'paused']
        formatted_queuemember = cls._extract_ami(fields_to_extract, ami_event)
        return formatted_queuemember

    @classmethod
    def _extract_ami(cls, expected_field_list, ami_event):
        ami_map = {
            'queue_name': 'Queue',
            'interface': 'Location',
            'membership': 'Membership',
            'penalty': 'Penalty',
            'status': 'Status',
            'paused': 'Paused'}
        queuemember = {}
        for expected_field in expected_field_list:
            if expected_field in ami_map:
                ami_field = ami_map[expected_field]
                queuemember[expected_field] = ami_event[ami_field]
        key = cls._generate_key(queuemember)
        return {key: queuemember}
