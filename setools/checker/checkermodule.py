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

import sys
import logging
from abc import ABCMeta, abstractmethod
from typing import Dict, FrozenSet, List, Mapping

from ..exception import InvalidCheckOption
from ..policyrep import SELinuxPolicy

from .globalkeys import CHECK_TYPE_KEY, CHECK_DESC_KEY, CHECK_DISABLE, GLOBAL_CONFIG_KEYS


CHECKER_REGISTRY: Dict[str, type] = {}

__all__ = ['CheckerModule']


class CheckRegistry(ABCMeta):

    """Checker module registry metaclass.  This registers modules in the check registry."""

    def __new__(cls, clsname, superclasses, attributedict):
        check_type = attributedict.get("check_type")
        check_config = attributedict.get("check_config")

        if clsname != "CheckerModule":
            if not isinstance(check_type, str):
                raise TypeError(f"Checker module {clsname} does not set a check_type.")

            if not isinstance(check_config, frozenset):
                raise TypeError(f"Checker module {clsname} does not set a valid check_config.")

            if check_type in CHECKER_REGISTRY:
                existing_check_module = CHECKER_REGISTRY[check_type].__name__
                raise TypeError(
                    f"Checker module {clsname} conflicts with registered check {existing_check_module}"
                )


        classdef = super().__new__(cls, clsname, superclasses, attributedict)

        if check_type:
            CHECKER_REGISTRY[check_type] = classdef

        return classdef


class CheckerModule(metaclass=CheckRegistry):

    """Abstract base class for policy checker modules."""

    # The name of the check used in config files.
    # This must be set by subclasses.
    check_type: str

    # The container of valid config keys specific to the check
    # This is in addition to the common config keys
    # in the GLOBAL_CONFIG_KEYS above.  This must be set by subclasses.
    # If no additional keys  are needed, this should be set to an
    # empty container.
    check_config: FrozenSet[str]

    # T/F log findings that pass the check.
    log_passing: bool = False

    # Default output to stdout.
    output = sys.stdout

    policy: SELinuxPolicy

    def __init__(self, policy: SELinuxPolicy, checkname: str, config: Mapping[str, str]) -> None:
        self.policy = policy
        self.checkname = checkname

        # ensure there is a logger available. This should
        # be replaced with the concrete class' logger
        self.log = logging.getLogger(__name__)

        # Check available options are valid
        valid_options = GLOBAL_CONFIG_KEYS | self.check_config
        for k in config:
            if k not in valid_options:
                raise InvalidCheckOption(f"{self.checkname}: Invalid option: {k}")

        # Make sure all global config attrs are initialized for this check
        self.desc = config.get(CHECK_DESC_KEY)
        self.disable = config.get(CHECK_DISABLE)

    def log_info(self, msg: str) -> None:
        """Output an informational message."""
        self.output.write(msg)
        self.output.write("\n")
        self.log.debug(msg)

    def log_ok(self, msg: str) -> None:
        """
        Log findings that pass the check.  By default these messages are
        surpressed unless self.log_passing is True.
        """
        if self.log_passing:
            self.output.write(f"P   * {msg}\n")
        self.log.debug(f"P   * {msg}")

    def log_fail(self, msg: str) -> None:
        """Log findings that fail the check."""
        self.output.write(f'{"F" if self.log_passing else " "}   * {msg}\n')
        self.log.debug(f"F   * {msg}")

    @abstractmethod
    def run(self) -> List:
        """
        Run the configured check on the policy.

        Return:   List of failed items in the check.  If the check passes, list is empty.
        """
        pass
