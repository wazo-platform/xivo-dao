# -*- coding: utf-8 -*-

# Copyright (C) 2007-2016 Avencall
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

from __future__ import unicode_literals

import uuid

from hamcrest import assert_that
from hamcrest import equal_to
from hamcrest import has_property
from hamcrest import has_properties
from hamcrest import is_not
from hamcrest import none
from hamcrest import has_items
from hamcrest import contains
from hamcrest import not_

from xivo_dao.alchemy.entity import Entity
from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.alchemy.schedule import Schedule
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.alchemy.func_key_template import FuncKeyTemplate
from xivo_dao.alchemy.func_key_dest_user import FuncKeyDestUser
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.helpers.exception import NotFoundError, InputError
from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.user.model import UserDirectory, UserSummary
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.resources.func_key.tests.test_helpers import FuncKeyHelper


class TestUser(DAOTestCase, FuncKeyHelper):

    def setUp(self):
        super(TestUser, self).setUp()
        self.setup_funckeys()

    def prepare_user(self, **kwargs):
        template_row = self.add_func_key_template(private=True)
        kwargs.setdefault('func_key_private_template_id', template_row.id)
        user = User(**kwargs)
        self.session.add(user)
        self.session.flush()
        return user


class TestFindByIdUuid(TestUser):

    def test_given_no_user_when_finding_then_returns_none(self):
        assert_that(user_dao.find_by_id_uuid(1), none())

    def test_given_no_user_when_getting_then_returns_none(self):
        self.assertRaises(NotFoundError, user_dao.get_by_id_uuid, 1)

    def test_given_one_user_when_finding_by_its_id_then_returns_the_user(self):
        user_row = self.add_user()

        result = user_dao.find_by_id_uuid(user_row.id)

        assert_that(result.id, equal_to(user_row.id))

    def test_given_one_user_when_finding_by_its_string_id_then_returns_the_user(self):
        user_row = self.add_user()

        result = user_dao.find_by_id_uuid(str(user_row.id))

        assert_that(result.id, equal_to(user_row.id))

    def test_given_one_user_when_finding_by_its_string_uuid_then_returns_the_user(self):
        user_row = self.add_user()

        result = user_dao.find_by_id_uuid(user_row.uuid)

        assert_that(result.id, equal_to(user_row.id))
        assert_that(result.uuid, equal_to(user_row.uuid))

    def test_given_one_user_when_finding_by_its_uuid_then_returns_the_user(self):
        user_uuid = uuid.uuid4()
        user_row = self.add_user(uuid=str(user_uuid))

        result = user_dao.find_by_id_uuid(user_uuid)

        assert_that(result.id, equal_to(user_row.id))
        assert_that(result.uuid, equal_to(user_row.uuid))


