from scr.models.lse_data_builder.data_builder import LSEDataBuilder
from scr.utils.data_utils.csv_handler import CSVHandler

csv = CSVHandler()
builder = LSEDataBuilder()

builder.build_input_data("test")

test_df = csv.read_test_data_csv("test.csv")

