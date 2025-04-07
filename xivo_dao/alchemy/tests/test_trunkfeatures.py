# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, calling, equal_to, raises
from sqlalchemy.exc import IntegrityError

from xivo_dao.tests.test_dao import DAOTestCase

from ..trunkfeatures import TrunkFeatures as Trunk


class TestConstraint(DAOTestCase):
    def test_many_endpoints(self):
        sip = self.add_endpoint_sip()
        iax = self.add_useriax()
        assert_that(
            calling(self.add_trunk).with_args(
                endpoint_sip_uuid=sip.uuid,
                endpoint_iax_id=iax.id,
            ),
            raises(IntegrityError),
        )

    def test_register_iax_endpoint_sip_raise_integrity(self):
        sip = self.add_endpoint_sip()
        register_iax = self.add_register_iax()
        assert_that(
            calling(self.add_trunk).with_args(
                endpoint_sip_uuid=sip.uuid,
                register_iax_id=register_iax.id,
            ),
            raises(IntegrityError),
        )

    def test_register_iax_endpoint_custom_raise_integrity(self):
        custom = self.add_usercustom()
        register_iax = self.add_register_iax()
        assert_that(
            calling(self.add_trunk).with_args(
                endpoint_custom_id=custom.id,
                register_iax_id=register_iax.id,
            ),
            raises(IntegrityError),
        )


class TestName(DAOTestCase):
    def test_getter_endpoint_sip(self):
        name = 'my-custom-name'
        sip = self.add_endpoint_sip(name=name)
        trunk = self.add_trunk(endpoint_sip_uuid=sip.uuid)

        assert_that(trunk.name, equal_to(name))

    def test_getter_endpoint_iax(self):
        name = 'my-custom-name'
        iax = self.add_useriax(name=name)
        trunk = self.add_trunk(endpoint_iax_id=iax.id)

        assert_that(trunk.name, equal_to(name))

    def test_getter_endpoint_custom(self):
        name = 'my-custom-interface'
        custom = self.add_usercustom(interface=name)
        trunk = self.add_trunk(endpoint_custom_id=custom.id)

        assert_that(trunk.name, equal_to(name))

    def test_getter_other(self):
        trunk = self.add_trunk()

        assert_that(trunk.name, equal_to(None))

    def test_expression_endpoint_sip(self):
        name = 'my-custom-name'
        sip = self.add_endpoint_sip(name=name)
        trunk = self.add_trunk(endpoint_sip_uuid=sip.uuid)

        result = self.session.query(Trunk).filter(Trunk.name == name).first()

        assert_that(result, equal_to(trunk))
        assert_that(result.name, equal_to(name))

    def test_expression_endpoint_iax(self):
        name = 'my-custom-name'
        iax = self.add_useriax(name=name)
        trunk = self.add_trunk(endpoint_iax_id=iax.id)

        result = self.session.query(Trunk).filter(Trunk.name == name).first()

        assert_that(result, equal_to(trunk))
        assert_that(result.name, equal_to(name))

    def test_expression_endpoint_custom(self):
        name = 'my-custom-name'
        custom = self.add_usercustom(interface=name)
        trunk = self.add_trunk(endpoint_custom_id=custom.id)

        result = self.session.query(Trunk).filter(Trunk.name == name).first()

        assert_that(result, equal_to(trunk))
        assert_that(result.name, equal_to(name))

    def test_expression_other(self):
        trunk = self.add_trunk()

        result = self.session.query(Trunk).filter(Trunk.name.is_(None)).first()

        assert_that(result, equal_to(trunk))
        assert_that(result.name, equal_to(None))


class TestLabel(DAOTestCase):
    def test_getter_endpoint_sip(self):
        label = 'my-custom-label'
        sip = self.add_endpoint_sip(label=label)
        trunk = self.add_trunk(endpoint_sip_uuid=sip.uuid)

        assert_that(trunk.label, equal_to(label))

    def test_getter_other(self):
        trunk = self.add_trunk()

        assert_that(trunk.label, equal_to(None))

    def test_expression_endpoint_sip(self):
        label = 'my-custom-label'
        sip = self.add_endpoint_sip(label=label)
        trunk = self.add_trunk(endpoint_sip_uuid=sip.uuid)

        result = self.session.query(Trunk).filter(Trunk.label == label).first()

        assert_that(result, equal_to(trunk))
        assert_that(result.label, equal_to(label))

    def test_expression_other(self):
        trunk = self.add_trunk()

        result = self.session.query(Trunk).filter(Trunk.label.is_(None)).first()

        assert_that(result, equal_to(trunk))
        assert_that(result.label, equal_to(None))
