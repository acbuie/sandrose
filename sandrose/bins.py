"""
Functions for temporal binning.

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

import pandas as pd

from sandrose.common.constants import MONTHS, SEASONS


def month_bin(data: pd.DataFrame, time_column: str) -> pd.DataFrame:
    """Bin dataframe monthly.

    Adds a 'BIN' column, which specifies 'Month: *', where * is the
    month the record falls into.

    :param data: Input dataset.
    :type data: pd.DataFrame
    :param time_column:
        Dataframe column name to bin by. Must be datetimes.
    :type time_column: str
    :return: Dataset with added 'BIN' column.
    :rtype: pd.DataFrame
    """
    month: pd.Series = data[time_column].dt.month.replace(MONTHS)
    prefix = "Monthly: "

    category = [prefix + m for m in MONTHS.values()]
    bins = [prefix + m for m in month.astype(str)]

    data["BIN"] = pd.Categorical(bins, category)
    return data


def season_bin(data: pd.DataFrame, time_column: str) -> pd.DataFrame:
    """Bin dataframe by meterological season.

    Adds a 'BIN' column, which specifies 'Season: *', where * is the
    season the record falls into.

    :param data: Input dataset.
    :type data: pd.DataFrame
    :param time_column:
        Dataframe column name to bin by. Must be datetimes.
    :type time_column: str
    :return: Dataset with added 'BIN' column.
    :rtype: pd.DataFrame
    """
    season: pd.Series = (data[time_column].dt.month % 12 // 3 + 1).replace(
        SEASONS
    )
    prefix = "Seasonally: "

    category = [prefix + s for s in SEASONS.values()]
    bins = [prefix + s for s in season.astype(str)]

    data["BIN"] = pd.Categorical(bins, category)
    return data


def year_bin(data: pd.DataFrame, time_column: str) -> pd.DataFrame:
    """Bin dataframe yearly.

    Adds a 'BIN' column, which specifies 'Year: *', where * is the
    year of the record.

    :param data: Input dataset.
    :type data: pd.DataFrame
    :param time_column:
        Dataframe column name to bin by. Must be datetimes.
    :type time_column: str
    :return: Dataset with added 'BIN' column.
    :rtype: pd.DataFrame
    """
    year: pd.Series = data[time_column].dt.year
    prefix = "Yearly: "

    category = [prefix + str(y) for y in year.unique()]
    bins = [prefix + y for y in year.astype(str)]

    data["BIN"] = pd.Categorical(bins, category)
    return data
