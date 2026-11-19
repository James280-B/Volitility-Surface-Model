import pandas as pd
import os

from lse import LSE

from scr.utils.env_utils import read_environment_variables


class CSVHandler:
    def __init__(self) -> None:
        self._LSE_API_KEY = read_environment_variables("LSE_API_KEY")
        self.INPUT_MODEL_DATA_PATH = read_environment_variables("INPUT_MODEL_DATA_PATH")
        self.OUTPUT_MODEL_PATH = read_environment_variables("OUTPUT_MODEL_PATH")
        self.RAW_LSE_DATA_PATH = read_environment_variables("RAW_LSE_DATA_PATH")
        self._OIS_CURVE_DATA_PATH = read_environment_variables("OIS_CURVE_DATA_PATH")

        self._OUTPUT_FILE_NAME = "okr_iv_output"
        self._INPUT_DATA_FILE_NAME = "input_data"
        self._OIS_CURVE_DATA_FILE_NAME = "ois_curve_data"

    def request_lse_raw_options_flow_to_csv(
            self,
            request_params_dd: dict,
            start_date: str,
            end_date: str,
    ) -> pd.DataFrame:
        client = LSE(self._LSE_API_KEY)
        option_flow_data = client.options_flow(underlying=request_params_dd["underlying"],
                                               type=request_params_dd["type"],
                                               min_premium=request_params_dd["min_premium"],
                                               max_dte=request_params_dd["max_dte"],
                                               start=start_date,
                                               end=end_date,
                                               limit=request_params_dd["limit"],
                                               min_dte=request_params_dd["min_dte"])

        option_flow_data_df = pd.DataFrame(option_flow_data)

        return option_flow_data_df

    def read_input_model_data(self) -> pd.DataFrame:
        file_name = f"{self._INPUT_DATA_FILE_NAME}.csv"
        folder_path = os.path.join(self.INPUT_MODEL_DATA_PATH, file_name)
        df = pd.read_csv(folder_path)

        return df

    def read_model_output_data(self) -> pd.DataFrame:
        file_name = f"{self._OUTPUT_FILE_NAME}.csv"
        folder_path = os.path.join(self.OUTPUT_MODEL_PATH, file_name)
        df = pd.read_csv(folder_path)

        return df

    def read_ois_data_json(self) -> pd.DataFrame:
        file_name = f"{self._OIS_CURVE_DATA_FILE_NAME}.json"
        folder_path = os.path.join(self._OIS_CURVE_DATA_PATH, file_name)
        df = pd.read_json(folder_path)
        curve_ls = df["curve"].tolist()
        output_df = pd.DataFrame(curve_ls)
        return output_df

    def save_model_output(
            self,
            output_df: pd.DataFrame,
    ) -> None:
        file_name = f"{self._OUTPUT_FILE_NAME}.csv"
        folder_path = os.path.join(self.OUTPUT_MODEL_PATH, file_name)
        output_df.to_csv(folder_path, index=False)

    def save_input_data(
            self,
            df: pd.DataFrame,
    ) -> None:
        file_name = f"{self._INPUT_DATA_FILE_NAME}.csv"
        folder_path = os.path.join(self.INPUT_MODEL_DATA_PATH, file_name)
        df.to_csv(folder_path, index=False)

    def save_data_summary(
            self,
            input_df: pd.DataFrame,
    ) -> None:
        total_maturities = input_df["dte_call"].nunique()
        total_strikes = input_df["strike"].nunique()

        data_summary_dd = {
            "num_option_pairs": input_df.shape[0],
            "num_obvs": input_df.shape[0] * 2,
            "num_strikes": total_strikes,
            "num_maturities": total_maturities,
        }

        df = pd.DataFrame(data_summary_dd, index=[0])
        folder_path = os.path.join(self.INPUT_MODEL_DATA_PATH, "data_summary.csv")

        df.to_csv(folder_path, index=False)
