from dataclasses import dataclass

import pandas as pd


@dataclass
class NSummaryTable:
    total_records: int
    t_table: pd.DataFrame
    stats: pd.DataFrame
