# -*- coding: utf-8 -*-

# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall SAS. See the LICENSE file at top of the
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

import datetime


def format_queuemembers(queuemembers):
    ret = {}
    for queuemember in queuemembers:
        queuemember_formatted = _convert_row_to_dict(queuemember)
        key = _generate_key(queuemember_formatted)
        ret[key] = queuemember_formatted
    return ret


def _generate_key(queuemember):
    return '%s,%s' % (queuemember['interface'], queuemember['queue_name'])


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


def format_queuemember_from_ami_add(ami_event):
    fields_to_extract = ['queue_name',
                         'interface',
                         'membership',
                         'penalty',
                         'status',
                         'paused',
                         'lastcall',
                         'callstaken']
    formatted_queuemembers = _extract_ami(fields_to_extract, ami_event)
    return formatted_queuemembers


def format_queuemember_from_ami_remove(ami_event):
    fields_to_extract = ['queue_name',
                         'interface']
    formatted_queuemember = _extract_ami(fields_to_extract, ami_event)
    return formatted_queuemember


def format_queuemember_from_ami_update(ami_event):
    fields_to_extract = ['queue_name',
                         'interface',
                         'membership',
                         'penalty',
                         'status',
                         'paused',
                         'lastcall',
                         'callstaken']
    formatted_queuemember = _extract_ami(fields_to_extract, ami_event)
    return formatted_queuemember


def format_queuemember_from_ami_pause(ami_event):
    fields_to_extract = ['queue_name',
                         'interface',
                         'paused']
    formatted_queuemember = _extract_ami(fields_to_extract, ami_event)
    return formatted_queuemember


def _extract_ami(expected_field_list, ami_event):
    ami_map = {
        'queue_name': 'Queue',
        'interface': 'Location',
        'membership': 'Membership',
        'penalty': 'Penalty',
        'status': 'Status',
        'paused': 'Paused',
        'lastcall': 'LastCall',
        'callstaken': 'CallsTaken',
    }
    queuemember = {}
    for expected_field in expected_field_list:
        if expected_field in ami_map:
            ami_field = ami_map[expected_field]
            queuemember[expected_field] = ami_event[ami_field]
    if 'interface' in expected_field_list:
        member_name = ami_event.get('MemberName')
        if member_name is None:
            member_name = ami_event['Name']
        if member_name.startswith('Agent/'):
            queuemember['interface'] = member_name
    if 'lastcall' in expected_field_list:
        queuemember['lastcall'] = _convert_timestamp_to_date(queuemember['lastcall'])
    key = _generate_key(queuemember)
    return {key: queuemember}


def _convert_timestamp_to_date(timestamp):
    if timestamp == '0':
        return ''
    date = datetime.datetime.fromtimestamp(float(timestamp))
    return date.strftime("%H:%M:%S")
