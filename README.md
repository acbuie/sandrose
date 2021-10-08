![License](https://img.shields.io/github/license/acbuie/sandrose) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) ![Commit](https://img.shields.io/github/last-commit/acbuie/sandrose)

<!-- ![Package version](https://img.shields.io/pypi/v/sandrose)
![Python version](https://img.shields.io/pypi/pyversions/sandrose) -->

# **Sandrose**

**Sandrose** is a Python library to aid in the analysis of aeolian sand transport using wind data. It simplifies the calculation of Resulant Drift Potential and Direction, and provides access to simple polar bar plots for quick visualization.

---

## **Installation**

Sandrose is available on PyPI: (eventually)

Via `pip`:

```console
$ pip install sandrose
```

Via `poetry`:

```console
$ poetry add sandrose
```

<!-- ...with Conda: (eventually)
```console
$ conda install sandrose
``` -->

Or, install from GitHub (requires [git](https://git-scm.com/)):

```console
$ pip install "git+https://github.com/acbuie/sandrose.git#egg=sandrose"
$ poetry add git+https://github.com/acbuie/sandrose.git#egg=sandrose
```

As always, it's recommended to install within a python virtual environment.

---

## **Usage**

Sandrose supplies several useful functions for drift potential calculations. These are in the `sandrose.dp.calc` and `sandrose.dp.dp_sum` modules.

##### Drift Potential Calculation

Functions for calculating per-record drift potential and the resultant drift potential and direction can be found in the `sandrose.dp.calc` module. See Fryberg and Dean, 1979 for more.

- `drift_potential()`: Calculate the per-record drift potential.
- `time_perc()`: Calculate _t_ used in drift potential calculations. It is the time the wind blew expressed as a ratio of the total time of all measurements.
- `rdp_rdd()`: Calculate the resultant drift potential and resultant drift direction.

##### Drift Potential Summation

There are currently _5_ different methods to sum per-record drift potentials, and can be found in the `sandrose.dp.dp_sum` module.

- `sum_monthly()`: Sum all drift potential values, while binning montly and directionally (into 16 compass directions).
- `sum_seasonally()`: Sum _dp_ values, binning seasonally (meteorological) and directionally.
- `sum_yearly()`: Sum _dp_ values, binning yearly and directionally.
- `sum_all()`: Sum _dp_ values without time binning, but with directional binning.
- `sum_dp()`: Sum _dp_ values without time binning or directional binning. Useful for finding RDP/DP ratio.

---

## **Examples**

### Basic Script

```python
import pandas as pd
from sandrose import dp

# data has datetime col "date", wind col "vals", and direction col "str_dir"

t = dp.calc.time_perc(pd.Timedelta(10, unit="m"), data["date"])
data["dp"] = dp.calc.drift_potential(data["vals"], t)

all_dp = dp.dp_sum.sum_dp(data["dp"])

# Bin dp only via compass direction
grouped = dp.dp_sum.sum_all(
    data["date"],
    data["dp"],
    data["str_dir"],
)

dp_all = dp.calc.rdp_rdd(grouped, all_dp)
print(dp_all)
```

_fancy image output_

### Conversions

```python
from sandrose import conversions
```

#### Wind Conversions

These functions are supplied as a means to normalize wind data recorded at varying elevations.

```python
wind_data = pd.Series([5.0, 8.0, 10.0, 6.0, 9.0])

# Adjust records from 10.0m velocities to 80.0m velocities
conversions.wind_log_law(wind_data, z_rec=10.0, z_ref=80.0)
conversions.wind_power_law(wind_data, z_rec=10.0, z_ref=80.0)
```

_fancy image output_

#### Angular Converions

The default (and currently only supported) binning method places each drift potential calculation into one of the 16 carindal compass directions. Should your data only supply numerical degree direction, `conversions.degree_to_cardinal` will convert the data into the required format.

```python
# Supports angles over 360°, as well as 0° or 360° for North
angles = pd.Series([360, 100, 90, 220, 0, 300, 400])

conversions.degree_to_cardinal(angles)
```

_fancy image output_

### Calculating _t_ From Datetimes

`sandrose.dp.calc_time_percentage()` calculates the total time range of all records by constructing a `pd.Timedelta` object from the most recent record and the oldest record. This assumes the dataframe column passed contains `np.datetime64` (or other valid datetime) data types.

Some useful pandas functions related to datetimes:

- `pd.to_datetime()`: Converts a pandas Series into `np.datetime64` datatype. Read more [here](https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html). See [here](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior) for datetime formating options.

- `DataFrame.sort_values()`: Not unique to datetimes, but can be used to sort the data via datetime. Read more [here](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html).

### Quick Polar Bar Plot

Coming soon!

---

## License

This work is licensed under the [GNU GPLv3 license](https://github.com/acbuie/sandrose/blob/main/LICENSE.txt).

---

## Contributing

See [here](https://github.com/acbuie/sandrose/blob/main/CONTRIBUTING.md).
