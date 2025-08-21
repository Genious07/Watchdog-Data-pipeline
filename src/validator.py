import json
import pandas as pd
import great_expectations as gx
from src.db import get_last_hash


def ingest_data(raw_data):
    """
    Parses the JSON response from the CryptoCompare API into a pandas DataFrame.
    """
    data = json.loads(raw_data)

    # The data is nested under ['Data']['Data']
    ohlcv_data = data['Data']['Data']
    df = pd.DataFrame(ohlcv_data)

    # The 'time' column is a Unix timestamp, so we convert it to datetime.
    df['timestamp'] = pd.to_datetime(df['time'], unit='s')

    # The 'volumefrom' column corresponds to the base asset volume.
    df.rename(columns={'volumefrom': 'volume'}, inplace=True)

    # Ensure all numeric columns have the correct float data type.
    df[["open", "high", "low", "close", "volume"]] = df[
        ["open", "high", "low", "close", "volume"]
    ].astype(float)

    return df

def detect_change(content_hash):
    last_hash = get_last_hash()
    return last_hash != content_hash


def validate_data(df):
    # Work on a copy and add a numeric timestamp for monotonicity checks
    df_copy = df.copy()
    df_copy["ts_ns"] = df_copy["timestamp"].astype("int64")

    gx_df = gx.from_pandas(df_copy)

    # Basic presence checks
    for col in ["timestamp", "open", "high", "low", "close", "volume"]:
        gx_df.expect_column_values_to_not_be_null(column=col)

    # Type checks for numeric columns
    for col in ["open", "high", "low", "close", "volume"]:
        gx_df.expect_column_values_to_be_of_type(column=col, type_="float")

    # Monotonicity on integer timestamp (avoid datetime parsing issues)
    gx_df.expect_column_values_to_be_increasing(
        column="ts_ns", strictly=True
    )

    # Sanity checks: values strictly > 0
    for col in ["open", "high", "low", "close", "volume"]:
        gx_df.expect_column_values_to_be_between(
            column=col, min_value=0.000001, max_value=None
        )

    results = gx_df.validate()
    return results.to_json_dict()
