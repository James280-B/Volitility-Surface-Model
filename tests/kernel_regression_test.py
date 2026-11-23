from scr.utils.csv_handler import CSVHandler
from scr.models.vol_surface_model.kernel_regression_model import OneDKernelRegressionModel
from scr.utils.logging_config import setup_logger
from scr.models.lse_data_builder.data_builder import LSEDataBuilder

#builder = LSEDataBuilder()
#builder.build_input_data("test")

csv = CSVHandler()
setup_logger()

test_df = csv.read_test_data_csv("test.csv")
input_df = csv.read_input_model_data()

test_tag = "test_1"

model = OneDKernelRegressionModel(input_data_df=input_df)
test_moneyness = test_df["moneyness_call"].to_list() + test_df["moneyness_put"].to_list()

output_df = model.run(input_moneyness=test_moneyness)
csv.save_model_output(output_df)

test_dd = model.test(test_df=test_df, output_df=output_df, save=True, test_tag=test_tag)
