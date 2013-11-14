# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

import datetime
import logging
import random
import unittest

from mock import patch
from xivo_dao.helpers.db_manager import Base
from sqlalchemy.schema import MetaData
from xivo_dao.helpers import config
from xivo_dao.helpers import db_manager
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.sccpline import SCCPLine as SCCPLineSchema
from xivo_dao.alchemy.sccpdevice import SCCPDevice as SCCPDeviceSchema
from xivo_dao.alchemy.usercustom import UserCustom as UserCustomSchema
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.alchemy.useriax import UserIAX
from xivo_dao.alchemy.dialpattern import DialPattern
from xivo_dao.alchemy.cel import CEL as CELSchema
from xivo_dao.alchemy.sccpgeneralsettings import SCCPGeneralSettings
from xivo_dao.alchemy.phonefunckey import PhoneFunckey
from xivo_dao.alchemy.voicemail import Voicemail as VoicemailSchema
from xivo_dao.alchemy.context import Context
from xivo_dao.alchemy.contextinclude import ContextInclude
from xivo_dao.alchemy.staticvoicemail import StaticVoicemail
from xivo_dao.alchemy.staticsip import StaticSIP
from xivo_dao.alchemy.sipauthentication import SIPAuthentication
from xivo_dao.alchemy.pickup import Pickup
from xivo_dao.alchemy.pickupmember import PickupMember
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.groupfeatures import GroupFeatures
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.staticiax import StaticIAX
from xivo_dao.alchemy.staticmeetme import StaticMeetme
from xivo_dao.alchemy.musiconhold import MusicOnHold
from xivo_dao.alchemy.staticqueue import StaticQueue
from xivo_dao.alchemy.queue import Queue
from xivo_dao.alchemy.queueskillrule import QueueSkillRule
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.queueskill import QueueSkill

logger = logging.getLogger(__name__)


