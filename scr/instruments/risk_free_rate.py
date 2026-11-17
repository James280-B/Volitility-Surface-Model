import numpy as np

from scr.utils.csv_handler import CSVHandler


class RiskFreeRate:
    def __init__(
            self,
    ) -> None:
        pass

    @staticmethod
    def compute(tmt_yrs: float) -> float:
        csv = CSVHandler()
        curve_data_df = csv.read_ois_data_json()

        tenor_yrs = curve_data_df["days"] / 365
        par_rates = curve_data_df["rate"]

        print(tenor_yrs)
        print(par_rates)

        rf = np.interp(tmt_yrs, tenor_yrs, par_rates)

        return rf