class TestFind(TestUser):

    def test_find_no_user(self):
        result = user_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        user_row = self.add_user(firstname='Pâul',
                                 lastname='Rôgers',
                                 callerid='"Côol dude"',
                                 outcallerid='"Côol dude going out"',
                                 loginclient='paulrogers',
                                 passwdclient='paulrogers',
                                 musiconhold='mymusic',
                                 mobilephonenumber='4185551234',
                                 commented=1,
                                 rightcallcode='1234',
                                 userfield='userfield',
                                 timezone='America/Montreal',
                                 language='fr_FR',
                                 description='Really cool dude',
                                 preprocess_subroutine='preprocess_subroutine')

        voicemail_row = self.add_voicemail(mailbox='1234', context='default')
        self.link_user_and_voicemail(user_row, voicemail_row.uniqueid)

        user = user_dao.find(user_row.id)

        assert_that(user.id, equal_to(user.id))
        assert_that(user.lastname, equal_to(user_row.lastname))
        assert_that(user.caller_id, equal_to(user_row.callerid))
        assert_that(user.outgoing_caller_id, equal_to(user_row.outcallerid))
        assert_that(user.username, equal_to(user_row.loginclient))
        assert_that(user.password, equal_to(user_row.passwdclient))
        assert_that(user.music_on_hold, equal_to(user_row.musiconhold))
        assert_that(user.mobile_phone_number, equal_to(user_row.mobilephonenumber))
        assert_that(user.enabled, not_(equal_to(bool(user_row.commented))))
        assert_that(user.call_permission_password, equal_to(user_row.rightcallcode))
        assert_that(user.userfield, equal_to(user_row.userfield))
        assert_that(user.timezone, equal_to(user_row.timezone))
        assert_that(user.language, equal_to(user_row.language))
        assert_that(user.description, equal_to(user_row.description))
        assert_that(user.preprocess_subroutine, equal_to(user_row.preprocess_subroutine))
        assert_that(user.voicemail_id, equal_to(voicemail_row.uniqueid))
        assert_that(user.private_template_id, equal_to(user_row.func_key_private_template_id))

    def test_that_email_address_is_case_insensitive_when_comparing(self):
        user_row = self.add_user(firstname='Pâul',
                                 lastname='Rôgers',
                                 callerid='"Côol dude"',
                                 outcallerid='"Côol dude going out"',
                                 loginclient='paulrogers',
                                 passwdclient='paulrogers',
                                 musiconhold='mymusic',
                                 mobilephonenumber='4185551234',
                                 commented=1,
                                 email='paul.rogers@example.com',
                                 rightcallcode='1234',
                                 userfield='userfield',
                                 timezone='America/Montreal',
                                 language='fr_FR',
                                 description='Really cool dude',
                                 preprocess_subroutine='preprocess_subroutine')

        user = user_dao.find_by(email='Paul.Rogers@Example.COM')

        assert_that(user_row.id, equal_to(user.id))


class TestGet(TestUser):

    def test_get_no_user(self):
        self.assertRaises(NotFoundError, user_dao.get, 42)

    def test_get(self):
        user_row = self.add_user()

        user = user_dao.get(user_row.id)

        assert_that(user.id, equal_to(user.id))


class TestFindBy(TestUser):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, user_dao.find_by, invalid=42)

    def test_find_by_uuid(self):
        user_uuid = str(uuid.uuid4())
        user_row = self.add_user(uuid=user_uuid)

        user = user_dao.find_by(uuid=user_uuid)

        assert_that(user.id, equal_to(user_row.id))
        assert_that(user.uuid, equal_to(user_uuid))

    def test_find_by_template_id(self):
        user_row = self.add_user()

        user = user_dao.find_by(template_id=user_row.func_key_template_id)

        assert_that(user.id, equal_to(user_row.id))
        assert_that(user.func_key_template_id, equal_to(user_row.func_key_template_id))

    def test_find_by_private_template_id(self):
        user_row = self.add_user()

        user = user_dao.find_by(private_template_id=user_row.func_key_private_template_id)

        assert_that(user.id, equal_to(user_row.id))
        assert_that(user.func_key_private_template_id, equal_to(user_row.func_key_private_template_id))

    def test_find_by_fullname(self):
        user_row = self.add_user(firstname='Jôhn', lastname='Smîth')

        user = user_dao.find_by(fullname='Jôhn Smîth')

        assert_that(user.id, equal_to(user_row.id))
        assert_that(user.firstname, equal_to('Jôhn'))
        assert_that(user.lastname, equal_to('Smîth'))

    def test_given_user_does_not_exist_then_returns_null(self):
        user = user_dao.find_by(firstname='42')

        assert_that(user, none())


