# Copyright 2018-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains_exactly,
    equal_to,
    empty,
)
from xivo_dao.tests.test_dao import DAOTestCase

from ..queueskillrule import QueueSkillRule


class TestRules(DAOTestCase):

    def test_getter(self):
        skill_rule = QueueSkillRule(rule='abcd;1234')
        assert_that(skill_rule.rules, contains_exactly('abcd', '1234'))

    def test_getter_empty(self):
        skill_rule = QueueSkillRule(rule=None)
        assert_that(skill_rule.rules, empty())

    def test_setter(self):
        skill_rule = QueueSkillRule(rules=['abcd', '1234'])
        assert_that(skill_rule.rule, equal_to('abcd;1234'))

    def test_setter_empty(self):
        skill_rule = QueueSkillRule(rules=[])
        assert_that(skill_rule.rule, equal_to(None))

    def test_expression(self):
        skill_rule = self.add_queue_skill_rule(rules=['abcd', '1234'])
        result = self.session.query(QueueSkillRule).filter_by(rules=['abcd', '1234']).first()
        assert_that(result, equal_to(skill_rule))

    def test_expression_empty_rule(self):
        skill_rule = self.add_queue_skill_rule(rule='')
        result = self.session.query(QueueSkillRule).filter_by(rules=[]).first()
        assert_that(result, equal_to(skill_rule))

    def test_expression_null_rule(self):
        skill_rule = self.add_queue_skill_rule(rule=None)
        result = self.session.query(QueueSkillRule).filter_by(rules=[]).first()
        assert_that(result, equal_to(skill_rule))
