import numpy as np
import pandas as pd

from math import pi, sqrt, exp

from scr.utils.csv_handler import CSVHandler
from scr.utils.errors import SkipError


class OneDKernelRegressionModel:
    def __init__(
            self,
            total_data_sets_dd: dict,
            estimation_step_freq: float,
    ) -> None:
        self.total_data_sets_dd = total_data_sets_dd
        self.estimation_step_freq = estimation_step_freq
        self._num_days = len(total_data_sets_dd)
        self._BW_CONST = 0.75  # values between [0.6, 1]
        # as stated in "Option-implied information: What’s the vol surface got to do with it?" (2020):

    def run(self):
        total_output_df = pd.DataFrame(columns=["estimated_iv", "moneyness", "dte"])
        csv = CSVHandler()

        for df in self.total_data_sets_dd.values():
            print(f"length of input df is {len(df)}")
            implied_vol_output_df = pd.DataFrame(columns=["estimated_iv", "moneyness", "dte"])

            #min_moneyness = round(min(df["moneyness_call"].tolist() + df["moneyness_put"].tolist()), 3)
            #max_moneyness = round(max(df["moneyness_call"].tolist() + df["moneyness_put"].tolist()), 3)

            estimation_targets = np.arange(0.8, 1.2, self.estimation_step_freq)
            estimation_targets_ss = pd.Series(estimation_targets)

            try:
                implied_vol_output_df["estimated_iv"] = estimation_targets_ss.apply(self._compute_single_vol_point,
                                                                                    input_data_df=df)
            except SkipError:
                continue

            implied_vol_output_df["moneyness"] = estimation_targets_ss
            implied_vol_output_df["dte"] = round(df["dte_call"].values[0] / 365, 3)

            total_output_df = pd.concat([total_output_df, implied_vol_output_df], axis=0)

        csv.save_model_output(output_df=total_output_df)

    def _define_kernel_func(
            self,
            input_variable: float,
            input_data_df: pd.DataFrame,
    ) -> float:
        min_strike = min(input_data_df["strike"])
        max_strike = max(input_data_df["strike"])
        _n_obv_t = len(input_data_df)  # data is inputted in put call pairs

        if _n_obv_t <= 1:
            raise SkipError("Skipping maturities <= 1")

        ave_dis_k = (max_strike - min_strike) / (_n_obv_t - 1)
        bw = self._BW_CONST * ave_dis_k

        gaussian_const = 1 / sqrt(2 * pi)

        try:
            exp_comp = exp(-(input_variable ** 2) / (2 * bw))
        except ZeroDivisionError:
            exp_comp = 1  # TODO FIND BETTER FIX
        output = gaussian_const * exp_comp
        return output

    @staticmethod
    def _compute_distances(
            estimation_target: float,
            input_data_df: pd.DataFrame,
    ) -> tuple:
        all_distances_call = estimation_target - input_data_df["moneyness_call"]
        all_distances_put = estimation_target - input_data_df["moneyness_put"]

        all_distances = all_distances_call.to_list() + all_distances_put.to_list()
        return all_distances

    def _compute_weights(
            self,
            estimation_target: float,
            input_data_df: pd.DataFrame,
    ) -> list:
        kernel_sum = 0
        total_weights_ls = list()

        all_distance = self._compute_distances(
            estimation_target=estimation_target,
            input_data_df=input_data_df,
        )
        for j in range(len(all_distance)):
            kernel_sum += self._define_kernel_func(input_variable=all_distance[j], input_data_df=input_data_df)

        for i in range(len(all_distance)):
            kernel = self._define_kernel_func(input_variable=all_distance[i], input_data_df=input_data_df)
            total_weights_ls.append(kernel / kernel_sum)
        return total_weights_ls

    def _compute_single_vol_point(
            self,
            estimation_target: float,
            input_data_df: pd.DataFrame,
    ) -> float:
        iv_call = input_data_df["iv_call"].to_list()
        iv_put = input_data_df["iv_put"].to_list()

        total_iv_ls = iv_call + iv_put
        weights_ls = self._compute_weights(
            input_data_df=input_data_df,
            estimation_target=estimation_target,
        )
        single_vol = np.dot(weights_ls, total_iv_ls)

        return single_vol