class TestGetBy(TestUser):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, user_dao.get_by, invalid=42)

    def test_get_by_uuid(self):
        user_uuid = str(uuid.uuid4())
        user_row = self.add_user(uuid=user_uuid)

        user = user_dao.get_by(uuid=user_uuid)

        assert_that(user.id, equal_to(user_row.id))
        assert_that(user.uuid, equal_to(user_uuid))

    def test_get_by_template_id(self):
        user_row = self.add_user()

        user = user_dao.get_by(template_id=user_row.func_key_template_id)

        assert_that(user.id, equal_to(user_row.id))
        assert_that(user.func_key_template_id, equal_to(user_row.func_key_template_id))

    def test_get_by_private_template_id(self):
        user_row = self.add_user()

        user = user_dao.get_by(private_template_id=user_row.func_key_private_template_id)

        assert_that(user.id, equal_to(user_row.id))
        assert_that(user.func_key_private_template_id, equal_to(user_row.func_key_private_template_id))

    def test_get_by_fullname(self):
        user_row = self.add_user(firstname='Jôhn', lastname='Smîth')

        user = user_dao.get_by(fullname='Jôhn Smîth')

        assert_that(user.id, equal_to(user_row.id))
        assert_that(user.firstname, equal_to('Jôhn'))
        assert_that(user.lastname, equal_to('Smîth'))

    def test_given_user_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, user_dao.get_by, firstname='42')


class TestFindAllBy(TestUser):

    def test_find_all_by_no_users(self):
        result = user_dao.find_all_by(firstname='toto')

        assert_that(result, contains())

    def test_find_all_by_renamed_column(self):
        template_row = self.add_func_key_template()
        user1 = self.add_user(func_key_template_id=template_row.id)
        user2 = self.add_user(func_key_template_id=template_row.id)

        users = user_dao.find_all_by(template_id=template_row.id)

        assert_that(users, has_items(has_property('id', user1.id),
                                     has_property('id', user2.id)))

    def test_find_all_by_native_column(self):
        user1 = self.add_user(firstname="Rîchard")
        user2 = self.add_user(firstname="Rîchard")

        users = user_dao.find_all_by(firstname='Rîchard')

        assert_that(users, has_items(has_property('id', user1.id),
                                     has_property('id', user2.id)))


class TestLegacySearch(TestUser):

    def test_given_users_when_using_legacy_search_then_searches_on_fullname(self):
        user1 = self.add_user(firstname="Rîchard", lastname="Làtulippe")
        user2 = self.add_user(firstname="Jôhn", lastname="Smïth")

        total, users = user_dao.legacy_search("rîch")
        assert_that(total, equal_to(1))
        assert_that(users, contains(has_property('id', user1.id)))
        assert_that(users, is_not(contains(has_property('id', user2.id))))


class TestSearch(TestUser):

    def assert_search_returns_result(self, search_result, **parameters):
        result = user_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_given_no_users_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_commented_user_then_returns_one_result(self):
        user = self.prepare_user(firstname='bob')
        expected = SearchResult(1, [user])

        self.assert_search_returns_result(expected)

    def test_given_directory_view_then_returns_one_result(self):
        user = self.prepare_user(firstname='chârles')
        expected = SearchResult(1, [UserDirectory(id=user.id,
                                                  uuid=user.uuid,
                                                  line_id=None,
                                                  agent_id=None,
                                                  firstname='chârles',
                                                  lastname=None,
                                                  email=None,
                                                  mobile_phone_number=None,
                                                  voicemail_number=None,
                                                  exten=None,
                                                  userfield=None,
                                                  description=None,
                                                  context=None)])

        self.assert_search_returns_result(expected, view='directory')

    def test_given_user_without_line_when_using_summary_view_then_returns_summary_result(self):
        user = self.prepare_user(firstname='chârles')
        entity_name = self.session.query(Entity.name).filter_by(id=user.entity_id).scalar()

        expected = SearchResult(1, [UserSummary(id=user.id,
                                                uuid=user.uuid,
                                                firstname='chârles',
                                                lastname=None,
                                                entity=entity_name,
                                                enabled=True,
                                                extension=None,
                                                context=None,
                                                provisioning_code=None,
                                                protocol=None,
                                                )])

        self.assert_search_returns_result(expected, view='summary')

    def test_given_user_with_line_when_using_summary_view_then_returns_summary_result(self):
        user_line = self.add_user_line_with_exten(firstname='dânny',
                                                  lastname='rôgers')
        entity_name = self.session.query(Entity.name).filter_by(id=user_line.user.entity_id).scalar()

        expected = SearchResult(1, [UserSummary(id=user_line.user_id,
                                                uuid=user_line.user.uuid,
                                                firstname='dânny',
                                                lastname='rôgers',
                                                entity=entity_name,
                                                enabled=True,
                                                extension=user_line.extension.exten,
                                                context=user_line.extension.context,
                                                provisioning_code=user_line.linefeatures.provisioning_code,
                                                protocol=user_line.linefeatures.endpoint,
                                                )])

        self.assert_search_returns_result(expected, view='summary')

    def test_given_user_with_line_and_agent_then_returns_one_directory_view_result(self):
        agent_row = self.add_agent()
        voicemail_row = self.add_voicemail(mailbox='2002')
        user_line_row = self.add_user_line_with_exten(firstname='dânny',
                                                      lastname='rôgers',
                                                      agentid=agent_row.id,
                                                      mobilephonenumber='4185551234',
                                                      voicemail_id=voicemail_row.uniqueid,
                                                      userfield='userfield',
                                                      description='desc')

        expected = SearchResult(1, [UserDirectory(id=user_line_row.user_id,
                                                  uuid=user_line_row.user.uuid,
                                                  line_id=user_line_row.line_id,
                                                  agent_id=agent_row.id,
                                                  firstname='dânny',
                                                  lastname='rôgers',
                                                  email=None,
                                                  mobile_phone_number='4185551234',
                                                  voicemail_number='2002',
                                                  exten=user_line_row.extension.exten,
                                                  userfield='userfield',
                                                  description='desc',
                                                  context=user_line_row.extension.context)])

        self.assert_search_returns_result(expected, view='directory')


