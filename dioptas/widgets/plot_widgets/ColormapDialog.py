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
from __future__ import annotations

import pathlib

from qtpy import QtGui, QtCore, QtWidgets
import pyqtgraph.graphicsItems.GradientEditorItem

from . import utils
from ... import style_path


class ColormapDialog(QtWidgets.QDialog):
    """Dialog providing control over the currently used colormap"""

    sigCurrentGradientChanged = QtCore.Signal(dict)
    """Signal emitted when the colormap gradient has changed"""

    sigCurrentNormalizationChanged = QtCore.Signal(str)
    """Signal emitted when the colormap normalization has changed"""

    sigRangeChanged = QtCore.Signal(float, float)
    """Signal emitted when the data range has changed"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._histogram = None
        self.setWindowTitle("Colormap configuration")
        self.setStyleSheet(
            pathlib.Path(style_path, "stylesheet.qss").read_text()
        )

        layout = QtWidgets.QFormLayout(self)

        self._gradientComboBox = QtWidgets.QComboBox(self)
        for name, gradient in pyqtgraph.graphicsItems.GradientEditorItem.Gradients.items():
            icon = self._createQIconFromGradient(gradient)
            self._gradientComboBox.addItem(icon, name.capitalize(), gradient)
        self._gradientComboBox.currentIndexChanged.connect(self._gradientComboBoxCurrentIndexChanged)
        layout.addRow('Colormap:', self._gradientComboBox)

        self._normalizationComboBox = QtWidgets.QComboBox(self)
        self._normalizationComboBox.addItem("Linear", "linear")
        self._normalizationComboBox.addItem("Logarithmic", "log")
        self._normalizationComboBox.addItem("Square root", "sqrt")
        self._normalizationComboBox.addItem("Arcsinh", "arcsinh")

        self._normalizationComboBox.setCurrentIndex(0)
        self._normalizationComboBox.currentIndexChanged.connect(self._normalizationComboBoxCurrentIndexChanged)
        layout.addRow('Normalization:', self._normalizationComboBox)

        layout.addRow('Range:', QtWidgets.QLabel())
        self._minEdit = QtWidgets.QLineEdit(self)
        self._minEdit.setValidator(QtGui.QDoubleValidator(1, float('inf'), -1))
        self._minEdit.editingFinished.connect(self._rangeChanged)
        layout.addRow('Min:', self._minEdit)

        self._maxEdit = QtWidgets.QLineEdit(self)
        self._maxEdit.setValidator(QtGui.QDoubleValidator(1, float('inf'), -1))
        self._maxEdit.editingFinished.connect(self._rangeChanged)
        layout.addRow('Max:', self._maxEdit)

        reloadIcon = QtWidgets.QApplication.instance().style().standardIcon(
            QtWidgets.QStyle.SP_BrowserReload
        )
        self._autoscaleButton = QtWidgets.QPushButton(reloadIcon, "Reset", self)
        self._autoscaleButton.setToolTip("Scale colormap range with current mode")
        self._autoscaleButton.clicked.connect(self._autoscaleRequested)
        self._autoscaleButton.setAutoDefault(False)
        self._autoscaleButton.setEnabled(False)
        layout.addRow('', self._autoscaleButton)

        self._autoscaleModeComboBox = QtWidgets.QComboBox(self)
        self._autoscaleModeComboBox.addItem("Default", "default")
        self._autoscaleModeComboBox.setItemData(
            0, "Use default colormap range autoscale", QtCore.Qt.ToolTipRole)
        self._autoscaleModeComboBox.addItem("Min/Max", "minmax")
        self._autoscaleModeComboBox.setItemData(
            1, "Use data min/max to scale colormap range", QtCore.Qt.ToolTipRole)
        self._autoscaleModeComboBox.addItem("Mean±3 Std", "mean3std")
        self._autoscaleModeComboBox.setItemData(
            2, "Use data mean ± 3 × standard deviation to scale colormap range", QtCore.Qt.ToolTipRole)
        self._autoscaleModeComboBox.setCurrentIndex(0)
        self._autoscaleModeComboBox.currentIndexChanged.connect(self._autoscaleRequested)
        layout.addRow('Reset mode:', self._autoscaleModeComboBox)

        buttonBox = QtWidgets.QDialogButtonBox(parent=self)
        buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        closeButton = buttonBox.button(QtWidgets.QDialogButtonBox.Close)
        closeButton.clicked.connect(self.accept)
        closeButton.setAutoDefault(False)
        layout.addRow(buttonBox)

    def setDataHistogram(self, counts: Optional[np.ndarray], bins: Optional[np.ndarray]):
        """Set histogram of data to use for autoscale"""
        self._histogram = None if counts is None or bins is None else (counts, bins)
        self._autoscaleButton.setEnabled(self._histogram is not None)

    def getDataHistogram(self) -> Optional[tuple[np.ndarray, np.ndarray]]:
        """Returns histogram of data if set as (counts, bins) else None"""
        return self._histogram

    def _gradientComboBoxCurrentIndexChanged(self, index: int):
        if index < 0:
            return
        gradient = self._gradientComboBox.itemData(index, QtCore.Qt.UserRole)
        self.sigCurrentGradientChanged.emit(gradient)

    def _normalizationComboBoxCurrentIndexChanged(self, index: int):
        if index < 0:
            return
        normalization = self._normalizationComboBox.itemData(index, QtCore.Qt.UserRole)
        self.sigCurrentNormalizationChanged.emit(normalization)

    def setCurrentGradient(self, gradient: dict):
        """Set the currently selected gradient

        If the gradient is not available, a 'Custom' item is added for it.
        """
        for name, description in pyqtgraph.graphicsItems.GradientEditorItem.Gradients.items():
            if gradient['mode'] == description['mode'] and gradient['ticks'] == description['ticks']:
                self._gradientComboBox.setCurrentText(name.capitalize())
                return

        icon = self._createQIconFromGradient(gradient)
        # Block signals to avoid emitting with previously selected gradient since index changes
        wasBlocked = self._gradientComboBox.blockSignals(True)
        self._gradientComboBox.insertItem(0, icon, 'Custom', gradient)
        self._gradientComboBox.blockSignals(wasBlocked)
        self._gradientComboBox.setCurrentIndex(0)

    def getCurrentGradient(self) -> dict:
        """Returns the currently selected gradient"""
        return self._gradientComboBox.currentData()

    def setCurrentNormalization(self, normalization: str):
        """Set the currently selected normalization"""
        index = self._normalizationComboBox.findData(normalization)
        if index < 0:
            raise ValueError(f"Unsupported normalization: {normalization}")
        self._normalizationComboBox.setCurrentIndex(index)

    def getCurrentNormalization(self) -> str:
        """Returns the currently selected normalization"""
        return self._normalizationComboBox.currentData()

    def _rangeChanged(self):
        minimum, maximum = self.getRange()
        if maximum < minimum:
            self.setRange(maximum, minimum)
            return
        self.sigRangeChanged.emit(minimum, maximum)

    def setRange(self, minimum: float, maximum: float):
        """Set the data range (min, max) of the colormap"""
        if maximum < minimum:
            minimum, maximum = maximum, minimum
        if (minimum, maximum) == self.getRange():
            return
        self._minEdit.setText(self._minEdit.validator().locale().toString(float(minimum)))
        self._maxEdit.setText(self._maxEdit.validator().locale().toString(float(maximum)))
        self._rangeChanged()

    def getRange(self) -> tuple[float, float]:
        """Returns the data range of the colormap (min, max)"""
        minimum, validated = self._minEdit.validator().locale().toDouble(self._minEdit.text())
        if not validated:
            minimum = 1 
        maximum, validated = self._maxEdit.validator().locale().toDouble(self._maxEdit.text())
        if not validated:
            maximum = minimum
        return minimum, maximum

    def _autoscaleRequested(self, *args):
        histogram = self.getDataHistogram()
        if histogram is None:
            return
        counts, bins = histogram
        mode = self._autoscaleModeComboBox.currentData()
        minimum, maximum = utils.auto_level(bins, counts, mode)
        self.setRange(minimum, maximum)

    @staticmethod
    def _createQIconFromGradient(gradient: dict) -> QtGui.QIcon:
        """Generates a QIcon from a pyqtgraph gradient"""
        gradientEditorItem = pyqtgraph.graphicsItems.GradientEditorItem.GradientEditorItem()
        gradientEditorItem.setLength(100)
        gradientEditorItem.restoreState(gradient)
        qgradient = gradientEditorItem.getGradient()

        pixmap = QtGui.QPixmap(100, 100)
        painter = QtGui.QPainter(pixmap)
        brush = QtGui.QBrush(qgradient)
        painter.fillRect(QtCore.QRect(0, 0, 100, 100), brush)
        painter.end()
        return QtGui.QIcon(pixmap)
