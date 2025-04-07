# Copyright 2024-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from xivo_dao.helpers.sequence_utils import split_by


class TestSplitBy(unittest.TestCase):
    def test_split_by(self):
        seq = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        approved, rejected = split_by(seq, lambda x: x < 5)
        self.assertEqual(approved, [0, 1, 2, 3, 4])
        self.assertEqual(rejected, [5, 6, 7, 8, 9])

    def test_split_by_empty(self):
        seq = []
        approved, rejected = split_by(seq, lambda x: x < 5)
        self.assertEqual(approved, [])
        self.assertEqual(rejected, [])

    def test_split_by_all_rejected(self):
        seq = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        approved, rejected = split_by(seq, lambda x: x > 10)
        self.assertEqual(approved, [])
        self.assertEqual(rejected, seq)

    def test_split_by_all_approved(self):
        seq = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        approved, rejected = split_by(seq, lambda x: x < 10)
        self.assertEqual(approved, seq)
        self.assertEqual(rejected, [])

    def test_split_by_non_iterable(self):
        seq = None
        with self.assertRaises(TypeError):
            _ = split_by(seq, lambda x: x)
