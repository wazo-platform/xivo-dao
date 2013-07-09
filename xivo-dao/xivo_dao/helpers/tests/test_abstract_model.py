# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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

import unittest

from hamcrest import assert_that
from hamcrest.core import equal_to
from mock import Mock
from xivo_dao.data_handler.exception import InvalidParametersError
from xivo_dao.data_handler.user.model import User
from xivo_dao.data_handler.line.model import Line
from xivo_dao.data_handler.voicemail.model import Voicemail


class TestModelsAbstract(unittest.TestCase):

    def test_instance_of_new_class(self):
        firstname = 'toto'
        lastname = 'kiki'
        language = 'fr_FR'
        user = User(firstname=firstname,
                    lastname=lastname,
                    language=language)

        assert_that(user.firstname, equal_to(firstname))
        assert_that(user.lastname, equal_to(lastname))
        assert_that(user.language, equal_to(language))

    def test_equal_type_mismatch(self):
        line_1 = Line(
            name='test',
        )

        self.assertRaises(TypeError, lambda: line_1 == 'Not a line')

    def test_equal_same(self):
        name = 'samename'
        line_1 = Line(name=name)
        line_2 = Line(name=name)

        assert_that(line_1, equal_to(line_2))

    def test_equal(self):
        user_1 = Mock()
        user_2 = Mock()
        voicemail_1 = Voicemail(
            name='abc def',
            number='42',
            context='context 42',
            id=42,
            user=user_1
        )

        voicemail_2 = Voicemail(
            name='abc defg',
            number='43',
            context='context 43',
            id=43,
            user=user_2
        )

        voicemail_clone_1 = Voicemail(
            name='abc def',
            number='42',
            context='context 42',
            id=42,
            user=user_1
        )

        self.assertRaises(TypeError, lambda: voicemail_1 == 12)
        self.assertNotEquals(voicemail_1, Voicemail())
        self.assertEquals(voicemail_1, voicemail_1)
        self.assertNotEquals(voicemail_1, voicemail_2)
        self.assertEquals(voicemail_1, voicemail_clone_1)

    def test_from_data_source(self):
        properties = Mock()
        properties.id = user_id = 42
        properties.firstname = firstname = 'Moi'
        properties.lastname = lastname = 'Lastname'
        properties.callerid = callerid = '"Moi Lastnane" <123>'
        properties.outcallerid = outcallerid = 'default'
        properties.loginclient = username = 'username'
        properties.passwdclient = password = 'password'
        properties.mobilephonenumber = mobilephonenumber = '12345678'
        properties.language = language = 'fr_FR'
        properties.timezone = timezone = 'America/Montreal'
        properties.userfield = userfield = 'cp123yyx'

        user = User.from_data_source(properties)

        assert_that(user.id, equal_to(user_id))
        assert_that(user.firstname, equal_to(firstname))
        assert_that(user.lastname, equal_to(lastname))
        assert_that(user.callerid, equal_to(callerid))
        assert_that(user.username, equal_to(username))
        assert_that(user.password, equal_to(password))
        assert_that(user.outcallerid, equal_to(outcallerid))
        assert_that(user.mobilephonenumber, equal_to(mobilephonenumber))
        assert_that(user.language, equal_to(language))
        assert_that(user.timezone, equal_to(timezone))
        assert_that(user.userfield, equal_to(userfield))

    def test_to_data_source(self):
        user_id = 56984
        firstname = 'toto'
        lastname = 'kiki'
        language = 'fr_FR'

        user = User(id=user_id,
                    firstname=firstname,
                    lastname=lastname,
                    language=language)

        assert_that(user.id, equal_to(user_id))
        assert_that(user.firstname, equal_to(firstname))
        assert_that(user.lastname, equal_to(lastname))
        assert_that(user.language, equal_to(language))

    def test_from_user_data(self):
        voicemail_id = 1
        name = 'voicemail name'
        number = '42'
        context = 'default'
        properties = {
            'id': voicemail_id,
            'name': name,
            'number': number,
            'context': context,
        }

        voicemail = Voicemail.from_user_data(properties)

        self.assertEquals(voicemail_id, voicemail.id)
        self.assertEquals(name, voicemail.name)
        self.assertEquals(number, voicemail.number)
        self.assertEquals(context, voicemail.context)

    def test_update_from_data(self):
        expected_lastname = 'Toi'
        user = User()
        user.id = 42
        user.firstname = 'Moi'
        user.lastname = 'Lastname'

        data_update = {
            'lastname': expected_lastname
        }

        user.update_from_data(data_update)

        assert_that(user.lastname, equal_to(expected_lastname))

    def test_update_from_data_invalid_properties(self):
        user = User()

        data_update = {
            'toto': 'tata'
        }

        self.assertRaises(InvalidParametersError, user.update_from_data, data_update)
