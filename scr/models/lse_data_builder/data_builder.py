import numpy as np
import pandas as pd
import datetime as dt
import logging

from typing import cast

from scr.utils.csv_handler import CSVHandler
from scr.parameters.data_params import get_lse_request_params, compute_utc_dates, is_in_filtered_cols
from scr.utils.fin_utils import FinUtils
from scr.utils.errors import SkipError
from scr.instruments.risk_free_rate import RiskFreeRate
from scr.utils.pairs_data_row import PairsDataRow


class LSEDataBuilder:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
    def build_input_data(
            self,
            set_type: str,
    ) -> None:
        csv = CSVHandler()

        input_data_df = pd.DataFrame()
        lse_params_dd = get_lse_request_params(set_type)

        start_date = compute_utc_dates(lse_params_dd["start"])
        end_date = compute_utc_dates(lse_params_dd["end"])

        for i in range(lse_params_dd["num_requests"]):
            raw_data_df = csv.request_lse_raw_options_flow_to_csv(
                request_params_dd=lse_params_dd,
                start_date=start_date,
                end_date=end_date,
            )
            if raw_data_df.empty:
                self.logger.warning("No data found for requested date")
                continue
            self.logger.info("Request LSE data from {} to {}".format(start_date, end_date))

            cleaned_unfiltered_df = self._clean_raw_options_flow_data(raw_data_df=raw_data_df)
            filtered_df = self._filter_non_arb_options(cleaned_data_df=cleaned_unfiltered_df)

            input_data_df_single_request = self._clean_filtered_data(filtered_data_df=filtered_df)
            input_data_df = pd.concat([input_data_df, input_data_df_single_request])

            start_date = compute_utc_dates(lse_params_dd["start"] + 1)
            end_date = compute_utc_dates(lse_params_dd["end"] + 1)

        csv.save_input_data(input_data_df)
        self.logger.info("Input data successfully created")

    @staticmethod
    def _clean_raw_options_flow_data(raw_data_df: pd.DataFrame) -> pd.DataFrame:
        dropped_cols_df = raw_data_df.drop(columns=["premium", "size", "symbol", "venue"])  # drop uncessary cols
        dropped_cols_df = dropped_cols_df.replace('', np.nan, inplace=True)
        dropped_cols_df = dropped_cols_df.dropna()
        dropped_cols_df["expiry"] = pd.to_datetime(dropped_cols_df["expiry"], format="%Y-%m-%d")
        dropped_cols_df["ts"] = pd.to_datetime(dropped_cols_df["ts"],
                                               format="%Y-%m-%dT%H:%M:%S.%fZ")  # TODO MIGHT BE REDUNDENT
        ordered_data_df = dropped_cols_df.sort_values(by=["expiry", "strike"])

        return ordered_data_df

    def _find_daily_put_call_pairs(self, daily_data_df: pd.DataFrame) -> pd.DataFrame:
        calls_df = daily_data_df[daily_data_df["contract_type"] == "call"]
        puts_df = daily_data_df[daily_data_df["contract_type"] == "put"]

        if len(calls_df) == 1 and len(puts_df) == 1:
            output_df = pd.merge(calls_df, puts_df, how="inner", on=["strike"], suffixes=["_call", "_put"])

        elif len(calls_df) == 0 or len(puts_df) == 0:
            raise SkipError("no put or no calls on current expiry on current date")

        else:
            all_pairs_df = pd.merge(calls_df, puts_df, how="inner", on=["strike"], suffixes=["_call", "_put"])
            output_df = self._filter_pairs_on_constraints(all_pairs_df)
        output_df.reset_index(drop=True, inplace=True)
        return output_df

    @staticmethod
    def _compute_time_diff(df: pd.DataFrame) -> pd.Series:
        time_diff_ss = abs(df["ts_call"] - df["ts_put"])
        if time_diff_ss.empty:
            raise SkipError("time diff empty")

        return time_diff_ss

    def _filter_pairs_on_constraints(self, df: pd.DataFrame) -> pd.DataFrame:
        df["underlying_diff"] = self._compute_underlying_diff(df)
        df["time_diff"] = self._compute_time_diff(df)
        underlying_diff_threshold = 0.01
        time_diff_threshold = dt.timedelta(minutes=1)

        output_df = df[(df["underlying_diff"] <= underlying_diff_threshold) & (df["time_diff"] <= time_diff_threshold)]

        output_df.drop(columns=["underlying_diff", "time_diff"], inplace=True)
        return output_df

    @staticmethod
    def _compute_underlying_diff(df: pd.DataFrame) -> pd.Series:
        underlying_diff_ss = abs(
            (df["underlying_price_call"] - df["underlying_price_put"]) / df["underlying_price_call"])

        return underlying_diff_ss

    @staticmethod
    def _clean_filtered_data(
            filtered_data_df: pd.DataFrame,
    ) -> pd.DataFrame:
        for col in filtered_data_df.columns:
            if is_in_filtered_cols(col_name=col):
                filtered_data_df = filtered_data_df.drop(columns=[col])  # drop uncessary cols

        return filtered_data_df

    def _filter_non_arb_options(self, cleaned_data_df: pd.DataFrame) -> pd.DataFrame:
        filtered_data_df = pd.DataFrame()

        grouped_daily_data_dd = {
            date: group
            for date, group in cleaned_data_df.groupby(
                [cleaned_data_df["ts"].dt.date, cleaned_data_df["expiry"]])
        }
        for daily_data_df in grouped_daily_data_dd.values():
            dropped_rows = list()
            idx = -1  # TODO FIND BETTER METHOD THAN THIS

            tmt_yrs = daily_data_df["dte"].values[0] / 365
            rf = RiskFreeRate.compute(tmt_yrs=tmt_yrs)

            try:
                daily_put_call_pairs_df = self._find_daily_put_call_pairs(daily_data_df)
            except SkipError as sk:
                self.logger.info("Exception occurred: %s", str(sk))
                continue

            fin_maths_utils = FinUtils(tmt_yrs=tmt_yrs, rf_rate=rf)
            moneyness_df = fin_maths_utils.compute_moneyness(df=daily_put_call_pairs_df)
            daily_put_call_pairs_df = daily_put_call_pairs_df.join(moneyness_df)
            daily_div_yield = fin_maths_utils.compute_daily_continuous_div(df=daily_put_call_pairs_df)

            for row in daily_put_call_pairs_df.itertuples(index=True):
                idx += 1
                if not fin_maths_utils.is_arbitrage_compliant_single(row=cast(PairsDataRow, row),
                                                                     div_yield=daily_div_yield):  # TODO MAKE MORE EFFICIENT
                    dropped_rows.append(idx)

            daily_put_call_pairs_df.drop(index=dropped_rows, inplace=True)
            filtered_data_df = pd.concat([filtered_data_df, daily_put_call_pairs_df])

        return filtered_data_df
