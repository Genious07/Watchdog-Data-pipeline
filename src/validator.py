import json
import pandas as pd
import great_expectations as gx
from src.db import get_last_hash


def ingest_data(raw_data):
    data = json.loads(raw_data)
    # The new API provides a list of lists with format: [timestamp, open, high, low, close]
    # We will adapt this to the expected DataFrame structure.
    df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close"])

    # Convert timestamp and data types as before
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df[["open", "high", "low", "close"]] = df[
        ["open", "high", "low", "close"]
    ].astype(float)

    # Add a placeholder 'volume' column since it's required for validation,
    # but not provided by this specific CoinGecko endpoint.
    df["volume"] = 0.0

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
