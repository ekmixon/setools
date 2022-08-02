# Copyright 2016, Tresys Technology, LLC
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


class PortconTableModel(SEToolsTableModel):

    """Table-based model for portcons."""

    headers = ["Port/Port Range", "Protocol", "Context"]

    def data(self, index, role):
        if not self.resultlist or not index.isValid():
            return
        row = index.row()
        col = index.column()
        rule = self.resultlist[row]

        if role == Qt.DisplayRole:
            if col == 0:
                low, high = rule.ports
                return str(low) if low == high else "{0}-{1}".format(low, high)
            elif col == 1:
                return rule.protocol.name
            elif col == 2:
                return str(rule.context)

        elif role == Qt.UserRole:
            return rule