class TestSearchGivenMultipleUsers(TestSearch):

    def setUp(self):
        super(TestSearch, self).setUp()
        self.user1 = self.prepare_user(firstname='Ashton', lastname='ToujoursFrais', description='resto')
        self.user2 = self.prepare_user(firstname='Beaugarte', lastname='Cougar', description='bar')
        self.user3 = self.prepare_user(firstname='Casa', lastname='Grecque', description='resto')
        self.user4 = self.prepare_user(firstname='Dunkin', lastname='Donuts', description='resto')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.user2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.user1])
        self.assert_search_returns_result(expected_resto, search='ou', description='resto')

        expected_bar = SearchResult(1, [self.user2])
        self.assert_search_returns_result(expected_bar, search='ou', description='bar')

        expected_all_resto = SearchResult(3, [self.user1, self.user3, self.user4])
        self.assert_search_returns_result(expected_all_resto, description='resto', order='firstname')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4, [self.user1, self.user2, self.user3, self.user4])

        self.assert_search_returns_result(expected, order='firstname')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(4, [self.user4, self.user3, self.user2, self.user1])

        self.assert_search_returns_result(expected, order='firstname', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.user2])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_skipping_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.user4, self.user3, self.user1])

        self.assert_search_returns_result(expected, skip=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.user2])

        self.assert_search_returns_result(expected,
                                          search='a',
                                          order='firstname',
                                          direction='desc',
                                          skip=1,
                                          limit=1)


