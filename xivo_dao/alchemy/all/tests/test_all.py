# Copyright 2021-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


import importlib
import inspect
import pkgutil
import xivo_dao.alchemy
import xivo_dao.alchemy.all

from xivo_dao.helpers.db_manager import Base


def list_exported_classes():
    yield from sorted(xivo_dao.alchemy.all.__all__)


def explore_alchemy():
    for sub_module in pkgutil.walk_packages(
        xivo_dao.alchemy.__path__, prefix='xivo_dao.alchemy.'
    ):
        _, sub_module_name, _ = sub_module

        if '.tests.' in sub_module_name:
            continue

        yield sub_module_name


def list_model_names():
    for submodule_name in explore_alchemy():
        submodule = importlib.import_module(submodule_name)

        for element_name in dir(submodule):
            element = getattr(submodule, element_name)
            if not inspect.isclass(element):
                continue
            if not issubclass(element, Base):
                continue
            if element_name == 'Base':
                continue
            if element_name == 'MaterializedView':
                continue

            # Exclude polymorphic classes that are not real tables
            if ('polymorphic_identity' in getattr(element, '__mapper_args__', {})
                    and 'polymorphic_on' not in getattr(element, '__mapper_args__', {})):
                continue

            yield element_name


def test_all_classes_exported():
    assert set(list_model_names()) == set(list_exported_classes())
