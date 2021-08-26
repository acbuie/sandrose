# **Sandrose**

**Sandrose** is a Python library to aid in the analysis of aeolian sand transport using wind data. It simplifies the calculation of Resulant Drift Potential and Direction, and provides access to simple polar bar plots for visualization.

## **Example Plots**

TODO
Plots go here...

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

---

## **Usage**

Sandrose supplies several useful functions for drift potential calculations. The main `calc_drift_potential` function uses `numpy` arrays internally, so usage with `pandas` dataframes is simple.

## **More Examples**

### Simplified Drift Potential Calculation

```python
import datetime # For calculating t

import pandas as pd
import sandrose

data = pd.read_csv('path/to/file/data.csv')
wind_data = data["WIND_COL_NAME"]

wind_duration = datetime.timedelta(minutes=10)
total_duration = datetime.timedelta(days=1000)

t = sandrose.calc_time_percentage(wind_duration, total_duration)

dp_array = sandrose.calc_drift_potential(wind_data, t)
```

### Calculating _t_ From Datetime Stamps

If your data contains time stamps for each wind record, a simple way to calculate the `total_duration` variable is to use `pd.to_datetime`.

```python
# See below for more formats
d_format = "%d/%m/%Y"

# This will overwrite the original column, and may not be behavior
# you desire. You can always make a copy with DataFrame.copy()
data["DATE_COL"] = pd.to_datetime(
    data["DATE_COL"], format=d_format
    )

# We can now do datetime math.
# Total range = Newest record - Oldest record, or
# Last record - First record, if sorted.
total_duration = data["DATE_COL"].iloc[-1] - data["DATE_COL"][0]
```

See [here](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior) for more datetime formats.