class TestCreate(TestUser):

    def setUp(self):
        super(TestCreate, self).setUp()
        self.entity = self.add_entity()

    def assert_dial_action_created(self, user, event):
        dialaction = (self.session.query(Dialaction)
                      .filter_by(event=event,
                                 category='user',
                                 categoryval=str(user.id),
                                 action='none',
                                 linked=1)
                      .first())

        assert_that(dialaction, is_not(none()))

    def test_given_user_created_then_diactions_also_created(self):
        user = User(firstname="dialactions")
        created_user = user_dao.create(user)

        self.assert_dial_action_created(created_user, 'noanswer')
        self.assert_dial_action_created(created_user, 'busy')
        self.assert_dial_action_created(created_user, 'congestion')
        self.assert_dial_action_created(created_user, 'chanunavail')

    def test_create_minimal_fields(self):
        user = User(firstname='Jôhn')
        created_user = user_dao.create(user)

        row = self.session.query(User).first()

        assert_that(created_user, has_properties(id=row.id,
                                                 uuid=row.uuid,
                                                 firstname="Jôhn",
                                                 lastname=none(),
                                                 timezone=none(),
                                                 language=none(),
                                                 description=none(),
                                                 outgoing_caller_id=none(),
                                                 mobile_phone_number=none(),
                                                 call_permission_password=none(),
                                                 enabled=True,
                                                 caller_id='"Jôhn"',
                                                 music_on_hold=none(),
                                                 username=none(),
                                                 password=none(),
                                                 preprocess_subroutine=none(),
                                                 userfield=none(),
                                                 voicemail_id=none(),
                                                 call_transfer_enabled=True,
                                                 dnd_enabled=False,
                                                 incallfilter_enabled=False,
                                                 supervision_enabled=True,
                                                 call_record_enabled=False,
                                                 online_call_record_enabled=False,
                                                 busy_enabled=False,
                                                 busy_destination=None,
                                                 noanswer_enabled=False,
                                                 noanswer_destination=None,
                                                 unconditional_enabled=False,
                                                 unconditional_destination=None,
                                                 simultaneous_calls=5,
                                                 ring_seconds=30))

        assert_that(row, has_properties(id=is_not(none()),
                                        uuid=is_not(none()),
                                        entityid=self.entity.id,
                                        callerid='"Jôhn"',
                                        outcallerid='',
                                        mobilephonenumber='',
                                        rightcallcode=none(),
                                        commented=0,
                                        loginclient='',
                                        passwdclient='',
                                        musiconhold='',
                                        voicemailid=none(),
                                        enablehint=1,
                                        enablexfer=1,
                                        incallfilter=0,
                                        enablednd=0,
                                        enableonlinerec=0,
                                        callrecord=0,
                                        enablebusy=0,
                                        destbusy='',
                                        enablerna=0,
                                        destrna='',
                                        enableunc=0,
                                        destunc='',
                                        func_key_private_template_id=is_not(none())
                                        ))

    def test_create_with_all_fields(self):
        voicemail = self.add_voicemail()
        user = User(firstname='Jôhn',
                    lastname='Smîth',
                    timezone='America/Montreal',
                    language='en_US',
                    description='description',
                    caller_id='"fîrstname lâstname" <1000>',
                    outgoing_caller_id='ôutgoing_caller_id',
                    mobile_phone_number='1234567890',
                    call_permission_password='1234',
                    enabled=False,
                    username='username',
                    password='password',
                    music_on_hold='music_on_hold',
                    preprocess_subroutine='preprocess_subroutine',
                    voicemail_id=voicemail.id,
                    userfield='userfield',
                    call_transfer_enabled=False,
                    dnd_enabled=True,
                    incallfilter_enabled=True,
                    supervision_enabled=False,
                    call_record_enabled=True,
                    online_call_record_enabled=True,
                    busy_enabled=True,
                    busy_destination='123',
                    noanswer_enabled=True,
                    noanswer_destination='456',
                    unconditional_enabled=True,
                    unconditional_destination='789',
                    ring_seconds=60,
                    simultaneous_calls=10)

        created_user = user_dao.create(user)

        row = self.session.query(User).first()

        assert_that(created_user, has_properties(id=row.id,
                                                 uuid=row.uuid,
                                                 entity_id=self.entity.id,
                                                 firstname="Jôhn",
                                                 lastname='Smîth',
                                                 timezone='America/Montreal',
                                                 language='en_US',
                                                 description='description',
                                                 caller_id='"fîrstname lâstname" <1000>',
                                                 outgoing_caller_id='ôutgoing_caller_id',
                                                 mobile_phone_number='1234567890',
                                                 call_permission_password='1234',
                                                 enabled=False,
                                                 username='username',
                                                 password='password',
                                                 music_on_hold='music_on_hold',
                                                 preprocess_subroutine='preprocess_subroutine',
                                                 voicemail_id=voicemail.id,
                                                 call_transfer_enabled=False,
                                                 dnd_enabled=True,
                                                 incallfilter_enabled=True,
                                                 supervision_enabled=False,
                                                 call_record_enabled=True,
                                                 online_call_record_enabled=True,
                                                 busy_enabled=True,
                                                 busy_destination='123',
                                                 noanswer_enabled=True,
                                                 noanswer_destination='456',
                                                 unconditional_enabled=True,
                                                 unconditional_destination='789',
                                                 ring_seconds=60,
                                                 simultaneous_calls=10,
                                                 userfield='userfield'))

        assert_that(row, has_properties(callerid='"fîrstname lâstname" <1000>',
                                        outcallerid='ôutgoing_caller_id',
                                        mobilephonenumber='1234567890',
                                        rightcallcode='1234',
                                        commented=1,
                                        loginclient='username',
                                        passwdclient='password',
                                        voicemailid=voicemail.id,
                                        enablehint=0,
                                        enablexfer=0,
                                        incallfilter=1,
                                        enablednd=1,
                                        enableonlinerec=1,
                                        callrecord=1,
                                        enablebusy=1,
                                        destbusy='123',
                                        enablerna=1,
                                        destrna='456',
                                        enableunc=1,
                                        destunc='789',
                                        musiconhold='music_on_hold'))

    def test_that_the_user_uuid_is_unique(self):
        shared_uuid = str(uuid.uuid4())
        self.prepare_user(firstname='Alice', uuid=shared_uuid)

        self.assertRaises(Exception, user_dao.create, User(firstname='Jôhn', uuid=shared_uuid))


