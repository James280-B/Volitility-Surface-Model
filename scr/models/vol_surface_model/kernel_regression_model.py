import numpy as np
import pandas as pd
import logging
import statsmodels.regression.linear_model as lm
import statsmodels.api as sm

from math import pi, sqrt, exp

from scr.utils.csv_handler import CSVHandler
from scr.utils.errors import SkipError
from scr.utils.maths_utils import Maths


class OneDKernelRegressionModel:
    def __init__(
            self,
            input_data_df: pd.DataFrame,
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.df = input_data_df
        self._BW_CONST = 0.75  # values between [0.6, 1]
        # as stated in "Option-implied information: What’s the vol surface got to do with it?" (2020):

    def test(
            self,
            output_df: pd.DataFrame,
            test_df: pd.DataFrame,
            save: bool,
            test_tag: str
    ) -> dict:
        csv = CSVHandler()

        actual_ls = test_df["iv_call"].to_list() + test_df["iv_put"].to_list()
        actual_np = np.array(actual_ls)
        estimated_np = output_df["estimated_iv"].to_numpy()

        mh = Maths(actual=actual_np, predicted=estimated_np)

        test_output_dd = {
            "mae": mh.compute_mae(),
            "mse": mh.compute_mse(),
            "rmse": mh.compute_rmse(),
            "r2": mh.compute_r2(),
        }

        self.logger.info("computed test results")

        if save:
            df = pd.DataFrame(test_output_dd, index=[0])
            csv.save_test_output_summary(df=df, test_tag=test_tag)
        return test_output_dd

    def run(
            self,
            input_moneyness: float | list,
    ) -> pd.DataFrame:

        estimation_targets_ss = pd.Series(input_moneyness)

        implied_vol_output_df = pd.DataFrame(columns=["estimated_iv", "moneyness", "dte"])

        min_strike = min(self.df["strike"])
        max_strike = max(self.df["strike"])
        _n_obv_t = len(self.df) * 2  # data is inputted in put call pairs

        if _n_obv_t <= 1:
            raise SkipError("Skipping when num maturities <= 1")

        ave_dis_k = (max_strike - min_strike) / (_n_obv_t - 1)

        if ave_dis_k == 0:
            self.logger.warning("ave_dis_k is 0: only one strike in set")
            ave_dis_k = 0.2

        implied_iv_np = self.df["iv_put"].to_list() + self.df["iv_call"].to_list()
        moneyness_np = self.df["moneyness_call"].to_list() + self.df["moneyness_put"].to_list()

        extrapolated_data = self._compute_tail_extrapolation(delta_k=ave_dis_k, implied_iv_ls=implied_iv_np,
                                                             moneyness_ls=moneyness_np)

        input_data_dd = {
            "ave_dis_k": ave_dis_k,
            "total_iv_arr": extrapolated_data[0],
            "total_moneyness_arr": extrapolated_data[1],
        }

        implied_vol_output_df["estimated_iv"] = estimation_targets_ss.apply(self._compute_single_vol_point,
                                                                            input_data_dd=input_data_dd)

        implied_vol_output_df["moneyness"] = estimation_targets_ss
        # implied_vol_output_df["dte"] = round(self.df["dte_call"].values[0] / 365, 3)  #TODO FINISH THIS
        implied_vol_output_df["estimated_iv"] = round(implied_vol_output_df["estimated_iv"], 4)

        self.logger.info("completed model run")

        return implied_vol_output_df

    def _define_kernel_func(
            self,
            input_variable: float,
            ave_dis_k: float,
    ) -> float:
        bw = self._BW_CONST * ave_dis_k

        gaussian_const = 1 / sqrt(2 * pi)

        try:
            exp_comp = exp(-(input_variable ** 2) / (2 * bw))
        except ZeroDivisionError:
            self.logger.info("ZeroDivisionError")
            exp_comp = 1  # TODO FIND BETTER FIX
        output = gaussian_const * exp_comp
        return output

    def _compute_weights(
            self,
            estimation_target: float,
            input_data_dd: dict,
    ) -> list:
        kernel_sum = 0
        total_weights_ls = list()

        all_distance = estimation_target - input_data_dd["total_moneyness_arr"]
        for j in range(len(all_distance)):
            kernel_sum += self._define_kernel_func(input_variable=all_distance[j], ave_dis_k=input_data_dd["ave_dis_k"])

        for i in range(len(all_distance)):
            kernel = self._define_kernel_func(input_variable=all_distance[i], ave_dis_k=input_data_dd["ave_dis_k"])
            total_weights_ls.append(kernel / kernel_sum)
        return total_weights_ls

    def _compute_single_vol_point(
            self,
            estimation_target: float,
            input_data_dd: dict,
    ) -> float:

        weights_ls = self._compute_weights(
            estimation_target=estimation_target,
            input_data_dd=input_data_dd,
        )

        single_vol = np.dot(weights_ls, input_data_dd["total_iv_arr"])
        return single_vol

    def _compute_tail_extrapolation(
            self,
            moneyness_ls: list,
            implied_iv_ls: list,
            delta_k: float,
    ) -> tuple:
        min_moneyness = min(moneyness_ls)
        max_moneyness = max(moneyness_ls)

        left_tail_iv = implied_iv_ls[:4]
        left_tail_moneyness = implied_iv_ls[:4]
        left_tail_range_arr = np.arange(min_moneyness, 0.4, step=-delta_k)

        right_tail_iv = implied_iv_ls[-4:]
        right_tail_moneyness = implied_iv_ls[-4:]
        right_tail_range_arr = np.arange(max_moneyness, 1.6, step=delta_k)

        const_left_moneyness_ls = sm.add_constant(left_tail_moneyness, has_constant="add")
        const_right_tail_moneyness = sm.add_constant(right_tail_moneyness, has_constant="add")

        simple_regression_model_left = lm.OLS(left_tail_iv, const_left_moneyness_ls)
        simple_regression_model_right = lm.OLS(right_tail_iv, const_right_tail_moneyness)

        results_left = simple_regression_model_left.fit()
        results_right = simple_regression_model_right.fit()

        ols_iv_left_np = results_left.params[0] + results_left.params[1] * left_tail_range_arr
        ols_iv_right_np = results_right.params[0] + results_right.params[1] * right_tail_range_arr

        total_moneyness_np = np.array(list(left_tail_range_arr) + moneyness_ls + list(right_tail_range_arr))
        total_iv_np = np.array(list(ols_iv_left_np) + implied_iv_ls + list(ols_iv_right_np))

        self.logger.info("finished estimating implied vol")
        return total_iv_np, total_moneyness_np
