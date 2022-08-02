# Copyright 2019, Chris PeBenito <pebenito@ieee.org>
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
from PyQt5.QtCore import Qt

from .models import SEToolsTableModel


class IbpkeyconTableModel(SEToolsTableModel):

    """Table-based model for ibpkeycons."""

    headers = ["Subnet Prefix", "Partition Keys", "Context"]

    def data(self, index, role):
        if not self.resultlist or not index.isValid():
            return
        row = index.row()
        col = index.column()
        rule = self.resultlist[row]

        if role == Qt.DisplayRole:
            if col == 0:
                return str(rule.subnet_prefix)
            elif col == 1:
                low, high = rule.pkeys
                return (
                    "{0:#x}".format(low)
                    if low == high
                    else "{0:#x}-{1:#x}".format(low, high)
                )

            elif col == 2:
                return str(rule.context)

        elif role == Qt.UserRole:
            return rule
