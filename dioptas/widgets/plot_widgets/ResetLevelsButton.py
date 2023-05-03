# -*- coding: utf-8 -*-
# Dioptas - GUI program for fast processing of 2D X-ray diffraction data
# Principal author: Clemens Prescher (clemens.prescher@gmail.com)
# Copyright (C) 2014-2019 GSECARS, University of Chicago, USA
# Copyright (C) 2015-2018 Institute for Geology and Mineralogy, University of Cologne, Germany
# Copyright (C) 2019-2020 DESY, Hamburg, Germany
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import functools

from qtpy import QtWidgets, QtCore, QtGui


class _ResetLevelsButtonMenu(QtWidgets.QMenu):
    """QMenu aligned to the right side of its parent and either on top or bottom
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._isOnTop = False

    def setOnTop(self, value):
        self._isOnTop = value

    def isOnTop(self):
        return self._isOnTop

    def event(self, event):
        if event.type() == QtCore.QEvent.Show:
            position = QtCore.QPoint(
                min(self.parent().width() - self.width(), 0),
                -self.height() if self.isOnTop() else self.parent().height(),
            )
            self.move(self.parent().mapToGlobal(position))
        return super().event(event)


class ResetLevelsButton(QtWidgets.QToolButton):
    """ToolButton with a menu to select auto-levels mode"""

    sigModeChanged = QtCore.Signal(str)
    """Emitted when auto-levels mode changed"""

    def __init__(self, *args):
        super().__init__(*args)
        self._currentMode = "default"
        self.setIcon(
            QtWidgets.QApplication.instance().style().standardIcon(
                QtWidgets.QStyle.SP_BrowserReload
            )
        )
        self.setIconSize(QtCore.QSize(15, 15))
        self.setToolTip("Autoscale colormap range")

        menu = _ResetLevelsButtonMenu(self)
        font = menu.font()
        font.setPointSize(10)
        menu.setFont(font)
        actionGroup = QtGui.QActionGroup(menu)

        action = QtGui.QAction("Default", actionGroup)
        action.setCheckable(True)
        action.toggled.connect(
            functools.partial(self._menuActionToggled, "default")
        )
        menu.addAction(action)
        action.trigger()

        action = QtGui.QAction("Min/max", actionGroup)
        action.setCheckable(True)
        action.toggled.connect(
            functools.partial(self._menuActionToggled, "minmax")
        )
        menu.addAction(action)

        action = QtGui.QAction("Mean±3std", actionGroup)
        action.setCheckable(True)
        action.toggled.connect(
            functools.partial(self._menuActionToggled, "mean3std")
        )
        menu.addAction(action)

        self.setMenu(menu)
        self.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)

    def _menuActionToggled(self, mode, checked):
        if checked:
            self._currentMode = mode
            self.sigModeChanged.emit(mode)

    def currentMode(self):
        """Returns the currently selected mode.

        One of: 'default', 'minmax', mean3std'
        """
        return self._currentMode

    def setMenuOnTop(self, value):
        self.menu().setOnTop(value)

    def isMenuOnTop(self):
        return self.menu().isOnTop()