class TestEdit(TestUser):

    def test_edit_all_fields(self):
        old_voicemail = self.add_voicemail()
        new_voicemail = self.add_voicemail()
        user = user_dao.create(User(firstname='Pâul',
                                    lastname='Rôgers',
                                    caller_id='"Côol dude"',
                                    outgoing_caller_id='"Côol dude going out"',
                                    username='paulrogers',
                                    password='paulrogers',
                                    music_on_hold='mymusic',
                                    mobile_phone_number='4185551234',
                                    call_permission_password='5678',
                                    enabled=True,
                                    userfield='userfield',
                                    timezone='America/Montreal',
                                    language='fr_FR',
                                    voicemail_id=old_voicemail.id,
                                    description='Really cool dude'))

        user = user_dao.get(user.id)
        user.firstname = 'firstname'
        user.lastname = 'lastname'
        user.timezone = 'America/Montreal'
        user.language = 'en_US'
        user.description = 'description'
        user.caller_id = '"John Sparrow"'
        user.outgoing_caller_id = 'outgoing_caller_id'
        user.mobile_phone_number = '1234567890'
        user.call_permission_password = '1234'
        user.enabled = False
        user.username = 'username'
        user.password = 'password'
        user.music_on_hold = 'music_on_hold'
        user.preprocess_subroutine = 'preprocess_subroutine'
        user.userfield = 'userfield'
        user.voicemail_id = new_voicemail.id
        user.call_transfer_enabled = False
        user.dnd_enabled = True
        user.incallfilter_enabled = True
        user.supervision_enabled = False
        user.call_record_enabled = True
        user.online_call_record_enabled = True
        user.busy_enabled = True
        user.busy_destination = '123'
        user.noanswer_enabled = True
        user.noanswer_destination = '456'
        user.unconditional_enabled = True
        user.unconditional_destination = '789'
        user.ring_seconds = 60
        user.simultaneous_calls = 5

        user_dao.edit(user)

        row = self.session.query(User).first()

        assert_that(row, has_properties(firstname='firstname',
                                        lastname='lastname',
                                        timezone='America/Montreal',
                                        language='en_US',
                                        description='description',
                                        caller_id='"John Sparrow"',
                                        outgoing_caller_id='outgoing_caller_id',
                                        mobile_phone_number='1234567890',
                                        call_permission_password='1234',
                                        enabled=False,
                                        username='username',
                                        password='password',
                                        music_on_hold='music_on_hold',
                                        preprocess_subroutine='preprocess_subroutine',
                                        voicemail_id=new_voicemail.id,
                                        call_transfer_enabled=False,
                                        dnd_enabled=True,
                                        incallfilter_enabled=True,
                                        supervision_enabled=False,
                                        call_record_enabled=True,
                                        online_call_record_enabled=True,
                                        busy_enabled=True,
                                        busy_destination='123',
                                        noanswer_enabled=True,
                                        noanswer_destination='456',
                                        unconditional_enabled=True,
                                        unconditional_destination='789',
                                        ring_seconds=60,
                                        simultaneous_calls=5,
                                        userfield='userfield'))

    def test_edit_set_fields_to_null(self):
        voicemail = self.add_voicemail()
        user = user_dao.create(User(firstname='Pâul',
                                    lastname='Rôgers',
                                    caller_id='"Côol dude"',
                                    outgoing_caller_id='"Côol dude going out"',
                                    username='paulrogers',
                                    password='paulrogers',
                                    music_on_hold='mymusic',
                                    mobile_phone_number='4185551234',
                                    call_permission_password='5678',
                                    userfield='userfield',
                                    timezone='America/Montreal',
                                    language='fr_FR',
                                    voicemail_id=voicemail.id,
                                    description='Really cool dude'))

        user = user_dao.get(user.id)
        user.lastname = None
        user.outgoing_caller_id = None
        user.username = None
        user.password = None
        user.music_on_hold = None
        user.mobile_phone_number = None
        user.call_permission_password = None
        user.userfield = None
        user.timezone = None
        user.language = None
        user.description = None
        user.voicemail_id = None

        user_dao.edit(user)

        row = self.session.query(User).first()

        assert_that(row, has_properties(id=user.id,
                                        uuid=user.uuid,
                                        firstname="Pâul",
                                        lastname=none(),
                                        timezone=none(),
                                        language=none(),
                                        description=none(),
                                        outcallerid='',
                                        mobilephonenumber='',
                                        rightcallcode=none(),
                                        musiconhold='',
                                        loginclient='',
                                        passwdclient='',
                                        preprocess_subroutine=none(),
                                        voicemailid=none(),
                                        userfield=none()))

    def test_edit_caller_id_with_number(self):
        caller_id = '<1000>'
        user = user_dao.create(User(firstname='Pâul'))

        user = user_dao.get(user.id)
        user.caller_id = caller_id

        user_dao.edit(user)

        row = self.session.query(User).first()

        assert_that(row.id, equal_to(user.id))
        assert_that(row.callerid, equal_to(caller_id))


