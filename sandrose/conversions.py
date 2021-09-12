from math import log

import numpy as np
import pandas as pd
from common import CARDINAL_DIRECTIONS


def wind_log_law(
    v_rec_col: pd.Series,
    z_rec: float,
    z_ref: float = 10.0,
    z_0: float = 0.1,
) -> np.ndarray:
    """
    Adjust wind velocities from the recorded height, z_rec, to a
    reference height, z_ref, according to the logarithmic law
    (Arya, 1988, Jacobson, 1999)

    :param v_rec:
        Recorded wind velocities column from Dataframe.
    :type v_rec: pd.Series
    :param z_rec: Recorded wind height
    :type z_rec: float
    :param z_ref: Reference wind height, defaults to 10.0 m
    :type z_ref: float
    :param z_0:
        Roughness length, defaults to 0.1, (Archer and Jacobson, 2003)
    :type z_0: float, optional
    :return: Height adjusted wind velocities
    :rtype: np.ndarray
    """
    v_rec_array = v_rec_col.to_numpy()
    numerator = v_rec_array * log(z_ref / z_0)
    denomenator = log(z_rec / z_0)
    return numerator / denomenator


def wind_power_law(
    v_rec_col: pd.Series,
    z_rec: float,
    z_ref: float = 10.0,
    alpha: float = (1.0 / 7.0),
) -> np.ndarray:
    """
    Adjust wind velocities from the recorded height, z_rec, to a
    reference height, z_ref, according to the power law
    (Arya, 1988, Jacobson, 1999)

    :param v_rec:
        Recorded wind velocities column of Dataframe.
    :type v_rec: pd.Series
    :param z_rec: Recorded wind height
    :type z_rec: float
    :param z_ref: Reference wind height, defaults to 10.0 m
    :type z_ref: float
    :param alpha:
        Friction coefficient, defaults to 1/7,
        (Archer and Jacobson, 2003)
    :type z_0: float, optional
    :return: Height adjusted wind velocities
    :rtype: np.ndarray
    """
    v_rec_array = v_rec_col.to_numpy()
    base = z_ref / z_rec
    return v_rec_array * (base ** alpha)


def degree_to_cardinal(values: pd.Series) -> np.ndarray:
    """Convert direction in degrees to cardinal direction strings.

    :param values: Dataframe column of direction values in degrees
    :type values: pd.Series
    :return: Array of cardinal directions
    :rtype: np.ndarray
    """

    temp = list(CARDINAL_DIRECTIONS.keys())
    temp.append("N")

    CARD_DIR = np.array(temp)

    vals_array = values.to_numpy()
    angle = np.remainder(vals_array, 360.0)
    index = np.around((angle / 22.5)).astype(np.int16, copy=False)
    return CARD_DIR[index]
