# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
import re

from sqlalchemy import text
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import column_property, relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.schema import (
    Column,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    PrimaryKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.sql import cast, func, not_
from sqlalchemy.types import Boolean, DateTime, Integer, String, Text

from xivo_dao.helpers.db_manager import Base
from xivo_dao.helpers.uuid import new_uuid

from . import enum
from .func_key_template import FuncKeyTemplate
from .queuemember import QueueMember
from .schedulepath import SchedulePath
from .user_line import UserLine


class EmailComparator(ColumnProperty.Comparator):
    def __eq__(self, other):
        return func.lower(self.__clause_element__()) == func.lower(other)


caller_id_regex = re.compile(
    r'''
    "                      #name start
    (?P<name>[^"]+)        #inside ""
    "                      #name end
    \s*                    #space between name and number
    (
    <                      #number start
    (?P<num>\+?[\dA-Z]+)   #inside <>
    >                      #number end
    )?                     #number is optional
    ''',
    re.VERBOSE,
)


def ordering_main_line(index, collection):
    return True if index == 0 else False


class UserFeatures(Base):
    __tablename__ = 'userfeatures'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        ForeignKeyConstraint(
            ('voicemailid',),
            ('voicemail.uniqueid',),
        ),
        ForeignKeyConstraint(
            ('tenant_uuid',),
            ('tenant.uuid',),
            ondelete='CASCADE',
        ),
        UniqueConstraint('func_key_private_template_id'),
        UniqueConstraint('uuid', name='userfeatures_uuid'),
        UniqueConstraint('email', name='userfeatures_email'),
        Index('userfeatures__idx__agentid', 'agentid'),
        Index('userfeatures__idx__firstname', 'firstname'),
        Index('userfeatures__idx__lastname', 'lastname'),
        Index('userfeatures__idx__loginclient', 'loginclient'),
        Index('userfeatures__idx__musiconhold', 'musiconhold'),
        Index('userfeatures__idx__uuid', 'uuid'),
        Index('userfeatures__idx__tenant_uuid', 'tenant_uuid'),
        Index('userfeatures__idx__voicemailid', 'voicemailid'),
        Index('userfeatures__idx__func_key_template_id', 'func_key_template_id'),
        Index(
            'userfeatures__idx__func_key_private_template_id',
            'func_key_private_template_id',
        ),
    )

    id = Column(Integer, nullable=False)
    uuid = Column(String(38), nullable=False, default=new_uuid)
    firstname = Column(String(128), nullable=False, server_default='')
    email = column_property(Column(String(254)), comparator_factory=EmailComparator)
    voicemailid = Column(Integer)
    agentid = Column(Integer)
    pictureid = Column(Integer)
    tenant_uuid = Column(String(36), nullable=False)
    callerid = Column(String(160))
    ringseconds = Column(Integer, nullable=False, server_default='30')
    simultcalls = Column(Integer, nullable=False, server_default='5')
    enableclient = Column(Integer, nullable=False, server_default='0')
    loginclient = Column(String(254), nullable=False, server_default='')
    passwdclient = Column(String(64), nullable=False, server_default='')
    enablehint = Column(Integer, nullable=False, server_default='1')
    enablevoicemail = Column(Integer, nullable=False, server_default='0')
    enablexfer = Column(Integer, nullable=False, server_default='0')
    dtmf_hangup = Column(Integer, nullable=False, server_default='0')
    enableonlinerec = Column(Integer, nullable=False, server_default='0')
    call_record_outgoing_external_enabled = Column(
        Boolean, nullable=False, server_default='false'
    )
    call_record_outgoing_internal_enabled = Column(
        Boolean, nullable=False, server_default='false'
    )
    call_record_incoming_external_enabled = Column(
        Boolean, nullable=False, server_default='false'
    )
    call_record_incoming_internal_enabled = Column(
        Boolean, nullable=False, server_default='false'
    )
    incallfilter = Column(Integer, nullable=False, server_default='0')
    enablednd = Column(Integer, nullable=False, server_default='0')
    enableunc = Column(Integer, nullable=False, server_default='0')
    destunc = Column(String(128), nullable=False, server_default='')
    enablerna = Column(Integer, nullable=False, server_default='0')
    destrna = Column(String(128), nullable=False, server_default='')
    enablebusy = Column(Integer, nullable=False, server_default='0')
    destbusy = Column(String(128), nullable=False, server_default='')
    musiconhold = Column(String(128), nullable=False, server_default='')
    outcallerid = Column(String(80), nullable=False, server_default='')
    mobilephonenumber = Column(String(128), nullable=False, server_default='')
    bsfilter = Column(enum.generic_bsfilter, nullable=False, server_default='no')
    preprocess_subroutine = Column(String(79))
    timezone = Column(String(128))
    language = Column(String(20))
    ringintern = Column(String(64))
    ringextern = Column(String(64))
    ringgroup = Column(String(64))
    ringforward = Column(String(64))
    rightcallcode = Column(String(16))
    commented = Column(Integer, nullable=False, server_default='0')
    func_key_template_id = Column(
        Integer, ForeignKey('func_key_template.id', ondelete="SET NULL")
    )
    func_key_private_template_id = Column(
        Integer, ForeignKey('func_key_template.id'), nullable=False
    )
    subscription_type = Column(Integer, nullable=False, server_default='0')
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        server_default=text("(now() at time zone 'utc')"),
    )

    webi_lastname = Column('lastname', String(128), nullable=False, server_default='')
    webi_userfield = Column('userfield', String(128), nullable=False, server_default='')
    webi_description = Column('description', Text, nullable=False, default='')

    func_key_template = relationship(FuncKeyTemplate, foreign_keys=func_key_template_id)
    func_key_template_private = relationship(
        FuncKeyTemplate, foreign_keys=func_key_private_template_id
    )

    main_line_rel = relationship(
        "UserLine",
        primaryjoin="""and_(
            UserFeatures.id == UserLine.user_id,
            UserLine.main_line == True
        )""",
        viewonly=True,
    )
    agent = relationship(
        "AgentFeatures",
        primaryjoin="AgentFeatures.id == UserFeatures.agentid",
        foreign_keys='UserFeatures.agentid',
        viewonly=True,
    )

    voicemail = relationship("Voicemail", back_populates="users")

    user_lines = relationship(
        'UserLine',
        order_by='desc(UserLine.main_line)',
        collection_class=ordering_list('main_line', ordering_func=ordering_main_line),
        cascade='all, delete-orphan',
        back_populates='user',
    )
    lines = association_proxy(
        'user_lines',
        'line',
        creator=lambda _line: UserLine(line=_line, main_user=False),
    )

    incall_dialactions = relationship(
        'Dialaction',
        primaryjoin="""and_(
            Dialaction.category == 'incall',
            Dialaction.action == 'user',
            Dialaction.actionarg1 == cast(UserFeatures.id, String)
        )""",
        foreign_keys='Dialaction.actionarg1',
        viewonly=True,
    )
    incalls = association_proxy('incall_dialactions', 'incall')

    user_dialactions = relationship(
        'Dialaction',
        primaryjoin="""and_(
            Dialaction.category == 'user',
            Dialaction.categoryval == cast(UserFeatures.id, String)
        )""",
        cascade='all, delete-orphan',
        collection_class=attribute_mapped_collection('event'),
        foreign_keys='Dialaction.categoryval',
        overlaps=(
            'callfilter_dialactions,'
            'dialaction,'
            'dialactions,'
            'group_dialactions,'
            'ivr_choice,'
            'queue_dialactions,'
            'switchboard_dialactions,'
        ),
    )

    group_members = relationship(
        'QueueMember',
        primaryjoin="""and_(
            QueueMember.category == 'group',
            QueueMember.usertype == 'user',
            QueueMember.userid == UserFeatures.id
        )""",
        foreign_keys='QueueMember.userid',
        cascade='all, delete-orphan',
        overlaps='queue_members,queue_queue_members,user',
    )
    groups = association_proxy(
        'group_members',
        'group',
        creator=lambda _group: QueueMember(
            category='group', usertype='user', group=_group
        ),
    )

    queue_members = relationship(
        'QueueMember',
        primaryjoin="""and_(
            QueueMember.category == 'queue',
            QueueMember.usertype == 'user',
            QueueMember.userid == UserFeatures.id
        )""",
        foreign_keys='QueueMember.userid',
        cascade='all, delete-orphan',
        overlaps='group_members,queue_queue_members,user',
    )
    queues = association_proxy('queue_members', 'queue')

    paging_users = relationship(
        'PagingUser',
        cascade='all, delete-orphan',
        back_populates='user',
    )

    switchboard_member_users = relationship(
        'SwitchboardMemberUser',
        cascade='all, delete-orphan',
        back_populates='user',
    )
    switchboards = association_proxy('switchboard_member_users', 'switchboard')

    _dialaction_actions = relationship(
        'Dialaction',
        primaryjoin="""and_(
            Dialaction.action == 'user',
            Dialaction.actionarg1 == cast(UserFeatures.id, String),
        )""",
        foreign_keys='Dialaction.actionarg1',
        cascade='all, delete-orphan',
        overlaps='_dialaction_actions',
    )

    schedule_paths = relationship(
        'SchedulePath',
        primaryjoin="""and_(
            SchedulePath.path == 'user',
            SchedulePath.pathid == UserFeatures.id
        )""",
        foreign_keys='SchedulePath.pathid',
        cascade='all, delete-orphan',
        overlaps='schedule_paths',
    )
    schedules = association_proxy(
        'schedule_paths',
        'schedule',
        creator=lambda _schedule: SchedulePath(
            path='user', schedule_id=_schedule.id, schedule=_schedule
        ),
    )

    call_filter_recipients = relationship(
        'Callfiltermember',
        primaryjoin="""and_(
            Callfiltermember.type == 'user',
            Callfiltermember.bstype == 'boss',
            Callfiltermember.typeval == cast(UserFeatures.id, String)
        )""",
        foreign_keys='Callfiltermember.typeval',
        cascade='delete, delete-orphan',
        overlaps='call_filter_surrogates,user',
    )
    call_filter_surrogates = relationship(
        'Callfiltermember',
        primaryjoin="""and_(
            Callfiltermember.type == 'user',
            Callfiltermember.bstype == 'secretary',
            Callfiltermember.typeval == cast(UserFeatures.id, String)
        )""",
        foreign_keys='Callfiltermember.typeval',
        cascade='delete, delete-orphan',
        overlaps='call_filter_recipients,user',
    )

    call_pickup_interceptors = relationship(
        'PickupMember',
        primaryjoin="""and_(
            PickupMember.category == 'member',
            PickupMember.membertype == 'user',
            PickupMember.memberid == UserFeatures.id
        )""",
        foreign_keys='PickupMember.memberid',
        cascade='delete, delete-orphan',
        overlaps='call_pickup_targets,call_pickup_interceptors,user,group',
    )
    call_pickup_targets = relationship(
        'PickupMember',
        primaryjoin="""and_(
            PickupMember.category == 'pickup',
            PickupMember.membertype == 'user',
            PickupMember.memberid == UserFeatures.id
        )""",
        foreign_keys='PickupMember.memberid',
        cascade='delete, delete-orphan',
        overlaps='call_pickup_targets,call_pickup_interceptors,user,group',
    )

    rightcall_members = relationship(
        'RightCallMember',
        primaryjoin="""and_(
            RightCallMember.type == 'user',
            RightCallMember.typeval == cast(UserFeatures.id, String)
        )""",
        foreign_keys='RightCallMember.typeval',
        cascade='all, delete-orphan',
        overlaps='rightcall_members',
    )

    call_permissions = association_proxy('rightcall_members', 'rightcall')

    call_pickup_interceptor_pickups = relationship(
        'Pickup',
        primaryjoin="""and_(
            PickupMember.category == 'member',
            PickupMember.membertype == 'user',
            PickupMember.memberid == UserFeatures.id
        )""",
        secondary="pickupmember",
        secondaryjoin="Pickup.id == pickupmember.c.pickupid",
        foreign_keys='PickupMember.pickupid,PickupMember.memberid',
        viewonly=True,
    )

    users_from_call_pickup_user_targets = association_proxy(
        'call_pickup_interceptor_pickups', 'user_targets'
    )
    users_from_call_pickup_group_targets = association_proxy(
        'call_pickup_interceptor_pickups', 'users_from_group_targets'
    )
    users_from_call_pickup_group_interceptors_user_targets = association_proxy(
        'group_members', 'users_from_call_pickup_group_interceptor_user_targets'
    )
    users_from_call_pickup_group_interceptors_group_targets = association_proxy(
        'group_members', 'users_from_call_pickup_group_interceptor_group_targets'
    )

    func_keys = relationship('FuncKeyDestUser', cascade='all, delete-orphan')
    tenant = relationship('Tenant')

    def extrapolate_caller_id(self, extension=None):
        default_num = extension.exten if extension else None
        user_match = caller_id_regex.match(self.callerid)
        name = user_match.group('name')
        num = user_match.group('num')
        return name, (num or default_num)

    def fill_caller_id(self):
        if self.caller_id is None:
            self.caller_id = f'"{self.fullname}"'

    @property
    def fallbacks(self):
        return self.user_dialactions

    @fallbacks.setter
    def fallbacks(self, dialactions):
        for event in list(self.user_dialactions.keys()):
            if event not in dialactions:
                self.user_dialactions.pop(event, None)

        for event, dialaction in dialactions.items():
            if dialaction is None:
                self.user_dialactions.pop(event, None)
                continue

            if event not in self.user_dialactions:
                dialaction.category = 'user'
                dialaction.event = event
                self.user_dialactions[event] = dialaction

            self.user_dialactions[event].action = dialaction.action
            self.user_dialactions[event].actionarg1 = dialaction.actionarg1
            self.user_dialactions[event].actionarg2 = dialaction.actionarg2

    @hybrid_property
    def fullname(self):
        name = self.firstname
        if self.lastname:
            name += f" {self.lastname}"
        return name

    @fullname.expression
    def fullname(cls):
        return func.trim(cls.firstname + " " + cls.webi_lastname)

    @hybrid_property
    def username(self):
        if self.loginclient == '':
            return None
        return self.loginclient

    @username.expression
    def username(cls):
        return func.nullif(cls.loginclient, '')

    @username.setter
    def username(self, value):
        if value is None:
            self.loginclient = ''
        else:
            self.loginclient = value

    @hybrid_property
    def password(self):
        if self.passwdclient == '':
            return None
        return self.passwdclient

    @password.expression
    def password(cls):
        return func.nullif(cls.passwdclient, '')

    @password.setter
    def password(self, value):
        if value is None:
            self.passwdclient = ''
        else:
            self.passwdclient = value

    @hybrid_property
    def agent_id(self):
        return self.agentid

    @agent_id.setter
    def agent_id(self, value):
        self.agentid = value

    @hybrid_property
    def caller_id(self):
        if self.callerid == '':
            return None
        return self.callerid

    @caller_id.expression
    def caller_id(cls):
        return func.nullif(cls.callerid, '')

    @caller_id.setter
    def caller_id(self, value):
        if value is None:
            self.callerid = ''
        else:
            self.callerid = value

    @hybrid_property
    def outgoing_caller_id(self):
        if self.outcallerid == '':
            return None
        return self.outcallerid

    @outgoing_caller_id.expression
    def outgoing_caller_id(cls):
        return func.nullif(cls.outcallerid, '')

    @outgoing_caller_id.setter
    def outgoing_caller_id(self, value):
        if value is None:
            self.outcallerid = ''
        else:
            self.outcallerid = value

    @hybrid_property
    def music_on_hold(self):
        if self.musiconhold == '':
            return None
        return self.musiconhold

    @music_on_hold.expression
    def music_on_hold(cls):
        return func.nullif(cls.musiconhold, '')

    @music_on_hold.setter
    def music_on_hold(self, value):
        if value is None:
            self.musiconhold = ''
        else:
            self.musiconhold = value

    @hybrid_property
    def mobile_phone_number(self):
        if self.mobilephonenumber == '':
            return None
        return self.mobilephonenumber

    @mobile_phone_number.expression
    def mobile_phone_number(cls):
        return func.nullif(cls.mobilephonenumber, '')

    @mobile_phone_number.setter
    def mobile_phone_number(self, value):
        if value is None:
            self.mobilephonenumber = ''
        else:
            self.mobilephonenumber = value

    @hybrid_property
    def voicemail_id(self):
        return self.voicemailid

    @voicemail_id.setter
    def voicemail_id(self, value):
        self.voicemailid = value

    @hybrid_property
    def userfield(self):
        if self.webi_userfield == '':
            return None
        return self.webi_userfield

    @userfield.expression
    def userfield(cls):
        return func.nullif(cls.webi_userfield, '')

    @userfield.setter
    def userfield(self, value):
        if value is None:
            self.webi_userfield = ''
        else:
            self.webi_userfield = value

    @hybrid_property
    def lastname(self):
        if self.webi_lastname == '':
            return None
        return self.webi_lastname

    @lastname.expression
    def lastname(cls):
        return func.nullif(cls.webi_lastname, '')

    @lastname.setter
    def lastname(self, value):
        if value is None:
            self.webi_lastname = ''
        else:
            self.webi_lastname = value

    @hybrid_property
    def description(self):
        if self.webi_description == '':
            return None
        return self.webi_description

    @description.expression
    def description(cls):
        return func.nullif(cls.webi_description, '')

    @description.setter
    def description(self, value):
        if value is None:
            self.webi_description = ''
        else:
            self.webi_description = value

    @hybrid_property
    def template_id(self):
        return self.func_key_template_id

    @template_id.setter
    def template_id(self, value):
        self.func_key_template_id = value

    @hybrid_property
    def private_template_id(self):
        return self.func_key_private_template_id

    @private_template_id.setter
    def private_template_id(self, value):
        self.func_key_private_template_id = value

    @hybrid_property
    def incallfilter_enabled(self):
        return self.incallfilter == 1

    @incallfilter_enabled.setter
    def incallfilter_enabled(self, value):
        self.incallfilter = int(value == 1) if value is not None else None

    @hybrid_property
    def dnd_enabled(self):
        return self.enablednd == 1

    @dnd_enabled.setter
    def dnd_enabled(self, value):
        self.enablednd = int(value == 1) if value is not None else None

    @hybrid_property
    def supervision_enabled(self):
        if self.enablehint is None:
            return None
        return self.enablehint == 1

    @supervision_enabled.setter
    def supervision_enabled(self, value):
        self.enablehint = int(value == 1) if value is not None else None

    @hybrid_property
    def call_transfer_enabled(self):
        if self.enablexfer is None:
            return None
        return self.enablexfer == 1

    @call_transfer_enabled.setter
    def call_transfer_enabled(self, value):
        self.enablexfer = int(value == 1) if value is not None else None

    @hybrid_property
    def dtmf_hangup_enabled(self):
        if self.dtmf_hangup is None:
            return None
        return self.dtmf_hangup == 1

    @dtmf_hangup_enabled.setter
    def dtmf_hangup_enabled(self, value):
        self.dtmf_hangup = int(value == 1) if value is not None else None

    @hybrid_property
    def online_call_record_enabled(self):
        if self.enableonlinerec is None:
            return None
        return self.enableonlinerec == 1

    @online_call_record_enabled.setter
    def online_call_record_enabled(self, value):
        self.enableonlinerec = int(value == 1) if value is not None else None

    @hybrid_property
    def ring_seconds(self):
        return self.ringseconds

    @ring_seconds.setter
    def ring_seconds(self, value):
        self.ringseconds = value

    @hybrid_property
    def simultaneous_calls(self):
        return self.simultcalls

    @simultaneous_calls.setter
    def simultaneous_calls(self, value):
        self.simultcalls = value

    @hybrid_property
    def cti_enabled(self):
        if self.enableclient is None:
            return None
        return self.enableclient == 1

    @cti_enabled.setter
    def cti_enabled(self, value):
        self.enableclient = int(value == 1) if value is not None else None

    @hybrid_property
    def busy_enabled(self):
        if self.enablebusy is None:
            return None
        return self.enablebusy == 1

    @busy_enabled.setter
    def busy_enabled(self, value):
        self.enablebusy = int(value == 1) if value is not None else None

    @hybrid_property
    def busy_destination(self):
        if self.destbusy == '':
            return None
        return self.destbusy

    @busy_destination.expression
    def busy_destination(cls):
        return func.nullif(cls.destbusy, '')

    @busy_destination.setter
    def busy_destination(self, value):
        if value is None:
            self.destbusy = ''
        else:
            self.destbusy = value

    @hybrid_property
    def noanswer_enabled(self):
        if self.enablerna is None:
            return None
        return self.enablerna == 1

    @noanswer_enabled.setter
    def noanswer_enabled(self, value):
        self.enablerna = int(value == 1) if value is not None else None

    @hybrid_property
    def noanswer_destination(self):
        if self.destrna == '':
            return None
        return self.destrna

    @noanswer_destination.expression
    def noanswer_destination(cls):
        return func.nullif(cls.destrna, '')

    @noanswer_destination.setter
    def noanswer_destination(self, value):
        if value is None:
            self.destrna = ''
        else:
            self.destrna = value

    @hybrid_property
    def unconditional_enabled(self):
        if self.enableunc is None:
            return None
        return self.enableunc == 1

    @unconditional_enabled.setter
    def unconditional_enabled(self, value):
        self.enableunc = int(value == 1) if value is not None else None

    @hybrid_property
    def unconditional_destination(self):
        if self.destunc == '':
            return None
        return self.destunc

    @unconditional_destination.expression
    def unconditional_destination(cls):
        return func.nullif(cls.destunc, '')

    @unconditional_destination.setter
    def unconditional_destination(self, value):
        if value is None:
            self.destunc = ''
        else:
            self.destunc = value

    @hybrid_property
    def enabled(self):
        if self.commented is None:
            return None
        return self.commented == 0

    @enabled.expression
    def enabled(cls):
        return not_(cast(cls.commented, Boolean))

    @enabled.setter
    def enabled(self, value):
        self.commented = int(value is False) if value is not None else None

    @hybrid_property
    def call_permission_password(self):
        if self.rightcallcode == '':
            return None
        return self.rightcallcode

    @call_permission_password.expression
    def call_permission_password(cls):
        return func.nullif(cls.rightcallcode, '')

    @call_permission_password.setter
    def call_permission_password(self, value):
        if value == '':
            self.rightcallcode = None
        else:
            self.rightcallcode = value

    @property
    def forwards(self):
        return self

    @property
    def services(self):
        return self

    @property
    def country(self):
        return self.tenant.country
