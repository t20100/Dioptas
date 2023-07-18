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

from typing import Optional
import numpy as np


def _default_auto_level(data: np.ndarray) -> tuple[float, float]:
    """Compute colormap range from data through histogram

    :param data:
    :returns: (min, max)
    """
    counts, bin_edges = np.histogram(data, bins=3000)
    left_edges = bin_edges[:-1]
    left_edges = left_edges[np.where(counts>0)]
    counts = counts[np.where(counts>0)]

    hist_y_cumsum = np.cumsum(counts)
    hist_y_sum = np.sum(counts)

    max_ind = np.where(hist_y_cumsum < (0.996 * hist_y_sum))
    min_level = np.mean(left_edges[:2])

    if len(max_ind[0]):
        max_level = left_edges[max_ind[0][-1]]
    else:
        max_level = 0.5 * np.max(left_edges)

    if len(left_edges[left_edges > 0]) > 0:
        min_level = max(min_level, np.nanmin(left_edges[left_edges > 0]))
    return min_level, max_level


def _minmax_auto_level(data: np.ndarray) -> tuple[float, float]:
    """Returns min/max of the data

    :returns: (min, max)
    """
    return float(np.min(data)), float(np.max(data))


def _mean3std_auto_level(data: np.ndarray) -> tuple[float, float]:
    """Returns mean+/-3std clipped to min/max of the data

    :returns: (lower limit, upper limit)
    """
    mean = np.mean(data, dtype=np.float64)
    std = np.std(data, dtype=np.float64)
    minimum, maximum = _minmax_auto_level(data)
    return max(mean - 3 * std, minimum), min(mean + 3 * std, maximum)


def auto_level(data: Optional[np.ndarray], mode: str = 'default') -> Optional[tuple[float, float]]:
    """Compute colormap range from data

    :param data: Data from which to compute colormap range
    :param mode: Mode of autoscale computation: "default", "minmax", "mean3std"
    :returns: (min, max) or None
    :raise ValueError: If the mode is not supported
    """
    if data is None:
        return None

    filtered_data = data[np.isfinite(data)]
    if filtered_data.size == 0:
        return None

    if mode == 'default':
        return _default_auto_level(filtered_data)
    if mode == 'minmax':
        return _minmax_auto_level(filtered_data)
    if mode == 'mean3std':
        return _mean3std_auto_level(filtered_data)
    raise ValueError(f'Unsupported mode: {mode}')
