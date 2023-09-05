# Copyright 2013-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao import callfilter_dao
from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.tests.test_dao import DAOTestCase


class BaseTestCallFilterDAO(DAOTestCase):
    def _add_user_to_filter(self, userid, filterid, role='boss'):
        member = Callfiltermember()
        member.type = 'user'
        member.typeval = str(userid)
        member.callfilterid = filterid
        member.bstype = role
        self.add_me(member)
        return member


class TestGetSecretariesIdByContext(BaseTestCallFilterDAO):
    def setUp(self):
        super().setUp()
        self.default_context = self.add_context(name='default')
        self.context = self.add_context()

    def _create_user_and_add_to_filter(self, filter_id, role, context='mycontext'):
        user_line_row = self.add_user_line_with_exten(context=context)
        filter_member_row = self._add_user_to_filter(
            user_line_row.user_id, filter_id, role
        )
        return filter_member_row

    def test_given_no_secretaries_then_returns_empty_list(self):
        result = callfilter_dao.get_secretaries_id_by_context(self.default_context.name)

        self.assertEqual(result, [])

    def test_given_boss_then_returns_empty_list(self):
        call_filter = self.add_call_filter()
        self._create_user_and_add_to_filter(call_filter.id, 'boss', self.context.name)

        result = callfilter_dao.get_secretaries_id_by_context(self.context.name)

        self.assertEqual(result, [])

    def test_given_one_secretary_then_returns_list_with_id(self):
        call_filter = self.add_call_filter()
        member = self._create_user_and_add_to_filter(
            call_filter.id, 'secretary', self.context.name
        )

        result = callfilter_dao.get_secretaries_id_by_context(self.context.name)

        self.assertEqual(len(result), 1)
        self.assertIn((member.id,), result)

    def test_given_two_secretaries_then_returns_list_with_both_ids(self):
        call_filter = self.add_call_filter()
        first_member = self._create_user_and_add_to_filter(
            call_filter.id, 'secretary', self.context.name
        )
        second_member = self._create_user_and_add_to_filter(
            call_filter.id, 'secretary', self.context.name
        )

        result = callfilter_dao.get_secretaries_id_by_context(self.context.name)

        self.assertEqual(len(result), 2)
        self.assertIn((first_member.id,), result)
        self.assertIn((second_member.id,), result)

    def test_given_line_with_multiple_users_then_returns_list_with_one_id(self):
        call_filter = self.add_call_filter()
        extension = self.add_extension(context=self.context.name)

        line = self.add_line(context=self.context.name)
        main_user = self.add_user()
        secondary_user = self.add_user()

        self.add_user_line(
            user_id=main_user.id, line_id=line.id, main_user=True, main_line=True
        )
        self.add_user_line(
            user_id=secondary_user.id, line_id=line.id, main_user=False, main_line=True
        )
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

        member = self._add_user_to_filter(main_user.id, call_filter.id, 'secretary')

        result = callfilter_dao.get_secretaries_id_by_context(self.context.name)

        self.assertEqual(len(result), 1)
        self.assertIn((member.id,), result)

    def test_given_user_with_multiple_line_then_returns_list_with_one_id(self):
        call_filter = self.add_call_filter()
        extension = self.add_extension(context=self.context.name)

        main_line = self.add_line(context=self.context.name)
        secondary_line = self.add_line(context=self.context.name)
        user = self.add_user()

        self.add_user_line(
            user_id=user.id, line_id=main_line.id, main_user=True, main_line=True
        )
        self.add_user_line(
            user_id=user.id, line_id=secondary_line.id, main_user=True, main_line=False
        )
        self.add_line_extension(line_id=main_line.id, extension_id=extension.id)
        self.add_line_extension(line_id=secondary_line.id, extension_id=extension.id)

        member = self._add_user_to_filter(user.id, call_filter.id, 'secretary')

        result = callfilter_dao.get_secretaries_id_by_context(self.context.name)

        self.assertEqual(len(result), 1)
        self.assertIn((member.id,), result)


