from src.validator import ingest_data, detect_change, validate_data

def test_ingest_data():
    # Corrected test data: now a list of dictionaries to match the real API response
    raw = b'''
    {
        "Data": {
            "Data": [
                {
                    "time": 1690000000, "open": 1.0, "high": 2.0, "low": 0.5,
                    "close": 1.5, "volumefrom": 100.0
                }
            ]
        }
    }
    '''
    df = ingest_data(raw)
    assert len(df) == 1
    assert df["open"][0] == 1.0

def test_detect_change():
    assert detect_change("new_hash")  # Since no DB, assumes change

def test_validate_data(mocker):
    # Corrected test data for the second test
    raw_data = b'''
    {
        "Data": {
            "Data": [
                {
                    "time": 1672531200, "open": 1.0, "high": 2.0, "low": 0.5,
                    "close": 1.5, "volumefrom": 100.0
                },
                {
                    "time": 1672534800, "open": 1.1, "high": 2.1, "low": 0.6,
                    "close": 1.6, "volumefrom": 101.0
                }
            ]
        }
    }
    '''
    df = ingest_data(raw_data)
    # Convert timestamp to int64 (nanoseconds since epoch) for GE
    df["timestamp"] = df["timestamp"].astype("int64")
    results = validate_data(df)
    assert "success" in results
