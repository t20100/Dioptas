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
"""Test ColormapPopup widget"""

import numpy as np
import pytest
from qtpy import QtCore, QtWidgets
from qtpy.QtTest import QSignalSpy, QTest

import pyqtgraph.graphicsItems.GradientEditorItem

from ...widgets.plot_widgets.ColormapPopup import ColormapPopup


def testRange(qWidgetFactory):
    """Test getRange, setRange and sigRangeChanged"""
    colormapPopup = qWidgetFactory(ColormapPopup)
    assert colormapPopup.getRange() == (1, 1)

    signalSpy = QSignalSpy(colormapPopup.sigRangeChanged)

    colormapPopup.setRange(100, 1000)
    assert len(signalSpy) == 1
    assert signalSpy[0] == [100, 1000]
    assert colormapPopup.getRange() == (100, 1000)

    colormapPopup.setRange(2000, 1000)
    assert len(signalSpy) == 2
    assert signalSpy[1] == [1000, 2000]
    assert colormapPopup.getRange() == (1000, 2000)


def testCurrentGradient(qWidgetFactory):
    """Test getCurrentGradient, setCurrentGradient and sigCurrentGradientChanged"""
    colormapPopup = qWidgetFactory(ColormapPopup)
    for firstName, firstGradient in pyqtgraph.graphicsItems.GradientEditorItem.Gradients.items():
        break
    gradient = colormapPopup.getCurrentGradient()
    assert gradient == firstGradient
    assert colormapPopup._gradientComboBox.currentText() == firstName.capitalize()
 
    signalSpy = QSignalSpy(colormapPopup.sigCurrentGradientChanged)
    viridisGradient = pyqtgraph.graphicsItems.GradientEditorItem.Gradients['viridis']
    colormapPopup.setCurrentGradient(viridisGradient)
    gradient = colormapPopup.getCurrentGradient()
    assert gradient == viridisGradient
    assert colormapPopup._gradientComboBox.currentText() == 'Viridis'
    assert len(signalSpy) == 1
    assert signalSpy[0] == [viridisGradient]


def testCustomGradient(qWidgetFactory):
    """Test setCurrentGradient with a custom gradient"""
    colormapPopup = qWidgetFactory(ColormapPopup)
    signalSpy = QSignalSpy(colormapPopup.sigCurrentGradientChanged)

    customGradient = {
        'mode': 'rgb',
        'ticks': [(0.0, (0, 0, 0, 255)), (1.0, (0, 0, 0, 255))],
    }
    colormapPopup.setCurrentGradient(customGradient)
    gradient = colormapPopup.getCurrentGradient()
    assert gradient == customGradient
    assert colormapPopup._gradientComboBox.currentText() == 'Custom'
    assert len(signalSpy) == 1
    assert signalSpy[0] == [customGradient]

    customGradient2 = {
        'mode': 'rgb',
        'ticks': [(0.0, (255, 255, 255, 255)), (1.0, (255, 255, 255, 255))],
    }
    colormapPopup.setCurrentGradient(customGradient2)
    gradient = colormapPopup.getCurrentGradient()
    assert gradient == customGradient2
    assert colormapPopup._gradientComboBox.currentText() == 'Custom'
    assert len(signalSpy) == 2
    assert signalSpy[1] == [customGradient2]


@pytest.mark.parametrize("normalization", ["log", "sqrt"])
def testCurrentNormalization(qWidgetFactory, normalization):
    """Test getCurrentNormalization, setCurrentNormalization and sigCurrentNormalizationChanged"""
    colormapPopup = qWidgetFactory(ColormapPopup)

    default_normalization = colormapPopup.getCurrentNormalization()
    assert default_normalization == "linear"
    assert colormapPopup._normalizationComboBox.currentText() == "Linear"
    assert colormapPopup._normalizationComboBox.currentData() == "linear"

    signalSpy = QSignalSpy(colormapPopup.sigCurrentNormalizationChanged)
    colormapPopup.setCurrentNormalization(normalization)
    returned_normalization = colormapPopup.getCurrentNormalization()
    assert returned_normalization == normalization
    assert colormapPopup._normalizationComboBox.currentData() == normalization
    assert len(signalSpy) == 1
    assert signalSpy[0] == [normalization]


def testResetMode(qWidgetFactory):
    """Test reset range and changing reset mode"""
    colormapPopup = qWidgetFactory(ColormapPopup)
    colormapPopup.setData(np.arange(101))

    buttons = colormapPopup._resetButtonGroup.buttons()
    defaultButton, minmaxButton, mean3stdButton, percentileButton = buttons

    assert colormapPopup._resetButtonGroup.checkedButton() == defaultButton
    mode = colormapPopup._getResetMode()
    assert mode == "default"

    QTest.mouseClick(colormapPopup._autoscaleButton, QtCore.Qt.LeftButton)
    range_ = colormapPopup.getRange()
    assert range_ == (1, 99)

    QTest.mouseClick(minmaxButton, QtCore.Qt.LeftButton)
    mode = colormapPopup._getResetMode()
    range_ = colormapPopup.getRange()
    assert mode == "minmax"
    assert range_ == (0, 100)

    QTest.mouseClick(percentileButton, QtCore.Qt.LeftButton)
    mode = colormapPopup._getResetMode()
    range_ = colormapPopup.getRange()
    assert mode == "1percentile"
    assert range_ == (1, 99)

    QTest.mouseClick(mean3stdButton, QtCore.Qt.LeftButton)
    mode = colormapPopup._getResetMode()
    range_ = colormapPopup.getRange()
    assert mode == "mean3std"
    assert range_ == (0, 100)

    QTest.mouseClick(defaultButton, QtCore.Qt.LeftButton)
    mode = colormapPopup._getResetMode()
    range_ = colormapPopup.getRange()
    assert mode == "default"
    assert range_ == (1, 99)
