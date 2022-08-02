# Copyright 2020, Microsoft Corporation
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
from typing import List

from ..exception import InvalidType, InvalidCheckValue
from .checkermodule import CheckerModule
from .util import config_bool_value


ATTR_OPT = "attr"
MISSINOK_OPT = "missing_ok"


class EmptyTypeAttr(CheckerModule):

    """Checker module for asserting a type attribute is empty."""

    check_type = "empty_typeattr"
    check_config = frozenset((ATTR_OPT, MISSINOK_OPT))

    def __init__(self, policy, checkname, config) -> None:
        super().__init__(policy, checkname, config)
        self.log = logging.getLogger(__name__)
        self._attr = None
        self._missing_ok = False

        # this will make the check pass automatically
        # since the attribute is missing.  Only set if
        # missing_ok is True AND attr is missing.
        self._pass_by_missing = False

        self.missing_ok = config.get(MISSINOK_OPT)
        self.attr = config.get(ATTR_OPT)

    @property
    def attr(self):
        return self._attr

    @attr.setter
    def attr(self, value):
        try:
            if not value:
                raise InvalidCheckValue(
                    f'{self.checkname}: \"{ATTR_OPT}\" setting is missing.'
                )


            self._attr = self.policy.lookup_typeattr(value)
            self._pass_by_missing = False

        except InvalidType as e:
            if not self.missing_ok:
                raise InvalidCheckValue(f"{self.checkname}: attr setting error: {e}") from e

            self._attr = value
            self._pass_by_missing = True

    @property
    def missing_ok(self):
        return self._missing_ok

    @missing_ok.setter
    def missing_ok(self, value):
        self._missing_ok = config_bool_value(value)

        self._pass_by_missing = bool(self._missing_ok and isinstance(self.attr, str))

    def run(self) -> List:
        self.log.info(f"Checking type attribute {self.attr} is empty.")

        failures = []

        if self._pass_by_missing:
            self.log_info(f"    {self.attr} does not exist.")
        else:
            self.output.write(f"Member types of {self.attr}:\n")

            if types := sorted(self.attr.expand()):
                for type_ in types:
                    self.log_fail(type_.name)
                    failures.append(type_)
            else:
                self.log_ok("    <empty>")

        self.log.debug(f"{failures} failure(s)")
        return failures
