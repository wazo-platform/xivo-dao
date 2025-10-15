# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from uuid import uuid4

from hamcrest import (
    all_of,
    assert_that,
    contains_inanyorder,
    equal_to,
    has_item,
    has_items,
    has_properties,
    not_,
)

from xivo_dao.tests.test_dao import DAOTestCase


class TestOptions(DAOTestCase):
    def test_getter(self):
        queue = self.add_queue(timeout=5)
        assert_that(queue.options, has_item(has_items('timeout', '5')))

    def test_getter_default_values(self):
        queue = self.add_queue()

        assert_that(
            queue.options,
            contains_inanyorder(
                has_items('timeout', '0'),
                has_items('ringinuse', 'no'),
                has_items('reportholdtime', 'no'),
                has_items('timeoutrestart', 'no'),
                has_items('timeoutpriority', 'app'),
                has_items('autofill', 'yes'),
                has_items('autopause', 'no'),
                has_items('setinterfacevar', 'no'),
                has_items('setqueueentryvar', 'no'),
                has_items('setqueuevar', 'no'),
                has_items('min-announce-frequency', '60'),
                has_items('random-periodic-announce', 'no'),
                has_items('announce-position', 'yes'),
                has_items('announce-position-limit', '5'),
            ),
        )

    def test_getter_exclude_columns(self):
        queue = self.add_queue(
            name='name',
            category='queue',
            commented='1',
            musicclass='musicclass',
        )

        assert_that(
            queue.options,
            all_of(
                not_(has_items(has_item('name'))),
                not_(has_items(has_item('category'))),
                not_(has_items(has_item('commented'))),
                not_(has_items(has_item('musicclass'))),
            ),
        )

    def test_getter_custom_columns(self):
        queue = self.add_queue()

        assert_that(
            queue.options,
            all_of(
                not_(has_items(has_item('enabled'))),
                not_(has_items(has_item('ring_in_use'))),
            ),
        )

    def test_getter_integer_values(self):
        queue = self.add_queue()
        assert_that(
            queue.options,
            has_items(
                has_items('ringinuse', 'no'),
                has_items('reportholdtime', 'no'),
                has_items('timeoutrestart', 'no'),
                has_items('autofill', 'yes'),
                has_items('setinterfacevar', 'no'),
                has_items('setqueueentryvar', 'no'),
                has_items('setqueuevar', 'no'),
                has_items('random-periodic-announce', 'no'),
            ),
        )

    def test_setter(self):
        queue = self.add_queue(defaultrule='111')

        queue.options = [['defaultrule', '222']]
        self.session.flush()

        self.session.expire_all()
        assert_that(queue.defaultrule, equal_to('222'))

    def test_setter_default_values(self):
        queue = self.add_queue(
            timeout=10,
            ringinuse=10,
            reportholdtime=1,
            timeoutrestart=10,
            timeoutpriority='toto',
            autofill=10,
            autopause='yes',
            setinterfacevar=1,
            setqueueentryvar=1,
            setqueuevar=1,
            min_announce_frequency=30,
            random_periodic_announce=10,
            announce_position='no',
            announce_position_limit=15,
        )

        queue.options = []
        self.session.flush()

        self.session.expire_all()
        assert_that(
            queue,
            has_properties(
                timeout=0,
                ringinuse=0,
                reportholdtime=0,
                timeoutrestart=0,
                timeoutpriority='app',
                autofill=1,
                autopause='no',
                setinterfacevar=0,
                setqueueentryvar=0,
                setqueuevar=0,
                min_announce_frequency=60,
                random_periodic_announce=0,
                announce_position='yes',
                announce_position_limit=5,
            ),
        )

    def test_setter_exclude_columns(self):
        queue = self.add_queue(
            name='name',
            category='queue',
            commented=0,
            musicclass='musicclass',
        )
        queue.options = [
            ['name', 'other_name'],
            ['category', 'other_category'],
            ['commented', '1'],
            ['musicclass', 'other_musicclass'],
            ['default', 'other_default'],
        ]
        self.session.flush()

        self.session.expire_all()
        assert_that(
            queue,
            has_properties(
                name='name',
                category='queue',
                commented=0,
                musicclass='musicclass',
            ),
        )

    def test_setter_custom_columns(self):
        queue = self.add_queue(enabled=True, ring_in_use=False)
        queue.options = [
            ['enabled', 'False'],
            ['ring_in_use', 'True'],
        ]
        self.session.flush()

        self.session.expire_all()
        assert_that(
            queue,
            has_properties(
                enabled=True,
                ring_in_use=False,
            ),
        )

    def test_setter_integer_values(self):
        queue = self.add_queue()
        queue.options = [
            ['ringinuse', 'yes'],
            ['reportholdtime', 'yes'],
            ['timeoutrestart', 'yes'],
            ['autofill', 'no'],
            ['setinterfacevar', 'yes'],
            ['setqueueentryvar', 'yes'],
            ['setqueuevar', 'yes'],
            ['random-periodic-announce', 'yes'],
        ]
        self.session.flush()

        self.session.expire_all()
        assert_that(
            queue,
            has_properties(
                ringinuse=1,
                reportholdtime=1,
                timeoutrestart=1,
                autofill=0,
                setinterfacevar=1,
                setqueueentryvar=1,
                setqueuevar=1,
                random_periodic_announce=1,
            ),
        )

    def test_label_group(self):
        group_uuid = uuid4()
        name = f'grp-mytenant-{group_uuid}'
        group = self.add_group(uuid=group_uuid, name=name, label='mylabel')
        self.session.flush()

        self.session.expire_all()
        assert_that(
            group._queue,
            has_properties(
                name=name,
                label='mylabel',
            ),
        )

    def test_label_queue(self):
        queuefeatures = self.add_queuefeatures(name='name', displayname='mylabel')
        self.session.flush()

        self.session.expire_all()
        assert_that(
            queuefeatures._queue,
            has_properties(
                name='name',
                label='mylabel',
            ),
        )

    def test_label_no_group_no_queue(self):
        queue = self.add_queue(category='group')
        self.session.flush()

        self.session.expire_all()
        assert_that(queue, has_properties(label='unknown'))

        queue = self.add_queue(category='queue')
        self.session.flush()

        self.session.expire_all()
        assert_that(queue, has_properties(label='unknown'))

        queue = self.add_queue()
        self.session.flush()

        self.session.expire_all()
        assert_that(queue, has_properties(label='unknown'))
