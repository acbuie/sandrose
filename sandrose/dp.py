"""
Functions related to calculating drift potential.

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
import numpy as np
import pandas as pd

from sandrose.common.constants import CARDINAL_DIRECTIONS
from sandrose.common.structures import NSummaryTable


def drift_potential(
    wind_speed_col: pd.Series,
    wind_dir_col: pd.Series,
    n_summary_table: NSummaryTable,
    *,
    v_thresh: float = 12.0,
    remove_negatives: bool = True,
) -> pd.DataFrame:
    """
    Calculate the drift potential from recorded wind velocities. Assumes
    recorded wind velocities at 10m height and units in knots. Uses the
    same bins as provided in the n_summary_table. By default, negative
    drift potential values are changed to 0.

    :param wind_speed_col: Recorded wind velocities column
    :type wind_speed_col: pd.Series
    :param wind_dir_col: Recorded wind cardinal directino column
    :type wind_dir_col: pd.Series
    :param n_summary_table:
        Table that contains T values, returned from :func:`n_summary`
    :type n_summary_table: NSummaryTable
    :param v_thresh:
        Impact threshold velocity to keep sand in saltation,
        defaults to 12.0 knots
    :type v_thresh: float, optional
    :param remove_negatives:
        Whether negative drift potential values are changed to 0,
        defaults to True
    :type remove_negatives: bool, optional
    :return: Not sure yet.
    :rtype: np.ndarray
    """
    idf = pd.DataFrame(
        {
            "Speed": wind_speed_col,
            "Direction": pd.Categorical(
                wind_dir_col, list(CARDINAL_DIRECTIONS.keys())
            ),
        }
    )

    t_vals = n_summary_table.t_table.iloc[:-2, :-1]
    bins = pd.IntervalIndex(t_vals.columns)

    speed_bins = pd.cut(idf["Speed"], bins)

    avg = idf["Speed"].groupby(speed_bins).mean().to_numpy()
    avg[np.isnan(avg)] = 0  # Convert any NaN to 0
    weighting_factor = avg ** 2 * (avg - v_thresh)

    dp_matrix = t_vals * weighting_factor

    # Replace negatives with 0
    if remove_negatives:
        dp_matrix[dp_matrix < 0] = 0

    df_mat = pd.DataFrame(
        dp_matrix / 100,
        index=list(CARDINAL_DIRECTIONS.keys()),
        columns=bins,
    )

    return df_mat


def n_summary(
    wind_col: pd.Series,
    direction_col: pd.Series,
    *,
    bins: list[float] = [
        0,
        4,
        7,
        11,
        17,
        22,
        28,
        34,
        41,
        48,
        55,
        float("inf"),
    ],
    precision: int = 1,
) -> NSummaryTable:
    """Calculate the N summary table from Fryberg 1979.

    Values in the table are the ratio of occurences in the bin to the
    total number of occurences.

    :param wind_col: Wind velocities column
    :type wind_col: pd.Series
    :param direction_col: Wind cardinal direction column
    :type direction_col: pd.Series
    :param bins:
        Wind speed bins, defaults to
        [0, 4, 7, 11, 17, 22, 28, 34, 41, 48, 55] in knots.
    :type bins: list[int], optional
    :param precision:
        Number of decimal places to round t values, defaults to 1
    :type precision: int
    :return:
        N Summary table from Fryberg 1979.
    :rtype: NSummaryTable
    """
    big_n = wind_col.count()
    calm_n = (wind_col == 0).sum()

    idf = pd.DataFrame(
        {
            "Speed (knts)": wind_col,
            "Dir": pd.Categorical(
                direction_col, list(CARDINAL_DIRECTIONS.keys())
            ),
        }
    )

    # Calc t_table
    groups = idf.groupby(["Dir", pd.cut(idf["Speed (knts)"], bins)])
    t_table = (groups.size() / big_n).unstack() * 100

    # Append Calm and Total rows
    num_cols = len(bins) - 1
    nans_list = [np.nan for _ in range(num_cols)]
    temp_zeroes = [0 for _ in range(num_cols)]

    append_df = pd.DataFrame(
        [nans_list, temp_zeroes],
        columns=t_table.columns,
        index=["Calm", "Total %"],
    )
    t_table = t_table.append(append_df)

    # Add percentage col
    t_table["Total %"] = 0

    # col_sums = t_table.sum(numeric_only=True, axis=0)
    t_table["Total %"] = t_table.iloc[:16].sum(numeric_only=True, axis=1)
    t_table["Total %"].loc["Calm"] = calm_n / big_n * 100
    t_table.loc["Total %"] = t_table.sum(numeric_only=True, axis=0)

    # Calc stats by bin
    stats = groups.agg(["count", "mean", "median", "std", "max"]).unstack()

    return NSummaryTable(big_n, t_table.round(precision), stats)


def rdp_rdd(dp_frame: pd.DataFrame) -> pd.DataFrame:
    """Calculate resultant drift potential and direction.

    See Yang, H.; Cao, J.; Hou, X. Characteristics of Aeolian Dune,
    Wind Regime and Sand Transport in Hobq Desert, China. Appl. Sci.
    2019, 9, 5543. https://doi.org/10.3390/app9245543

    :param dp_frame:
        Input dataframe, returned by :func:`drift_potential`
    :type dp_frame: pd.DataFrame
    :return:
        Dataframe of RDP, RDD, and RDP/DP. RDD units are degrees
        clockwise from North.
    :rtype: pd.DataFrame
    """
    car_dir = dp_frame.index.to_series().replace(CARDINAL_DIRECTIONS)
    dp_matrix = dp_frame.to_numpy()

    # -90 to make cos(0) = 1 at east, and sin(-90) = 1 at north
    theta = np.deg2rad(car_dir.to_numpy() - 90)
    r = dp_matrix.sum(axis=1)

    # Negate y to get in correct quadrant, negate both for +pi radians
    x = np.sum(r * np.cos(theta)) * -1
    y = np.sum(r * -np.sin(theta)) * -1

    rdp = (x * x + y * y) ** 0.5

    # Adjust angles to fit 0-360 from positive y axis (North)
    # Add 90 to move from N, *-1 for clockwise, +360/%360 for range
    rdd = np.rad2deg(np.arctan2(y, x)) * -1
    rdd = (rdd + 90 + 360) % 360

    dp = dp_matrix.sum()
    dp_ratio = rdp / dp

    df = pd.DataFrame({"RDP": [rdp], "RDD": [rdd], "RDP/DP": [dp_ratio]})

    return df
