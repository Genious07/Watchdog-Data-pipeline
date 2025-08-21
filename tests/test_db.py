from src.db import store_results, get_last_hash


def test_store_and_get(mocker):
    mock_coll = mocker.Mock()
    mock_coll.insert_one.return_value = None
    mock_coll.find_one.return_value = {"content_hash": "test_hash"}
    mocker.patch("src.db.collection", mock_coll)
    store_results(
        {"timestamp": "now", "success": True, "content_hash": "test_hash"},
        {}
    )
    assert get_last_hash() == "test_hash"
