from datetime import datetime, timedelta, timezone


def get_lse_request_params(set_type: str) -> dict:
    output_dd = dict

    test_dd = {
        "num_requests": 1,
        "underlying": "AAPL",
        "type": None,
        "min_premium": 250000,
        "max_dte": None,
        "start": 14,
        "end": 13,
        "limit": 1000,
        "min_dte": None,
    }

    input_dd = {
        "num_requests": 1,
        "underlying": "AAPL",
        "type": None,
        "min_premium": 1000,
        "max_dte": None,
        "start": 14,
        "end": 13,
        "limit": 5000,  # the max limit for single request
        "min_dte": None,
    }

    large_dd = {
        "num_requests": 3,
        "underlying": "AAPL",
        "type": None,
        "min_premium": 1000,
        "max_dte": None,
        "start": 14,
        "end": 13,
        "limit": 5000,  # the max limit for single request
        "min_dte": None,
    }

    if set_type == "test":
        output_dd = test_dd
    elif set_type == "input":
        output_dd = input_dd
    elif set_type == "large":
        output_dd = large_dd

    return output_dd


def is_in_filtered_cols(col_name: str) -> bool:
    output = False

    ls = [
        "Unnamed: 0_call",
        "pair_id_call",
        "Unnamed: 0_put",
        "pair_id_put",
        "underlying_call",
        "underlying_put",
        "day_put",
        "day_call",
        "contract_type_call",
        "contract_type_put",
    ]

    if col_name in ls:
        output = True

    return output


def compute_utc_dates(num_days: int) -> str:
    date = (datetime.now(timezone.utc) - timedelta(days=num_days)).strftime("%Y-%m-%d")
    print(date)
    return date
