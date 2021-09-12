from decimal import Decimal
from typing import Optional

import numpy as np
import pandas as pd

from sandrose.common.constants import CARDINAL_DIRECTIONS, MONTHS, SEASONS


def calc_drift_potential(
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


def sum_dp_monthly(
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


def sum_dp_yearly(
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


def sum_dp_seasonally(
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


def sum_dp_all(
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


def calc_time_percentage(
    rec_duration: pd.Timedelta,
    dates: pd.Series,
) -> float:
    """
    Calculate the value of t to be used by :func:`calc_drift_potential`

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


def calc_rdp_rdd(
    dp_frame: pd.DataFrame, dp: Optional[float] = None
) -> pd.DataFrame:
    """Calculate resultant drift potential and direction.

    :param dp_frame:
        Input dataframe, returned by one of the :func:`sum_dp_*`
        functions
    :type dp_frame: pd.DataFrame
    :param dp:
        Total summed drift potential. Value returned by :func:`sum_dp`.
        Defaults to None
    :type dp: float, optional
    :return: Dataframe of calculations for each time group
    :rtype: pd.DataFrame
    """

    def rdp_rdd(df: pd.DataFrame) -> pd.DataFrame:
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
            rdp_rdd
        )

        grouped.reset_index(level=1, drop=True, inplace=True)
        return grouped
    else:
        return rdp_rdd(dp_frame)