class TestDelete(TestUser):

    def test_delete(self):
        user = user_dao.create(User(firstname='Delete'))
        user = user_dao.get(user.id)

        user_dao.delete(user)

        row = self.session.query(User).first()
        assert_that(row, none())

    def test_delete_references_to_other_tables(self):
        user = user_dao.create(User(firstname='Delete'))
        self.add_queue_member(usertype='user', userid=user.id)
        self.add_right_call_member(type='user', typeval=str(user.id))
        self.add_schedule_path(path='user', pathid=user.id)
        call_filter = self.add_bsfilter()
        self.add_filter_member(call_filter.id, user.id)

        user_dao.delete(user)

        assert_that(self.session.query(QueueMember).first(), none())
        assert_that(self.session.query(RightCallMember).first(), none())
        assert_that(self.session.query(Dialaction).first(), none())
        assert_that(self.session.query(SchedulePath).first(), none())
        assert_that(self.session.query(Callfiltermember).first(), none())
        assert_that(self.session.query(FuncKeyDestUser).first(), none())
        assert_that(self.session.query(FuncKey).first(), none())
        assert_that(self.session.query(FuncKeyTemplate).first(), none())

    def add_right_call_member(self, **kwargs):
        member = RightCallMember(**kwargs)
        self.session.add(member)
        self.session.flush()
        return member

    def add_schedule_path(self, **kwargs):
        kwargs['schedule'] = Schedule()
        kwargs.setdefault('order', 1)
        schedule_path = SchedulePath(**kwargs)
        self.session.add(schedule_path)
        self.session.flush()
        return schedule_path
