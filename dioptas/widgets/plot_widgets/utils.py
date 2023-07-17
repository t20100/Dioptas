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

import numpy as np


def weighted_average_std(a: np.ndarray, weights: np.ndarray) -> tuple[float, float]:
    """Returns the weighted average and weighted standard deviation"""
    mean, sum_of_weights = np.average(a, weights=weights, returned=True)
    variance = np.sum(weights * (a - mean)  ** 2) / sum_of_weights
    return mean, np.sqrt(variance)


def _default_auto_level(hist_x: np.ndarray, hist_y: np.ndarray) -> tuple[float, float]:
    """Compute colormap range from histogram of the data

    :param hist_x: Bin left edges
    :param hist_y: Histogram count
    :returns: (min, max)
    """
    hist_y_cumsum = np.cumsum(hist_y)
    hist_y_sum = np.sum(hist_y)

    max_ind = np.where(hist_y_cumsum < (0.996 * hist_y_sum))
    min_level = np.mean(hist_x[:2])

    if len(max_ind[0]):
        max_level = hist_x[max_ind[0][-1]]
    else:
        max_level = 0.5 * np.max(hist_x)

    if len(hist_x[hist_x > 0]) > 0:
        min_level = max(min_level, np.nanmin(hist_x[hist_x > 0]))
    return min_level, max_level


def _minmax_auto_level(hist_x: np.ndarray, hist_y: np.ndarray) -> tuple[float, float]:
    """Returns min/max of the data

    :param hist_x: Bin left edges
    :param hist_y: Histogram count
    :returns: (min, max)
    """
    bin_size = hist_x[-1] - hist_x[-2]
    return hist_x[0], hist_x[-1] + bin_size


def _mean3std_auto_level(hist_x: np.ndarray, hist_y: np.ndarray) -> tuple[float, float]:
    """Returns mean+/-3std clipped to min/max of the data

    :param hist_x: Bin left edges
    :param hist_y: Histogram count
    :returns: (lower limit, upper limit)
    """
    mean, std = weighted_average_std(hist_x, hist_y)
    minimum, maximum = _minmax_auto_level(hist_x, hist_y)
    return max(mean - 3 * std, minimum), min(mean + 3 * std, maximum)


def auto_level(hist_x: np.ndarray, hist_y: np.ndarray, mode: str = 'default') -> tuple[float, float]:
    """Compute colormap range from histogram of the data

    :param hist_x: Bin left edges
    :param hist_y: Histogram count
    :param mode: Mode of autoscale computation: "default", "minmax", "mean3std"
    :returns: (min, max)
    :raise ValueError: If the mode is not supported
    """
    if mode == 'default':
        return _default_auto_level(hist_x, hist_y)
    if mode == 'minmax':
        return _minmax_auto_level(hist_x, hist_y)
    if mode == 'mean3std':
        return _mean3std_auto_level(hist_x, hist_y)
    raise ValueError(f'Unsupported mode: {mode}')
