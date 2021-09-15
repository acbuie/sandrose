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

import numpy as np
import pandas as pd

from sandrose.common.constants import CARDINAL_DIRECTIONS, MONTHS, SEASONS


def sum_monthly(
    dates: pd.Series, dp_values: pd.Series, direction: pd.Series
) -> pd.DataFrame:
    """
    Sum per-record drift potential values by month. Binned in 16
    cardinal compass directions.

    :param dates: Dataframe column of date records
    :type dates: pd.Series
    :param dp_values: Calculated drift potential values
    :type dp_values: pd.Series
    :param direction: Cardinal wind direction of the record
    :type direction: pd.Series
    :return:
        Long-form dataframe of monthly summed drift potentials. Binned
        and sorted in monthly ascending order (Jan - Dec) and clockwise
        cardinal direction order, starting at North (N - NNW)
    :rtype: pd.DataFrame
    """

    # months: pd.Series = dates.dt.month.replace(MONTHS)

    data = pd.DataFrame(
        {
            "Month": pd.Categorical(
                dates.dt.month.replace(MONTHS), list(MONTHS.values())
            ),
            "Drift_Potential": dp_values,
            "Cardinal_Direction": pd.Categorical(
                direction, list(CARDINAL_DIRECTIONS.keys())
            ),
        }
    )

    unsorted = (
        data.groupby(["Month", "Cardinal_Direction"]).sum().reset_index()
    )

    sorted_df = unsorted.sort_values(by=["Month", "Cardinal_Direction"])

    return sorted_df


def sum_yearly(
    dates: pd.Series, dp_values: pd.Series, direction: pd.Series
) -> pd.DataFrame:
    """
    Sum per-record drift potential values by year. Binned in 16 cardinal
    compass directions.

    :param dates: Dataframe column of date records
    :type dates: pd.Series
    :param dp_values: Calculated drift potential values
    :type dp_values: pd.Series
    :param direction: Cardinal wind direction of the record
    :type direction: pd.Series
    :return:
        Long-form dataframe of monthly summed drift potentials. Binned
        and sorted in yearly ascending order and clockwise cardinal
        direction order, starting at North (N - NNW)
    :rtype: pd.DataFrame
    """

    data = pd.DataFrame(
        {
            "Year": dates,
            "Drift_Potential": dp_values,
            "Cardinal_Direction": pd.Categorical(
                direction, list(CARDINAL_DIRECTIONS.keys())
            ),
        }
    )

    unsorted = (
        data.groupby([data["Year"].dt.year, "Cardinal_Direction"])
        .sum()
        .reset_index()
    )
    sorted_df = unsorted.sort_values(by=["Year", "Cardinal_Direction"])

    return sorted_df


def sum_seasonally(
    dates: pd.Series, dp_values: pd.Series, direction: pd.Series
) -> pd.DataFrame:
    """Sum per-record drift potential values by season
    (DJF, MAM, JJA, SON). Binned in 16 cardinal compass directions.

    :param dates: Dataframe column of date records
    :type dates: pd.Series
    :param dp_values: Calculated drift potential values
    :type dp_values: pd.Series
    :param direction: Cardinal wind direction of the record
    :type direction: pd.Series
    :return:
        Long-form dataframe of seasonally summed drift potentials.
        Binned and sorted from Winter - Fall and clockwise cardinal
        direction order, starting at North (N - NNW)
    :rtype: pd.DataFrame
    """

    data = pd.DataFrame(
        {
            "Season": pd.Categorical(
                (dates.dt.month % 12 // 3 + 1).replace(SEASONS),
                list(SEASONS.values()),
            ),
            "Drift_Potential": dp_values,
            "Cardinal_Direction": pd.Categorical(
                direction, list(CARDINAL_DIRECTIONS.keys())
            ),
        }
    )

    unsorted = (
        data.groupby(["Season", "Cardinal_Direction"]).sum().reset_index()
    )
    sorted_df = unsorted.sort_values(by=["Season", "Cardinal_Direction"])

    return sorted_df


def sum_all(
    dates: pd.Series, dp_values: pd.Series, direction: pd.Series
) -> pd.DataFrame:
    """Sum all per-record drift potential values.

    :param dates: Dataframe column of date records
    :type dates: pd.Series
    :param dp_values: Calculated drift potential values
    :type dp_values: pd.Series
    :param direction: Cardinal wind direction of the record
    :type direction: pd.Series
    :return:
        Long-form dataframe of summed drift potentials. Binned and
        sorted in clockwise cardinal direction order, starting at
        North (N - NNW)
    :rtype: pd.DataFrame
    """

    data = pd.DataFrame(
        {
            "Date": dates,
            "Drift_Potential": dp_values,
            "Cardinal_Direction": pd.Categorical(
                direction, list(CARDINAL_DIRECTIONS.keys())
            ),
        }
    )

    unsorted = data.groupby("Cardinal_Direction").sum().reset_index()
    sorted_df = unsorted.sort_values(by="Cardinal_Direction")

    return sorted_df


def sum_dp(dp_values: pd.Series) -> float:
    """Sum all drift potential records. No binning by compass direction.

    :param dp_values: Dataframe column of drift potential values.
    :type dp_values: pd.Series
    :return: Summed drift potential off all wind records. Not binned.
    :rtype: float
    """
    return np.sum(dp_values.to_numpy())
