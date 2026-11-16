from scr.utils.csv_handler import CSVHandler
from scr.vol_surface_model.kernel_regression_model import OneDKernelRegressionModel

csv = CSVHandler()
csv.create_input_data_set(set_type="input")

options_data_df = csv.read_input_model_data()
summary_dd = csv.produce_data_summary(options_data_df)
print(summary_dd)

grouped_dte_data_dd = {
    dte: group
    for dte, group in options_data_df.groupby(options_data_df["expiry_call"])
}

kernel_regression_model = OneDKernelRegressionModel(total_data_sets_dd=grouped_dte_data_dd, estimation_step_freq=0.01)
kernel_regression_model.run()

print("model run completed")
