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
from xivo_dao.models.user import User


class TestUser(unittest.TestCase):

    def test_from_data_source(self):
        properties = Mock()
        properties.id = user_id = 42
        properties.firstname = firstname = 'Moi'
        properties.lastname = lastname = 'Lastname'
        properties.callerid = callerid = '"Moi Lastnane" <123>'
        properties.ringseconds = ringseconds = 30
        properties.simultcalls = simultcalls = 5
        properties.enablevoicemail = enablevoicemail = 0
        properties.voicemailid = voicemailid = None
        properties.enablexfer = enablexfer = 1
        properties.enableautomon = enableautomon = 0
        properties.callrecord = callrecord = 0
        properties.incallfilter = incallfilter = 1
        properties.enablednd = enablednd = 1
        properties.enableunc = enableunc = 0
        properties.destunc = destunc = ''
        properties.enablerna = enablerna = 0
        properties.destrna = destrna = ''
        properties.enablebusy = enablebusy = 0
        properties.destbusy = destbusy = ''
        properties.musiconhold = musiconhold = 'default'
        properties.outcallerid = outcallerid = 'default'
        properties.preprocess_subroutine = preprocess_subroutine = ''
        properties.mobilephonenumber = mobilephonenumber = '12345678'
        properties.bsfilter = bsfilter = 'no'
        properties.language = language = 'fr_FR'
        properties.userfield = userfield = 'cp123yyx'

        user = User.from_data_source(properties)

        assert_that(user.id, equal_to(user_id))
        assert_that(user.firstname, equal_to(firstname))
        assert_that(user.lastname, equal_to(lastname))
        assert_that(user.callerid, equal_to(callerid))
        assert_that(user.ringseconds, equal_to(ringseconds))
        assert_that(user.simultcalls, equal_to(simultcalls))
        assert_that(user.enablevoicemail, equal_to(enablevoicemail))
        assert_that(user.voicemailid, equal_to(voicemailid))
        assert_that(user.enablexfer, equal_to(enablexfer))
        assert_that(user.enableautomon, equal_to(enableautomon))
        assert_that(user.callrecord, equal_to(callrecord))
        assert_that(user.incallfilter, equal_to(incallfilter))
        assert_that(user.enablednd, equal_to(enablednd))
        assert_that(user.enableunc, equal_to(enableunc))
        assert_that(user.destunc, equal_to(destunc))
        assert_that(user.enablerna, equal_to(enablerna))
        assert_that(user.destrna, equal_to(destrna))
        assert_that(user.enablebusy, equal_to(enablebusy))
        assert_that(user.destbusy, equal_to(destbusy))
        assert_that(user.musiconhold, equal_to(musiconhold))
        assert_that(user.outcallerid, equal_to(outcallerid))
        assert_that(user.preprocess_subroutine, equal_to(preprocess_subroutine))
        assert_that(user.mobilephonenumber, equal_to(mobilephonenumber))
        assert_that(user.bsfilter, equal_to(bsfilter))
        assert_that(user.language, equal_to(language))
        assert_that(user.userfield, equal_to(userfield))
