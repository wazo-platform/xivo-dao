# -*- coding: utf-8 -*-

# Copyright (C) 2012-2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo_dao.alchemy.phonebook import Phonebook
from xivo_dao.alchemy.phonebookaddress import PhonebookAddress
from xivo_dao.alchemy.phonebooknumber import PhonebookNumber
from xivo_dao.helpers.db_manager import daosession


@daosession
def get(session, phonebook_id):
    return session.query(Phonebook).filter(Phonebook.id == phonebook_id).first()


@daosession
def get_phonebookaddress(session, phonebook_id):
    return session.query(PhonebookAddress).filter(PhonebookAddress.phonebookid == phonebook_id).all()


@daosession
def get_phonebooknumber(session, phonebook_id):
    return session.query(PhonebookNumber).filter(PhonebookNumber.phonebookid == phonebook_id).all()


@daosession
def all_join_elements(session):
    res = []
    phonebooks = session.query(Phonebook).all()
    for phonebook in phonebooks:
        phonebookaddress = get_phonebookaddress(phonebook.id)
        phonebooknumber = get_phonebooknumber(phonebook.id)
        res.append((phonebook, phonebookaddress, phonebooknumber))
    return res
