# Copyright 2020, Microsoft Corporation
# Copyright 2020, Chris PeBenito <pebenito@ieee.org>
#
# This file is part of SETools.
#
# SETools is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 2.1 of
# the License, or (at your option) any later version.
#
# SETools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with SETools.  If not, see
# <http://www.gnu.org/licenses/>.
#

import logging
from typing import List, Union

from ..exception import InvalidCheckValue
from ..policyrep import AnyTERule
from ..terulequery import TERuleQuery
from .checkermodule import CheckerModule
from .descriptors import ConfigDescriptor, ConfigSetDescriptor, ConfigPermissionSetDescriptor

SOURCE_OPT = "source"
TARGET_OPT = "target"
CLASS_OPT = "tclass"
PERMS_OPT = "perms"
EXEMPT_SRC_OPT = "exempt_source"
EXEMPT_TGT_OPT = "exempt_target"
EXPECT_SRC_OPT = "expect_source"
EXPECT_TGT_OPT = "expect_target"


class AssertTE(CheckerModule):

    """Checker module for asserting a type enforcement allow rule exists (or not)."""

    check_type = "assert_te"
    check_config = frozenset((SOURCE_OPT, TARGET_OPT, CLASS_OPT, PERMS_OPT, EXEMPT_SRC_OPT,
                              EXEMPT_TGT_OPT, EXPECT_SRC_OPT, EXPECT_TGT_OPT))

    source = ConfigDescriptor("lookup_type_or_attr")
    target = ConfigDescriptor("lookup_type_or_attr")
    tclass = ConfigSetDescriptor("lookup_class", strict=True, expand=False)
    perms = ConfigPermissionSetDescriptor()

    exempt_source = ConfigSetDescriptor("lookup_type_or_attr", strict=False, expand=True)
    exempt_target = ConfigSetDescriptor("lookup_type_or_attr", strict=False, expand=True)
    expect_source = ConfigSetDescriptor("lookup_type_or_attr", strict=True, expand=True)
    expect_target = ConfigSetDescriptor("lookup_type_or_attr", strict=True, expand=True)

    def __init__(self, policy, checkname, config) -> None:
        super().__init__(policy, checkname, config)
        self.log = logging.getLogger(__name__)

        self.source = config.get(SOURCE_OPT)
        self.target = config.get(TARGET_OPT)
        self.tclass = config.get(CLASS_OPT)
        self.perms = config.get(PERMS_OPT)

        self.exempt_source = config.get(EXEMPT_SRC_OPT)
        self.exempt_target = config.get(EXEMPT_TGT_OPT)
        self.expect_source = config.get(EXPECT_SRC_OPT)
        self.expect_target = config.get(EXPECT_TGT_OPT)

        if not any((self.source, self.target, self.tclass, self.perms)):
            raise InvalidCheckValue(
                "At least one of source, target, tclass, or perms options must be set.")

        if source_exempt_expect_overlap := self.exempt_source & self.expect_source:
            self.log.info(
                f'Overlap in expect_source and exempt_source: {", ".join((i.name for i in source_exempt_expect_overlap))}'
            )


        if target_exempt_expect_overlap := self.exempt_target & self.expect_target:
            self.log.info(
                f'Overlap in expect_target and exempt_target: {", ".join((i.name for i in target_exempt_expect_overlap))}'
            )

    def run(self) -> List:
        assert any((self.source, self.target, self.tclass, self.perms)), \
                "AssertTe no options set, this is a bug."

        self.log.info("Checking TE allow rule assertion.")

        query = TERuleQuery(self.policy,
                            source=self.source,
                            target=self.target,
                            tclass=self.tclass,
                            perms=self.perms,
                            ruletype=("allow",))

        unseen_sources = set(self.expect_source)
        unseen_targets = set(self.expect_target)
        failures: List[Union[AnyTERule, str]] = []
        for rule in sorted(query.results()):
            srcs = set(rule.source.expand())
            tgts = set(rule.target.expand())

            unseen_sources -= srcs
            unseen_targets -= tgts
            if (srcs - self.expect_source - self.exempt_source) and \
                        (tgts - self.expect_target - self.exempt_target):

                self.log_fail(str(rule))
                failures.append(rule)
            else:
                self.log_ok(str(rule))

        for item in unseen_sources:
            failure = f'Expected rule with source \"{item}\" not found.'
            self.log_fail(failure)
            failures.append(failure)

        for item in unseen_targets:
            failure = f'Expected rule with target \"{item}\" not found.'
            self.log_fail(failure)
            failures.append(failure)

        self.log.debug(f"{failures} failure(s)")
        return failures