class TestCallFilterDAO(BaseTestCallFilterDAO):
    def test_get_with_no_filter(self):
        call_filter_id = 1

        result = callfilter_dao.get(call_filter_id)

        self.assertEqual(result, [])

    def test_get_with_filter_but_no_members(self):
        call_filter = self.add_call_filter()

        result = callfilter_dao.get(call_filter.id)

        self.assertEqual(result, [])

    def test_get_with_filter_having_members(self):
        boss_id = 1
        call_filter = self.add_call_filter()
        self._add_user_to_filter(boss_id, call_filter.id, 'boss')

        result = callfilter_dao.get(call_filter.id)

        self.assertEqual(1, len(result))
        callfilter = result[0][0]
        member = result[0][1]
        self.assertEqual(callfilter.id, call_filter.id)
        self.assertEqual(member.typeval, str(boss_id))

    def test_get_with_filter_having_2_members(self):
        boss_id = 1
        secretary_id = 2
        call_filter = self.add_call_filter()
        self._add_user_to_filter(boss_id, call_filter.id, 'boss')
        self._add_user_to_filter(secretary_id, call_filter.id, 'secretary')

        result = callfilter_dao.get(call_filter.id)

        self.assertEqual(2, len(result))
        member_ids = [int(c[1].typeval) for c in result]
        self.assertIn(boss_id, member_ids)
        self.assertIn(secretary_id, member_ids)

    def test_does_secretary_filter_boss_with_no_filters(self):
        boss_id = 1
        secretary_id = 2

        result = callfilter_dao.does_secretary_filter_boss(boss_id, secretary_id)

        self.assertFalse(result)

    def test_does_secretary_filter_boss_with_no_boss_or_secretary(self):
        boss_id = 1
        secretary_id = 2
        self.add_call_filter()

        result = callfilter_dao.does_secretary_filter_boss(boss_id, secretary_id)

        self.assertFalse(result)

    def test_does_secretary_filter_boss_with_no_secretary(self):
        boss_id = 1
        secretary_id = 2
        call_filter = self.add_call_filter()
        self._add_user_to_filter(boss_id, call_filter.id, 'boss')

        result = callfilter_dao.does_secretary_filter_boss(boss_id, secretary_id)

        self.assertFalse(result)

    def test_does_secretary_filter_boss_with_no_boss(self):
        boss_id = 1
        secretary_id = 2
        call_filter = self.add_call_filter()
        self._add_user_to_filter(secretary_id, call_filter.id, 'secretary')

        result = callfilter_dao.does_secretary_filter_boss(boss_id, secretary_id)

        self.assertFalse(result)

    def test_does_secretary_filter_boss_with_boss_and_secretary_in_different_filters(
        self,
    ):
        boss_id = 1
        secretary_id = 2
        boss_call_filter = self.add_call_filter()
        secretatry_call_filter = self.add_call_filter()
        self._add_user_to_filter(boss_id, boss_call_filter.id, 'boss')
        self._add_user_to_filter(secretary_id, secretatry_call_filter.id, 'secretary')

        result = callfilter_dao.does_secretary_filter_boss(boss_id, secretary_id)

        self.assertFalse(result)

    def test_does_secretary_filter_boss_with_boss_and_secretary_in_same_filter(self):
        boss_id = 1
        secretary_id = 2
        call_filter = self.add_call_filter()
        self._add_user_to_filter(boss_id, call_filter.id, 'boss')
        self._add_user_to_filter(secretary_id, call_filter.id, 'secretary')

        result = callfilter_dao.does_secretary_filter_boss(boss_id, secretary_id)

        self.assertTrue(result)

    def test_does_secretary_filter_boss_with_2_secretaries(self):
        boss_id = 1
        first_secretary_id = 20
        second_secretary_id = 21
        call_filter = self.add_call_filter()
        self._add_user_to_filter(boss_id, call_filter.id, 'boss')
        self._add_user_to_filter(first_secretary_id, call_filter.id, 'secretary')
        self._add_user_to_filter(second_secretary_id, call_filter.id, 'secretary')

        first_result = callfilter_dao.does_secretary_filter_boss(
            boss_id, first_secretary_id
        )
        second_result = callfilter_dao.does_secretary_filter_boss(
            boss_id, second_secretary_id
        )

        self.assertTrue(first_result)
        self.assertTrue(second_result)

    def test_does_secretary_filter_boss_with_2_bosses(self):
        first_boss_id = 1
        second_boss_id = 2
        secretary_id = 20
        call_filter = self.add_call_filter()
        self._add_user_to_filter(secretary_id, call_filter.id, 'secretary')
        self._add_user_to_filter(first_boss_id, call_filter.id, 'boss')
        self._add_user_to_filter(second_boss_id, call_filter.id, 'boss')

        first_result = callfilter_dao.does_secretary_filter_boss(
            first_boss_id, secretary_id
        )
        second_result = callfilter_dao.does_secretary_filter_boss(
            second_boss_id, secretary_id
        )

        self.assertTrue(first_result)
        self.assertTrue(second_result)