class DAOTestCase(unittest.TestCase):

    @classmethod
    @patch('xivo_dao.helpers.bus_manager.send_bus_command')
    def setUpClass(cls, send_bus_command):
        logger.debug("Connecting to database")
        config.DB_URI = 'postgresql://asterisk:asterisk@localhost/asterisktest'
        config.XIVO_DB_URI = 'postgresql://asterisk:asterisk@localhost/asterisktest'
        db_manager._init()
        cls.session = db_manager.AsteriskSession()
        cls.engine = cls.session.bind
        logger.debug("Connected to database")
        cls.cleanTables()

    @classmethod
    def tearDownClass(cls):
        logger.debug("Closing connection")
        cls.session.close()

    @classmethod
    def cleanTables(cls):
        logger.debug("Cleaning tables")
        cls.session.begin()

        if hasattr(cls, 'tables') and cls.tables:
            engine = cls.engine

            meta = MetaData(engine)
            meta.reflect()
            logger.debug("drop all tables")
            meta.drop_all()

            table_list = [table.__table__ for table in cls.tables]
            logger.debug("create all tables")
            Base.metadata.create_all(engine, table_list)
            engine.dispose()

        cls.session.commit()
        logger.debug("Tables cleaned")

    def empty_tables(self):
        logger.debug("Emptying tables")
        table_names = [table.__tablename__ for table in self.tables]
        self.session.begin()
        self.session.execute("TRUNCATE %s CASCADE;" % ",".join(table_names))
        self.session.commit()
        logger.debug("Tables emptied")

    def add_user_line_with_exten(self, **kwargs):
        kwargs.setdefault('firstname', 'unittest')
        kwargs.setdefault('lastname', 'unittest')
        kwargs.setdefault('callerid', u'"%s %s"' % (kwargs['firstname'], kwargs['lastname']))
        kwargs.setdefault('exten', '%s' % random.randint(1000, 1999))
        kwargs.setdefault('context', 'foocontext')
        kwargs.setdefault('protocol', 'sip')
        kwargs.setdefault('protocolid', int(''.join(random.choice('123456789') for _ in range(3))))
        kwargs.setdefault('name_line', ''.join(random.choice('0123456789ABCDEF') for _ in range(6)))
        kwargs.setdefault('commented_line', 0)
        kwargs.setdefault('device', 1)
        kwargs.setdefault('voicemail_id', None)

        user = self.add_user(firstname=kwargs['firstname'],
                             lastname=kwargs['lastname'],
                             callerid=kwargs['callerid'],
                             voicemailid=kwargs['voicemail_id'])
        line = self.add_line(number=kwargs['exten'],
                             context=kwargs['context'],
                             protocol=kwargs['protocol'],
                             protocolid=kwargs['protocolid'],
                             name=kwargs['name_line'],
                             device=kwargs['device'],
                             commented=kwargs['commented_line'])
        extension = self.add_extension(exten=kwargs['exten'],
                                       context=kwargs['context'],
                                       typeval=user.id)
        user_line = self.add_user_line(line_id=line.id,
                                       user_id=user.id,
                                       extension_id=extension.id)

        user_line.user = user
        user_line.line = line
        user_line.extension = extension

        return user_line

    def add_line(self, **kwargs):
        kwargs.setdefault('name', ''.join(random.choice('0123456789ABCDEF') for _ in range(6)))
        kwargs.setdefault('context', 'foocontext')
        kwargs.setdefault('protocol', 'sip')
        kwargs.setdefault('protocolid', int(''.join(random.choice('123456789') for _ in range(3))))
        kwargs.setdefault('provisioningid', int(''.join(random.choice('123456789') for _ in range(6))))
        kwargs.setdefault('id', self._generate_id())

        line = LineFeatures(**kwargs)
        self.add_me(line)
        return line

    def add_context(self, **kwargs):
        kwargs.setdefault('entity', 'entity_id')
        kwargs.setdefault('name', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))
        kwargs.setdefault('displayname', kwargs['name'].capitalize())
        kwargs.setdefault('description', 'Auto create context')

        context = Context(**kwargs)
        self.add_me(context)
        return context

    def add_context_include(self, **kwargs):
        kwargs.setdefault('context', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))
        kwargs.setdefault('include', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))
        kwargs.setdefault('priority', 0)

        context_include = ContextInclude(**kwargs)
        self.add_me(context_include)
        return context_include

    def add_user_line(self, **kwargs):
        kwargs.setdefault('main_user', True)
        kwargs.setdefault('main_line', True)
        kwargs.setdefault('id', self._generate_id())

        user_line = UserLine(**kwargs)
        self.add_me(user_line)
        return user_line

    def add_extension(self, **kwargs):
        kwargs.setdefault('type', 'user')
        kwargs.setdefault('context', 'default')
        kwargs.setdefault('id', self._generate_id())

        extension = Extension(**kwargs)
        self.add_me(extension)
        return extension

    def add_user(self, **kwargs):
        kwargs.setdefault('id', self._generate_id())
        user = UserFeatures(**kwargs)
        self.add_me(user)
        return user

    def add_agent(self, **kwargs):
        kwargs.setdefault('id', self._generate_id())
        kwargs.setdefault('numgroup', self._generate_id())
        kwargs.setdefault('number', int(''.join(random.choice('123456789') for _ in range(6))))
        kwargs.setdefault('passwd', '')
        kwargs.setdefault('context', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))
        kwargs.setdefault('language', random.choice(['fr_FR', 'en_US']))
        agent = AgentFeatures(**kwargs)
        self.add_me(agent)
        return agent

    def add_group(self, **kwargs):
        kwargs.setdefault('id', self._generate_id())
        kwargs.setdefault('name', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))
        group = GroupFeatures(**kwargs)
        self.add_me(group)
        return group

    def add_queuefeatures(self, **kwargs):
        kwargs.setdefault('id', self._generate_id())
        kwargs.setdefault('name', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))
        kwargs.setdefault('displayname', kwargs['name'].capitalize())
        queuefeatures = QueueFeatures(**kwargs)
        self.add_me(queuefeatures)
        return queuefeatures

    def add_queue(self, **kwargs):
        kwargs.setdefault('name', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))
        kwargs.setdefault('category', random.choice(['group', 'queue']))
        queue = Queue(**kwargs)
        self.add_me(queue)
        return queue

    def add_queue_skill(self, **kwargs):
        kwargs.setdefault('id', self._generate_id())
        kwargs.setdefault('catid', self._generate_id())
        kwargs.setdefault('name', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))
        kwargs.setdefault('description', '')
        queue_skill = QueueSkill(**kwargs)
        self.add_me(queue_skill)
        return queue_skill

    def add_queue_skill_rule(self, **kwargs):
        kwargs.setdefault('id', self._generate_id())
        kwargs.setdefault('name', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))
        kwargs.setdefault('rule', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))
        queue_skill_rule = QueueSkillRule(**kwargs)
        self.add_me(queue_skill_rule)
        return queue_skill_rule

    def add_queue_general_settings(self, **kwargs):
        kwargs.setdefault('id', self._generate_id())
        kwargs.setdefault('cat_metric', 0)
        kwargs.setdefault('var_metric', 0)
        kwargs.setdefault('commented', 0)
        kwargs.setdefault('filename', 'queues.conf')
        kwargs.setdefault('category', 'general')
        kwargs.setdefault('var_name', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))
        kwargs.setdefault('var_val', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))

        static_queue = StaticQueue(**kwargs)
        self.add_me(static_queue)
        return static_queue

    def add_queue_member(self, **kwargs):
        kwargs.setdefault('queue_name', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))
        kwargs.setdefault('interface', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))
        kwargs.setdefault('usertype', random.choice(['user', 'agent']))
        kwargs.setdefault('category', random.choice(['group', 'queue']))
        kwargs.setdefault('channel', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))
        kwargs.setdefault('userid', self._generate_id())

        queue_member = QueueMember(**kwargs)
        self.add_me(queue_member)
        return queue_member

    def add_pickup(self, **kwargs):
        kwargs.setdefault('id', self._generate_id())
        kwargs.setdefault('name', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))

        pickup = Pickup(**kwargs)
        self.add_me(pickup)
        return pickup

    def add_pickup_member(self, **kwargs):
        kwargs.setdefault('pickupid', self._generate_id())
        kwargs.setdefault('category', random.choice(['pickup', 'member']))
        kwargs.setdefault('membertype', random.choice(['group', 'queue', 'user']))
        kwargs.setdefault('memberid', self._generate_id())

        pickup_member = PickupMember(**kwargs)
        self.add_me(pickup_member)
        return pickup_member

    def add_dialpattern(self, **kwargs):
        kwargs.setdefault('id', self._generate_id())
        kwargs.setdefault('type', 'outcall')
        kwargs.setdefault('typeid', self._generate_id())
        kwargs.setdefault('exten', ''.join(random.choice('0123456789_*X.') for _ in range(6)))
        dialpattern = DialPattern(**kwargs)
        self.add_me(dialpattern)
        return dialpattern

    def add_usersip(self, **kwargs):
        kwargs.setdefault('name', ''.join(random.choice('0123456789ABCDEF') for _ in range(6)))
        kwargs.setdefault('context', 'default')
        kwargs.setdefault('type', 'friend')
        kwargs.setdefault('id', self._generate_id())

        usersip = UserSIP(**kwargs)
        self.add_me(usersip)
        return usersip

    def add_useriax(self, **kwargs):
        kwargs.setdefault('id', self._generate_id())
        kwargs.setdefault('name', ''.join(random.choice('0123456789ABCDEF') for _ in range(6)))
        kwargs.setdefault('context', 'default')
        kwargs.setdefault('type', 'friend')

        useriax = UserIAX(**kwargs)
        self.add_me(useriax)
        return useriax

    def add_usercustom(self, **kwargs):
        kwargs.setdefault('id', self._generate_id())
        kwargs.setdefault('interface', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))

        usercustom = UserCustomSchema(**kwargs)
        self.add_me(usercustom)
        return usercustom

    def add_sccpdevice(self, **kwargs):
        kwargs.setdefault('name', 'SEP001122334455')
        kwargs.setdefault('device', 'SEP001122334455')
        kwargs.setdefault('line', '1000')
        kwargs.setdefault('id', self._generate_id())
        kwargs.setdefault('voicemail', '1234')

        sccpdevice = SCCPDeviceSchema(**kwargs)
        self.add_me(sccpdevice)
        return sccpdevice

    def add_sccpline(self, **kwargs):
        kwargs.setdefault('name', '1234')
        kwargs.setdefault('context', 'default')
        kwargs.setdefault('cid_name', 'Tester One')
        kwargs.setdefault('cid_num', '1234')
        kwargs.setdefault('id', self._generate_id())

        sccpline = SCCPLineSchema(**kwargs)
        self.add_me(sccpline)
        return sccpline

    def add_function_key_to_user(self, **kwargs):
        kwargs.setdefault('iduserfeatures', self._generate_id())
        kwargs.setdefault('fknum', '1')
        kwargs.setdefault('exten', ''.join(random.choice('0123456789_*X.') for _ in range(6)))
        kwargs.setdefault('supervision', '0')
        kwargs.setdefault('label', 'toto')
        kwargs.setdefault('typeextenumbersright', 'user')
        kwargs.setdefault('typeextenumbers', None)
        kwargs.setdefault('typevalextenumbers', None)
        kwargs.setdefault('progfunckey', '1')

        phone_func_key = PhoneFunckey(**kwargs)
        self.add_me(phone_func_key)
        return phone_func_key

    def add_sccp_general_settings(self, **kwargs):
        kwargs.setdefault('id', self._generate_id())
        kwargs.setdefault('option_name', 'directmedia')
        kwargs.setdefault('option_value', 'no')

        sccp_general_settings = SCCPGeneralSettings(**kwargs)
        self.add_me(sccp_general_settings)
        return sccp_general_settings

    def add_cel(self, **kwargs):
        kwargs.setdefault('id', self._generate_id())
        kwargs.setdefault('eventtype', 'eventtype')
        kwargs.setdefault('eventtime', datetime.datetime.now())
        kwargs.setdefault('userdeftype', 'userdeftype')
        kwargs.setdefault('cid_name', 'cid_name')
        kwargs.setdefault('cid_num', 'cid_num')
        kwargs.setdefault('cid_ani', 'cid_ani')
        kwargs.setdefault('cid_rdnis', 'cid_rdnis')
        kwargs.setdefault('cid_dnid', 'cid_dnid')
        kwargs.setdefault('exten', 'exten')
        kwargs.setdefault('context', 'context')
        kwargs.setdefault('channame', 'channame')
        kwargs.setdefault('appname', 'appname')
        kwargs.setdefault('appdata', 'appdata')
        kwargs.setdefault('amaflags', 0)
        kwargs.setdefault('accountcode', 'accountcode')
        kwargs.setdefault('peeraccount', 'peeraccount')
        kwargs.setdefault('uniqueid', 'uniqueid')
        kwargs.setdefault('linkedid', 'linkedid')
        kwargs.setdefault('userfield', 'userfield')
        kwargs.setdefault('peer', 'peer')

        cel = CELSchema(**kwargs)
        self.add_me(cel)
        return cel.id

    def add_voicemail(self, **kwargs):
        kwargs.setdefault('fullname', 'Auto Voicemail')
        kwargs.setdefault('mailbox', ''.join(random.choice('0123456789_*X.') for _ in range(6)))
        kwargs.setdefault('context', 'unittest')
        kwargs.setdefault('uniqueid', self._generate_id())

        voicemail = VoicemailSchema(**kwargs)
        self.add_me(voicemail)
        return voicemail

    def link_user_and_voicemail(self, user_row, voicemail_id):
        user_row.voicemailtype = 'asterisk'
        user_row.voicemailid = voicemail_id

        if not user_row.language:
            user_row.language = 'fr_FR'

        self.add_me(user_row)

    def add_musiconhold(self, **kwargs):
        kwargs.setdefault('id', self._generate_id())
        kwargs.setdefault('cat_metric', 0)
        kwargs.setdefault('var_metric', 0)
        kwargs.setdefault('commented', 0)
        kwargs.setdefault('filename', 'musiconhold.conf')
        kwargs.setdefault('category', 'default')
        kwargs.setdefault('var_name', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))
        kwargs.setdefault('var_val', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))

        musiconhold = MusicOnHold(**kwargs)
        self.add_me(musiconhold)
        return musiconhold

    def add_meetme_general_settings(self, **kwargs):
        kwargs.setdefault('id', self._generate_id())
        kwargs.setdefault('cat_metric', 0)
        kwargs.setdefault('var_metric', 0)
        kwargs.setdefault('commented', 0)
        kwargs.setdefault('filename', 'meetme.conf')
        kwargs.setdefault('category', 'general')
        kwargs.setdefault('var_name', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))
        kwargs.setdefault('var_val', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))

        static_meetme = StaticMeetme(**kwargs)
        self.add_me(static_meetme)
        return static_meetme

    def add_voicemail_general_settings(self, **kwargs):
        kwargs.setdefault('id', self._generate_id())
        kwargs.setdefault('cat_metric', 0)
        kwargs.setdefault('var_metric', 0)
        kwargs.setdefault('commented', 0)
        kwargs.setdefault('filename', 'voicemail.conf')
        kwargs.setdefault('category', 'general')
        kwargs.setdefault('var_name', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))
        kwargs.setdefault('var_val', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))

        static_voicemail = StaticVoicemail(**kwargs)
        self.add_me(static_voicemail)
        return static_voicemail

    def add_iax_general_settings(self, **kwargs):
        kwargs.setdefault('id', self._generate_id())
        kwargs.setdefault('cat_metric', 0)
        kwargs.setdefault('var_metric', 0)
        kwargs.setdefault('commented', 0)
        kwargs.setdefault('filename', 'sip.conf')
        kwargs.setdefault('category', 'general')
        kwargs.setdefault('var_name', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))
        kwargs.setdefault('var_val', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))

        static_iax = StaticIAX(**kwargs)
        self.add_me(static_iax)
        return static_iax

    def add_sip_general_settings(self, **kwargs):
        kwargs.setdefault('id', self._generate_id())
        kwargs.setdefault('cat_metric', 0)
        kwargs.setdefault('var_metric', 0)
        kwargs.setdefault('commented', 0)
        kwargs.setdefault('filename', 'sip.conf')
        kwargs.setdefault('category', 'general')
        kwargs.setdefault('var_name', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))
        kwargs.setdefault('var_val', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))

        static_sip = StaticSIP(**kwargs)
        self.add_me(static_sip)
        return static_sip

    def add_sip_authentication(self, **kwargs):
        kwargs.setdefault('id', self._generate_id())
        kwargs.setdefault('usersip_id', self._generate_id())
        kwargs.setdefault('user', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))
        kwargs.setdefault('secretmode', 'md5')
        kwargs.setdefault('secret', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))
        kwargs.setdefault('realm', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))

        sip_authentication = SIPAuthentication(**kwargs)
        self.add_me(sip_authentication)
        return sip_authentication

    def add_me(self, obj):
        self.session.begin()
        try:
            self.session.add(obj)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    def add_me_all(self, obj_list):
        self.session.begin()
        self.session.add_all(obj_list)
        self.session.commit()

    def _generate_id(self):
        return random.randint(1, 1000000)
