# -*- coding: utf-8 -*-
#
# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the source tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.phonebook import Phonebook
from xivo_dao.alchemy.phonebookaddress import PhonebookAddress
from xivo_dao.alchemy.phonebooknumber import PhonebookNumber

_DB_NAME = 'asterisk'


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def get(phonebook_id):
    return _session().query(Phonebook).filter(Phonebook.id == phonebook_id).first()


def all():
    return (_session().query(Phonebook, PhonebookAddress, PhonebookNumber)
            .join((PhonebookAddress, Phonebook.id == PhonebookAddress.phonebookid))
            .outerjoin((PhonebookNumber, Phonebook.id == PhonebookNumber.phonebookid))
            .all())
