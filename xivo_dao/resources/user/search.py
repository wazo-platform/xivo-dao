# -*- coding: utf-8 -*-

# Copyright 2014-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.sql import and_

from xivo_dao.alchemy.entity import Entity
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.alchemy.extension import Extension
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(table=UserFeatures,
                      columns={'id': UserFeatures.id,
                               'uuid': UserFeatures.uuid,
                               'firstname': UserFeatures.firstname,
                               'lastname': UserFeatures.lastname,
                               'fullname': (UserFeatures.firstname + " " + UserFeatures.lastname),
                               'caller_id': UserFeatures.callerid,
                               'description': UserFeatures.description,
                               'userfield': UserFeatures.userfield,
                               'email': UserFeatures.email,
                               'mobile_phone_number': UserFeatures.mobilephonenumber,
                               'music_on_hold': UserFeatures.musiconhold,
                               'outgoing_caller_id': UserFeatures.outcallerid,
                               'preprocess_subroutine': UserFeatures.preprocess_subroutine,
                               'entity': Entity.name,
                               'voicemail_number': Voicemail.mailbox,
                               'provisioning_code': LineFeatures.provisioning_code,
                               'exten': Extension.exten,
                               'extension': Extension.exten,
                               'context': Extension.context,
                               'username': UserFeatures.loginclient,
                               'enabled': UserFeatures.enabled},
                      search=['fullname',
                              'caller_id',
                              'description',
                              'userfield',
                              'email',
                              'mobile_phone_number',
                              'music_on_hold',
                              'preprocess_subroutine',
                              'outgoing_caller_id',
                              'exten',
                              'username',
                              'provisioning_code'],
                      default_sort='lastname')


class UserSearchSystem(SearchSystem):

    def search_from_query(self, query, parameters):
        query = self._search_on_extension(query)
        return super(UserSearchSystem, self).search_from_query(query, parameters)

    def _search_on_extension(self, query):
        return (query
                .outerjoin(Entity,
                           UserFeatures.entity_id == Entity.id)
                .outerjoin(UserLine,
                           and_(UserLine.user_id == UserFeatures.id,
                                UserLine.main_line == True))  # noqa
                .outerjoin(LineFeatures,
                           and_(LineFeatures.id == UserLine.line_id,
                                LineFeatures.commented == 0))
                .outerjoin(LineExtension,
                           UserLine.line_id == LineExtension.line_id)
                .outerjoin(Extension,
                           and_(LineExtension.extension_id == Extension.id,
                                LineExtension.main_extension == True,  # noqa
                                Extension.commented == 0))
                .outerjoin(Voicemail,
                           and_(UserFeatures.voicemailid == Voicemail.uniqueid,
                                Voicemail.commented == 0)))


user_search = UserSearchSystem(config)
