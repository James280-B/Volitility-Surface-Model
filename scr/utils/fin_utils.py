import pandas as pd

from math import exp, log
from typing import cast
from scr.utils.pairs_data_row import PairsDataRow


class FinUtils:

    def __init__(
            self,
            tmt_yrs: float,
            rf_rate: float | None,
    ) -> None:
        self.rf = rf_rate
        self.time_to_maturity_yrs = tmt_yrs

    def is_arbitrage_compliant_single(self, row: PairsDataRow, div_yield: float) -> bool:
        arbitrage_compliant = False

        if row.price_call >= (
                row.underlying_price_call * exp(-div_yield * self.time_to_maturity_yrs) - (
                row.strike * exp(-self.rf * self.time_to_maturity_yrs))):
            arbitrage_compliant = True

        if row.price_put >= (row.strike * exp(-self.rf * self.time_to_maturity_yrs) - (
                row.underlying_price_put * exp(-div_yield * self.time_to_maturity_yrs))):
            arbitrage_compliant = True

        return arbitrage_compliant

    def _compute_continuous_div_single(self, row: PairsDataRow) -> float:
        mid_underlying = (row.underlying_price_call + row.underlying_price_put) / 2

        continuous_div_single = 1 / self.time_to_maturity_yrs * (
                log(mid_underlying) - log(
            row.price_call - row.price_put + (
                    exp(-self.rf * self.time_to_maturity_yrs) * row.strike)))

        return continuous_div_single

    def compute_daily_continuous_div(self, df: pd.DataFrame) -> float:
        con_div = 0
        total_rows = len(df)

        for row in df.itertuples(index=False):
            con_div += self._compute_continuous_div_single(row=cast(PairsDataRow, row))
            con_div = con_div / total_rows

        return con_div

    def compute_moneyness(self, df: pd.DataFrame) -> pd.DataFrame:
        forward_price_call_ss = df["underlying_price_call"] * exp(self.time_to_maturity_yrs * self.rf)
        forward_price_put_ss = df["underlying_price_put"] * exp(self.time_to_maturity_yrs * self.rf)

        moneyness_call_ss = df["strike"] / forward_price_call_ss
        moneyness_put_ss = df["strike"] / forward_price_put_ss

        d = {
            "moneyness_call": moneyness_call_ss,
            "moneyness_put": moneyness_put_ss,
        }

        moneyness_df = pd.DataFrame.from_dict(d)

        return moneyness_df
