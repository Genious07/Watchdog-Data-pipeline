from src.validator import ingest_data, detect_change, validate_data


def test_ingest_data():
    raw = b'[[1690000000000, "1", "2", "0.5", "1.5", "100", 0, 0, 0, 0, 0, 0]]'
    df = ingest_data(raw)
    assert len(df) == 1
    assert df["open"][0] == 1.0


def test_detect_change():
    assert detect_change("new_hash")  # Since no DB, assumes change


def test_validate_data(mocker):
    # Simulate the raw data format that ingest_data expects
    raw_data = (
        b'[[1672531200000, "1.0", "2.0", "0.5", "1.5", "100.0", 0, 0, 0, 0, '
        b'0, 0], [1672534800000, "1.1", "2.1", "0.6", "1.6", "101.0", 0, 0, '
        b'0, 0, 0, 0]]'
    )
    df = ingest_data(raw_data)
    # Convert timestamp to int64 (nanoseconds since epoch) for GE
    df["timestamp"] = df["timestamp"].astype("int64")
    results = validate_data(df)
    assert "success" in results
