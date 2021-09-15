"""
Sandrose
Copyright (C) 2021  Aidan Buie

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from decimal import Decimal
from typing import Optional

import numpy as np
import pandas as pd

from sandrose.common.constants import CARDINAL_DIRECTIONS


def drift_potential(
    v_rec_col: pd.Series,
    t: float,
    v_thresh: float = 6.0,
    remove_negatives: bool = True,
) -> np.ndarray:
    """
    Calculate the drift potential from recorded wind velocities. Assumes
    recorded wind velocities at 10m height and units in meters. By
    default, negative drift potential values are changed to 0.

    :param v_rec:
        Recorded wind velocities column of Dataframe
    :type v_rec: pd.Series
    :param t:
        Time wind blew, expressed as a percentage on N summary. See
        Fryberg and Dean, 1979 for more
    :type t: float
    :param v_thresh:
        Impact threshold velocity to keep sand in saltation,
        defaults to 6.0 m/s
    :type v_thresh: float, optional
    :param remove_negatives:
        Whether negative drift potential values are changed to 0,
        defaults to True
    :type remove_negatives: bool, optional
    :return: Per record drift potential, in vector units
    :rtype: np.ndarray
    """
    v_rec_array = v_rec_col.to_numpy()
    weighting_factor = v_rec_array ** 2 * (v_rec_array - v_thresh)
    dp = weighting_factor * t

    # Replace negatives with 0
    if remove_negatives:
        dp[dp < 0] = 0

    return dp


def time_perc(
    rec_duration: pd.Timedelta,
    dates: pd.Series,
) -> float:
    """
    Calculate the value of t to be used by :func:`drift_potential`

    Uses :class:`decimal.Decimal` for accurate division, as the total
    time in seconds of the data can be quite large.

    :param rec_duration:
        The duration of each wind record, or the amount of time the
        wind blew
    :type rec_duration: pd.Timedelta
    :param total_range:
        Dataframe column of dates. Will calculate the total range of
        time records were recorded in
    :type total_range: pd.Series
    :return:
        The time wind blew, expressed as a ratio over the total time
    :rtype: float
    """
    # Not sure if Decimal is needed
    total_range: pd.Timedelta = dates.iloc[-1] - dates.iloc[0]
    total_range_s = Decimal(total_range.total_seconds())
    rec_duration_s = Decimal(rec_duration.total_seconds())

    decimal_result = rec_duration_s / total_range_s

    return float(decimal_result)


def rdp_rdd(
    dp_frame: pd.DataFrame, dp: Optional[float] = None
) -> pd.DataFrame:
    """Calculate resultant drift potential and direction.

    :param dp_frame:
        Input dataframe, returned by one of the :func:`sum_*`
        functions
    :type dp_frame: pd.DataFrame
    :param dp:
        Total summed drift potential. Value returned by :func:`sum_dp`.
        Used for calculating the RDP/DP ratio. Defaults to None
    :type dp: float, optional
    :return:
        Dataframe of calculations for each time group. RDD units are
        degrees. If dp is not supplied, then only RDP and RDD are
        returned in the Dataframe.
    :rtype: pd.DataFrame
    """

    def i_rdp_rdd(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate resultant drift potential and resultant drift
        direction

        See Yang, H.; Cao, J.; Hou, X. Characteristics of Aeolian Dune,
        Wind Regime and Sand Transport in Hobq Desert, China. Appl. Sci.
        2019, 9, 5543. https://doi.org/10.3390/app9245543
        """
        df["Cardinal_Direction"].replace(CARDINAL_DIRECTIONS, inplace=True)

        theta = np.deg2rad(df["Cardinal_Direction"].to_numpy())
        r = df["Drift_Potential"].to_numpy()

        x = np.sum(r * np.cos(theta))
        y = np.sum(r * np.sin(theta))

        rdp = (x * x + y * y) ** 0.5
        rdd = np.rad2deg(np.arctan((y / x)))

        if not dp:
            return pd.DataFrame({"RDP": [rdp], "RDD": [rdd]})
        else:
            return pd.DataFrame(
                {"RDP": [rdp], "RDD": [rdd], "RDP/DP": [rdp / dp]}
            )

    # Only df.apply() if 3 columns, i.e. sum_dp_*
    if dp_frame.shape[1] == 3:
        grouped: pd.DataFrame = dp_frame.groupby(dp_frame.iloc[:, 0]).apply(
            i_rdp_rdd
        )

        grouped.reset_index(level=1, drop=True, inplace=True)
        return grouped
    else:
        return i_rdp_rdd(dp_frame)
